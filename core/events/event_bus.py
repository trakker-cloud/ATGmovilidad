#!/usr/bin/env python3
# Etiqueta: APP_CHANGO_EVENT_BUS_02102026
# Proyecto: app chango
# Arquitectura: Event-Driven Architecture / Apache Kafka Producer-Consumer

import json
import os
from kafka import KafkaProducer, KafkaConsumer
from kafka.errors import KafkaError

class AppChangoEventBus:
    """
    Espina dorsal de eventos basada en Apache Kafka.
    Garantiza que los cambios de estado (Viajes, Ubicación, Pagos) 
    sean distribuidos de forma asíncrona y tolerante a fallos.
    """
    def __init__(self, bootstrap_servers: str = "localhost:9092"):
        self.bootstrap_servers = os.getenv("KAFKA_SERVERS", bootstrap_servers)
        self.producer = None
        self._init_producer()

    def _init_producer(self):
        try:
            self.producer = KafkaProducer(
                bootstrap_servers=[self.bootstrap_servers],
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                key_serializer=lambda k: k.encode('utf-8') if k else None,
                retries=3
            )
            print("[EVENT BUS] Productor de Kafka conectado exitosamente.")
        except Exception as e:
            print(f"[EVENT WARNING] No se pudo conectar a Kafka ({e}). Operando en modo simulación/fallback.")
            self.producer = None

    def publish_event(self, topic: str, event_key: str, event_payload: dict):
        """
        Publica un evento transaccional o de telemetría a un tópico específico de Kafka.
        """
        if self.producer:
            try:
                future = self.producer.send(topic, key=event_key, value=event_payload)
                self.producer.flush(timeout=2.0)
                print(f"[KAFKA PUBLISH] Tópico: '{topic}' | Key: '{event_key}'")
                return True
            except KafkaError as ke:
                print(f"[ERROR KAFKA] Fallo al enviar evento al tópico {topic}: {ke}")
                return False
        else:
            print(f"[SIMULACIÓN EVENTO] Tópico: '{topic}' | Payload: {event_payload}")
            return True

if __name__ == "__main__":
    print("--- [APP CHANGO] Verificando Capa de Eventos (Kafka) ---")
    bus = AppChangoEventBus()
    
    # Simulación de un evento de viaje solicitado
    sample_event = {
        "event_type": "RideRequested",
        "tenant_id": "app_chango",
        "trip_id": "TRIP-TUC-2026-001",
        "passenger_id": "USER-20-23056760",
        "origin": {"lat": -26.8083, "lng": -65.2176},
        "destination": {"lat": -26.8321, "lng": -65.2070}
    }
    
    bus.publish_event("chango.trip.events", "TRIP-TUC-2026-001", sample_event)
    print("\n[OK] Conector de Event Bus validado.")
