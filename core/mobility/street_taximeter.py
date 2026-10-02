#!/usr/bin/env python3
# Etiqueta: APP_CHANGO_STREET_TAXIMETER_02102026
# Proyecto: app chango
# Arquitectura: Municipal Ordinance Compliance / Street Taximeter Engine

import time
import json
from datetime import datetime
from typing import Dict, Any, Optional

class StreetTaximeterEngine:
    """
    Motor de taxímetro físico/digital para pasajeros en calle (bandera libre).
    Diseñado bajo cumplimiento de normativas municipales de transporte 
    (San Miguel de Tucumán), permitiendo activación táctil o por VOX Core.
    """
    def __init__(self, franchise_id: str):
        self.franchise_id = franchise_id
        # Tarifario regulado (Valores base ajustados a ordenanza municipal de referencia)
        self.flag_drop = 950.00      # Bajada de ficha / bandera inicial
        self.price_per_unit = 90.00    # Costo por ficha (cada X metros o segundos)
        self.unit_distance_meters = 100.0 # Cada 100 metros suma una ficha
        self.unit_time_seconds = 30.0     # O cada 30 segundos en espera (semáforos/tráfico)
        
        # Estado interno del taxímetro
        self.active = False
        self.start_time: Optional[float] = None
        self.accumulated_distance_meters = 0.0
        self.current_fare = 0.0
        self.trip_mode = "STREET_HAIL"

    def activate_taximeter(self, trigger_source: str = "TOUCH") -> Dict[str, Any]:
        """
        Acciona el reloj taxímetro (por pantalla táctil o comando de voz del conductor).
        """
        if self.active:
            return {"status": "error", "message": "El taxímetro ya se encuentra en funcionamiento."}

        self.active = True
        self.start_time = time.time()
        self.accumulated_distance_meters = 0.0
        self.current_fare = self.flag_drop
        
        activation_record = {
            "status": "TAXIMETER_STARTED",
            "trigger": trigger_source, # "TOUCH" o "VOX_COMMAND"
            "tenant": self.franchise_id,
            "flag_drop_fare": self.flag_drop,
            "timestamp": datetime.now().isoformat()
        }
        
        print(f"[TAXIMETER MUNICIPAL] ¡Bandera bajada! Activado por: {trigger_source}. Tarifa inicial: ${self.flag_drop}")
        return activation_record

    def simulate_meter_tick(self, delta_meters: float, delta_seconds: float) -> Dict[str, Any]:
        """
        Simula el pulso del odómetro y reloj durante el viaje en la calle.
        """
        if not self.active:
            return {"status": "inactive"}

        self.accumulated_distance_meters += delta_meters
        
        # Cálculo de fichas por distancia y tiempo de espera
        distance_units = self.accumulated_distance_meters / self.unit_distance_meters
        elapsed_time = time.time() - self.start_time
        time_units = elapsed_time / self.unit_time_seconds
        
        # Tarifa dinámica municipal (acumula por la mayor variable activa)
        variable_cost = (distance_units + (time_units * 0.2)) * self.price_per_unit
        self.current_fare = round(self.flag_drop + variable_cost, 2)
        
        return {
            "status": "RUNNING",
            "distance_km": round(self.accumulated_distance_meters / 1000.0, 2),
            "elapsed_min": round(elapsed_time / 60.0, 1),
            "current_fare_ars": self.current_fare
        }

    def stop_taximeter(self) -> Dict[str, Any]:
        """Finaliza el recorrido en calle y emite el ticket digital para el pasajero."""
        if not self.active:
            return {"status": "error", "message": "El taxímetro no está activo."}

        final_data = {
            "status": "TAXIMETER_COMPLETED",
            "mode": self.trip_mode,
            "total_distance_km": round(self.accumulated_distance_meters / 1000.0, 2),
            "total_fare_ars": self.current_fare,
            "timestamp": datetime.now().isoformat()
        }
        
        self.active = False
        print(f"[TAXIMETER MUNICIPAL] Viaje en calle finalizado. Total a cobrar: ${self.current_fare}")
        return final_data

if __name__ == "__main__":
    print("--- [APP CHANGO] Verificando Módulo Taxímetro Municipal (Pasajero en Calle) ---")
    
    taximeter = StreetTaximeterEngine(franchise_id="app_chango")
    
    # 1. Activación por comando de voz (Integración con VOX Core)
    print("\n[SIMULACIÓN VOX] Conductor dice: 'Iniciar taxímetro'")
    taximeter.activate_taximeter(trigger_source="VOX_COMMAND")
    
    # 2. Simulamos avance del vehículo en la calle (ej. 1.5 km recorridos, 3 minutos)
    tick = taximeter.simulate_meter_tick(delta_meters=1500.0, delta_seconds=180.0)
    print(f"[PANTALLA EMERGENTE RELOJ] Distancia: {tick['distance_km']} km | Tarifa actual: ${tick['current_fare_ars']}")
    
    # 3. Finalizar viaje
    ticket = taximeter.stop_taximeter()
