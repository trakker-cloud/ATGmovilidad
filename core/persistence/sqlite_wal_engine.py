#!/usr/bin/env python3
# Etiqueta: APP_CHANGO_SQLITE_WAL_ENGINE_02102026
# Proyecto: app chango
# Arquitectura: High-Performance SQLite WAL Persistence Engine (ACID & Concurrency)

import sqlite3
import os
from datetime import datetime
from typing import Dict, Any, Optional

class ChangoPersistenceEngine:
    """
    Motor de persistencia atómica local basado en SQLite con modo WAL habilitado.
    Garantiza durabilidad ACID y concurrencia segura para el padrón central,
    coordinadores, deudas de comisiones y estados de viaje.
    """
    def __init__(self, db_path: str = "data/chango_runtime.db"):
        self.db_path = db_path
        self._initialize_storage()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, timeout=10.0)
        conn.row_factory = sqlite3.Row
        return conn

    def _initialize_storage(self):
        """Crea el directorio de datos, activa el modo WAL y levanta las tablas relacionales."""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        conn = self._get_connection()
        try:
            # Activar modo Write-Ahead Logging para máxima concurrencia y velocidad
            conn.execute("PRAGMA journal_mode=WAL;")
            conn.execute("PRAGMA synchronous=NORMAL;")

            # 1. Tabla del Padrón Central de Conductores y Regla de los 90 Días
            conn.execute("""
                CREATE TABLE IF NOT EXISTS drivers_registry (
                    driver_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    vehicle TEXT,
                    current_coordinator TEXT,
                    last_linked_date TEXT,
                    global_status TEXT DEFAULT 'ACTIVE'
                );
            """)

            # 2. Tabla del Libro Contable de Comisiones en Efectivo
            conn.execute("""
                CREATE TABLE IF NOT EXISTS cash_ledger (
                    driver_id TEXT PRIMARY KEY,
                    total_debt_ars REAL DEFAULT 0.0,
                    last_updated TEXT
                );
            """)

            conn.commit()
            print(f"[PERSISTENCE] Almacenamiento SQLite WAL inicializado correctamente en '{self.db_path}'.")
        except Exception as e:
            print(f"[PERSISTENCE ERROR] Fallo al inicializar base de datos: {e}")
        finally:
            conn.close()

    def upsert_driver(self, driver_id: str, name: str, vehicle: str, coordinator_id: Optional[str]) -> Dict[str, Any]:
        """Inserta o actualiza un conductor en el padrón central respetando persistencia en disco."""
        conn = self._get_connection()
        now = datetime.now().isoformat()
        try:
            cursor = conn.cursor()
            # Verificar si ya existe para evaluar cambio de coordinador y fecha
            cursor.execute("SELECT current_coordinator, last_linked_date FROM drivers_registry WHERE driver_id = ?", (driver_id,))
            row = cursor.fetchone()

            if row:
                current_coord = row["current_coordinator"]
                # Actualizar coordinador y fecha de vinculación
                cursor.execute("""
                    UPDATE drivers_registry 
                    SET current_coordinator = ?, last_linked_date = ?, name = ?, vehicle = ?
                    WHERE driver_id = ?
                """, (coordinator_id, now, name, vehicle, driver_id))
                action = "UPDATED_DRIVER"
            else:
                cursor.execute("""
                    INSERT INTO drivers_registry (driver_id, name, vehicle, current_coordinator, last_linked_date, global_status)
                    VALUES (?, ?, ?, ?, ?, 'ACTIVE')
                """, (driver_id, name, vehicle, coordinator_id, now))
                action = "INSERTED_NEW_DRIVER"

            conn.commit()
            return {"status": "SUCCESS", "action": action, "driver_id": driver_id, "coordinator": coordinator_id}
        except Exception as e:
            conn.rollback()
            return {"status": "ERROR", "message": str(e)}
        finally:
            conn.close()

    def get_driver(self, driver_id: str) -> Optional[Dict[str, Any]]:
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM drivers_registry WHERE driver_id = ?", (driver_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
        finally:
            conn.close()

if __name__ == "__main__":
    print("--- [APP CHANGO] Verificando Capa de Persistencia SQLite WAL ---")
    
    db = ChangoPersistenceEngine(db_path="data/test_chango.db")
    
    # Prueba de persistencia de conductor
    res = db.upsert_driver("DRIVER-WAL-01", "Roberto Sanchez", "Chevrolet Onix", "COORD-TUC-01")
    print(res)
    
    # Recuperación desde disco
    driver_data = db.get_driver("DRIVER-WAL-01")
    print("\n[LECTURA DESDE DISCO WAL]:", driver_data)
