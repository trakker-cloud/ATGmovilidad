#!/usr/bin/env python3
# Etiqueta: APP_CHANGO_TRIP_ENGINE_02102026
# Proyecto: app chango
# Arquitectura: Microkernel / Domain-Driven Design / State Machine

from enum import Enum
from datetime import datetime
from typing import Dict, Optional

class TripState(str, Enum):
    REQUESTED = "REQUESTED"
    SEARCHING = "SEARCHING"
    OFFERED = "OFFERED"
    ACCEPTED = "ACCEPTED"
    DRIVER_ARRIVING = "DRIVER_ARRIVING"
    PASSENGER_ONBOARD = "PASSENGER_ONBOARD"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"
    SYSTEM_ERROR = "SYSTEM_ERROR"

class TripStateMachine:
    """
    Máquina de estados estricta para el ciclo de vida de un viaje en app chango.
    Garantiza transiciones válidas según el dominio de movilidad urbana.
    """
    TRANSITIONS = {
        TripState.REQUESTED: [TripState.SEARCHING, TripState.CANCELLED, TripState.SYSTEM_ERROR],
        TripState.SEARCHING: [TripState.OFFERED, TripState.CANCELLED, TripState.SYSTEM_ERROR],
        TripState.OFFERED: [TripState.ACCEPTED, TripState.SEARCHING, TripState.CANCELLED], # Vuelve a searching si rechaza
        TripState.ACCEPTED: [TripState.DRIVER_ARRIVING, TripState.CANCELLED],
        TripState.DRIVER_ARRIVING: [TripState.PASSENGER_ONBOARD, TripState.CANCELLED],
        TripState.PASSENGER_ONBOARD: [TripState.IN_PROGRESS, TripState.CANCELLED],
        TripState.IN_PROGRESS: [TripState.COMPLETED, TripState.SYSTEM_ERROR],
        TripState.COMPLETED: [],
        TripState.CANCELLED: [],
        TripState.SYSTEM_ERROR: []
    }

    def __init__(self, trip_id: str, passenger_id: str, origin: dict, destination: dict):
        self.trip_id = trip_id
        self.passenger_id = passenger_id
        self.origin = origin
        self.destination = destination
        self.current_state = TripState.REQUESTED
        self.assigned_driver_id: Optional[str] = None
        self.created_at = datetime.now().isoformat()
        self.history = [{"state": self.current_state, "timestamp": self.created_at}]

    def transition_to(self, new_state: TripState, metadata: Optional[dict] = None) -> bool:
        """Valida y ejecuta la transición de estado de manera segura."""
        allowed_states = self.TRANSITIONS.get(self.current_state, [])
        
        if new_state not in allowed_states:
            print(f"[ERROR TRANSICIÓN] Viaje {self.trip_id}: No se puede pasar de {self.current_state} a {new_state}")
            return False
            
        self.current_state = new_state
        transition_record = {
            "state": self.current_state,
            "timestamp": datetime.now().isoformat(),
            "meta": metadata or {}
        }
        self.history.append(transition_record)
        print(f"[TRIP ENGINE] Viaje {self.trip_id} -> Estado actualizado: {self.current_state}")
        return True

if __name__ == "__main__":
    print("--- [APP CHANGO] Verificando Trip Engine (Simulación de Ciclo) ---")
    
    # Simulación de un viaje urbano en San Miguel de Tucumán
    trip = TripStateMachine(
        trip_id="TRIP-TUC-2026-001",
        passenger_id="USER-20-23056760",
        origin={"lat": -26.8083, "lng": -65.2176, "address": "Plaza Independencia"},
        destination={"lat": -26.8321, "lng": -65.2070, "address": "Terminal de Ómnibus"}
    )
    
    # Ciclo transaccional de prueba
    trip.transition_to(TripState.SEARCHING, {"radius_meters": 3000})
    trip.transition_to(TripState.OFFERED, {"driver_id": "DRIVER-99", "eta_min": 4})
    trip.transition_to(TripState.ACCEPTED, {"driver_id": "DRIVER-99"})
    trip.transition_to(TripState.DRIVER_ARRIVING)
    trip.transition_to(TripState.PASSENGER_ONBOARD)
    trip.transition_to(TripState.IN_PROGRESS)
    trip.transition_to(TripState.COMPLETED, {"fare_ars": 4500.00})
    
    print("\n[OK] Máquina de estados validada y lista para integrarse con Kafka Event Bus.")
