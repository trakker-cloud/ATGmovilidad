#!/usr/bin/env python3
# Etiqueta: APP_CHANGO_CIRCUIT_BREAKER_02102026
# Proyecto: app chango
# Arquitectura: Fail-Safe Circuit Breaker & Graceful Degradation Engine

import time
from typing import Callable, Any, Dict

class CircuitBreakerOpenException(Exception):
    """Excepción lanzada cuando el cortacircuitos está abierto y desvía al fallback."""
    pass

class CircuitBreaker:
    """
    Implementación del patrón Circuit Breaker para protección de servicios críticos
    (Redis, Kafka, PostGIS) ante caídas de red o latencia extrema en calle.
    """
    def __init__(self, failure_threshold: int = 3, recovery_timeout_sec: float = 5.0):
        self.failure_threshold = failure_threshold
        self.recovery_timeout_sec = recovery_timeout_sec
        
        self.state = "CLOSED"  # Estados: CLOSED, OPEN, HALF_OPEN
        self.failure_count = 0
        self.last_failure_time = 0.0

    def call(self, primary_func: Callable[..., Any], fallback_func: Callable[..., Any], *args, **kwargs) -> Any:
        """
        Ejecuta la función primaria. Si el circuito está abierto o la función falla 
        superando el umbral, activa la degradación grácil ejecutando la función de fallback.
        """
        current_time = time.time()

        # 1. Evaluar transición de OPEN a HALF_OPEN si pasó el tiempo de recuperación
        if self.state == "OPEN":
            if current_time - self.last_failure_time > self.recovery_timeout_sec:
                self.state = "HALF_OPEN"
                print(f"[CIRCUIT BREAKER] Estado cambiado a HALF-OPEN. Probando reconexión...")
            else:
                print(f"[CIRCUIT BREAKER] Estado OPEN. Activando Degradación Grácil (Fallback local)...")
                return fallback_func(*args, **kwargs)

        # 2. Intentar ejecución de la función primaria (Infraestructura)
        try:
            result = primary_func(*args, **kwargs)
            
            # Si estábamos en HALF_OPEN y tuvo éxito, cerramos el circuito
            if self.state == "HALF_OPEN":
                self.state = "CLOSED"
                self.failure_count = 0
                print(f"[CIRCUIT BREAKER] ¡Reconexión exitosa! Circuito restaurado a CLOSED.")
                
            return result

        except Exception as e:
            self.failure_count += 1
            self.last_failure_time = current_time
            print(f"[CIRCUIT BREAKER ERROR] Fallo en servicio primario ({self.failure_count}/{self.failure_threshold}): {e}")

            # 3. Si se supera el umbral de fallos, abrimos el circuito
            if self.failure_count >= self.failure_threshold or self.state == "HALF_OPEN":
                self.state = "OPEN"
                print(f"[CIRCUIT BREAKER] Umbral superado. Circuito ABIERTO (OPEN). Derivando a Fallback.")

            return fallback_func(*args, **kwargs)

if __name__ == "__main__":
    print("--- [APP CHANGO] Verificando Patrón Circuit Breaker y Degradación Grácil ---")
    
    cb = CircuitBreaker(failure_threshold=2, recovery_timeout_sec=2.0)
    
    # Simulación de servicios
    def mock_kafka_publish_fail():
        raise ConnectionError("Kafka broker no disponible (Zona de sombra / Corte de red)")

    def local_sqlite_fallback(*args, **kwargs):
        return {"status": "FALLBACK_SUCCESS", "message": "Operación guardada en buffer SQLite local para sincronización posterior."}

    # Prueba 1 y 2: Provocar fallos consecutivos para abrir el circuito
    print("\n[PRUEBA 1] Intento fallido 1:")
    print(cb.call(mock_kafka_publish_fail, local_sqlite_fallback))

    print("\n[PRUEBA 2] Intento fallido 2 (Supera umbral y abre circuito):")
    print(cb.call(mock_kafka_publish_fail, local_sqlite_fallback))

    print("\n[PRUEBA 3] Intento con circuito abierto (Degradación grácil inmediata sin intentar conectar a la red):")
    print(cb.call(mock_kafka_publish_fail, local_sqlite_fallback))
