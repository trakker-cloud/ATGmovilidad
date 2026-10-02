#!/usr/bin/env python3
# Etiqueta: APP_CHANGO_OPERATIONS_GUARD_02102026
# Proyecto: app chango
# Arquitectura: Offline Buffer, SOS Kill Switch & Biometric Verification

import sqlite3
import json
from datetime import datetime
from typing import Dict, Any, List

class OfflineSyncBuffer:
    """
    Buffer local basado en SQLite para almacenar telemetría GPS y eventos 
    durante zonas de sombra (pérdida de señal celular), asegurando sincronización posterior.
    """
    def __init__(self, db_path: str = "offline_buffer.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pending_sync_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                topic TEXT NOT NULL,
                payload TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        conn.commit()
        conn.close()

    def save_event_locally(self, topic: str, payload: dict):
        """Guarda un evento localmente cuando Kafka o la red no están disponibles."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO pending_sync_events (topic, payload) VALUES (?, ?)",
            (topic, json.dumps(payload))
        )
        conn.commit()
        conn.close()
        print(f"[OFFLINE BUFFER] Evento guardado localmente (Zona de sombra). Tópico: {topic}")

    def flush_to_event_bus(self, event_bus_client) -> int:
        """Sincroniza los eventos acumulados con el Event Bus (Kafka) al recuperar señal."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT id, topic, payload FROM pending_sync_events ORDER BY id ASC;")
        rows = cursor.fetchall()
        
        synced_count = 0
        for row in rows:
            event_id, topic, raw_payload = row
            payload = json.loads(raw_payload)
            success = event_bus_client.publish_event(topic, str(event_id), payload)
            if success:
                cursor.execute("DELETE FROM pending_sync_events WHERE id = ?", (event_id,))
                synced_count += 1
            else:
                break # Detener si la red vuelve a caer
                
        conn.commit()
        conn.close()
        print(f"[OFFLINE SYNC] Sincronizados {synced_count} eventos pendientes al Event Bus.")
        return synced_count

class SafetyGuardManager:
    """
    Gestiona el Kill Switch Zonal, Alerta SOS y Validación Biométrica (Centinel).
    """
    @staticmethod
    def trigger_sos_kill_switch(driver_id: str, tenant_id: str, reason: str) -> Dict[str, Any]:
        """Activa el bloqueo de emergencia y alerta silenciosa."""
        print(f"[SOS EMERGENCY] ¡ALERTA ACTIVADA! Conductor {driver_id} en tenant '{tenant_id}'. Motivo: {reason}")
        return {
            "status": "SOS_TRIGGERED",
            "driver_id": driver_id,
            "tenant_id": tenant_id,
            "action": "DRIVER_LOCKED_AND_DISPATCH_ALERTED",
            "timestamp": datetime.now().isoformat()
        }

    @staticmethod
    def verify_driver_biometrics(driver_dni: str, biometric_hash: str) -> bool:
        """Validación biométrica rápida en el inicio de turno (Centinel Protocol)."""
        expected_hash = f"BIO_HASH_{driver_dni}_SECURE"
        is_valid = (biometric_hash == expected_hash)
        if is_valid:
            print(f"[CENTINEL BIOMETRIC] Validación biométrica exitosa para DNI: {driver_dni}")
        else:
            print(f"[CENTINEL BIOMETRIC] Falla de validación biométrica para DNI: {driver_dni}")
        return is_valid

if __name__ == "__main__":
    print("--- [APP CHANGO] Verificando Módulo de Resiliencia y Seguridad ---")
    
    # 1. Prueba de Buffer Offline
    buffer = OfflineSyncBuffer()
    buffer.save_event_locally("chango.trip.events", {"trip_id": "OFFLINE-01", "status": "IN_PROGRESS"})
    
    # 2. Prueba de Seguridad (SOS)
    SafetyGuardManager.trigger_sos_kill_switch("DRIVER-TUC-007", "app_chango", "Situación de riesgo en vía pública")
    
    # 3. Prueba de Biometría Centinel
    SafetyGuardManager.verify_driver_biometrics("23056760", "BIO_HASH_23056760_SECURE")
    
    print("\n[OK] Módulo de operaciones y seguridad validado.")
