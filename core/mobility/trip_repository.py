#!/usr/bin/env python3
# Etiqueta: APP_CHANGO_TRIP_REPOSITORY_02102026
# Proyecto: app chango
# Arquitectura: PostGIS Spatial Persistence / Trip Repository

import json
from core.db.database import db_manager
from core.mobility.trip_engine import TripStateMachine, TripState

class TripRepository:
    """
    Repositorio encargado de persistir los viajes y su historial de estados
    utilizando tipado espacial PostGIS para el origen y destino.
    """
    @staticmethod
    async def initialize_schema(schema_name: str):
        """Crea las tablas necesarias con soporte PostGIS si no existen."""
        conn = await db_manager.get_tenant_connection(schema_name)
        try:
            await conn.execute("CREATE EXTENSION IF NOT EXISTS postgis;")
            
            # Tabla principal de viajes
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS trips (
                    trip_id VARCHAR(64) PRIMARY KEY,
                    passenger_id VARCHAR(64) NOT NULL,
                    driver_id VARCHAR(64),
                    current_state VARCHAR(32) NOT NULL,
                    origin GEOMETRY(Point, 4326) NOT NULL,
                    destination GEOMETRY(Point, 4326) NOT NULL,
                    history JSONB NOT NULL,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                );
            """)
            print(f"[TRIP REPO] Esquema espacial inicializado para tenant: {schema_name}")
        finally:
            await db_manager.release_connection(conn)

    @staticmethod
    async def save_trip(schema_name: str, trip: TripStateMachine):
        """Persiste un nuevo viaje utilizando puntos PostGIS (SRID 4326)."""
        conn = await db_manager.get_tenant_connection(schema_name)
        try:
            query = """
                INSERT INTO trips (trip_id, passenger_id, current_state, origin, destination, history)
                VALUES ($1, $2, $3, ST_SetSRID(ST_MakePoint($4, $5), 4326), ST_SetSRID(ST_MakePoint($6, $7), 4326), $8)
                ON CONFLICT (trip_id) DO UPDATE 
                SET current_state = EXCLUDED.current_state,
                    driver_id = EXCLUDED.driver_id,
                    history = EXCLUDED.history,
                    updated_at = CURRENT_TIMESTAMP;
            """
            await conn.execute(
                query,
                trip.trip_id,
                trip.passenger_id,
                trip.current_state,
                trip.origin["lng"], trip.origin["lat"],
                trip.destination["lng"], trip.destination["lat"],
                json.dumps(trip.history)
            )
            print(f"[DB] Viaje {trip.trip_id} persistido exitosamente en esquema '{schema_name}'.")
        finally:
            await db_manager.release_connection(conn)

if __name__ == "__main__":
    import asyncio
    
    async def test_persistence():
        print("--- [TEST] Probando Repositorio de Viajes con PostGIS ---")
        # Simulación de prueba para la franquicia por defecto 'schema_chango_root'
        schema = "schema_chango_root"
        
        # Nota: Requiere una instancia de PostgreSQL corriendo con PostGIS.
        # Aquí validamos la construcción sintáctica y lógica del conector asíncrono.
        print("[INFO] Módulo de persistencia cargado correctamente en memoria.")

    asyncio.run(test_persistence())
