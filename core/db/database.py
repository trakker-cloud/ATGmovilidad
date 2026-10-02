#!/usr/bin/env python3
# Etiqueta: APP_CHANGO_DATABASE_CONNECTOR_02102026
# Proyecto: app chango
# Arquitectura: Microkernel / PostgreSQL + PostGIS / Multi-Tenant

import os
import asyncpg
from typing import Optional

class DatabaseManager:
    """
    Gestor de conexiones asíncronas a PostgreSQL con soporte multi-tenant 
    mediante la separación estricta de esquemas (schema_path).
    """
    def __init__(self):
        # En producción, estas credenciales vendrán de variables de entorno seguras (.env)
        self.user = os.getenv("DB_USER", "postgres")
        self.password = os.getenv("DB_PASSWORD", "postgres")
        self.database = os.getenv("DB_NAME", "app_chango_db")
        self.host = os.getenv("DB_HOST", "localhost")
        self.port = os.getenv("DB_PORT", "5432")
        self.pool: Optional[asyncpg.Pool] = None

    async def connect(self):
        """Inicializa el pool de conexiones asíncronas."""
        if not self.pool:
            self.pool = await asyncpg.create_pool(
                user=self.user,
                password=self.password,
                database=self.database,
                host=self.host,
                port=self.port,
                min_size=5,
                max_size=20
            )
            print("[DB MANAGER] Pool de conexiones PostgreSQL establecido exitosamente.")

    async def disconnect(self):
        """Cierra el pool de conexiones."""
        if self.pool:
            await self.pool.close()
            print("[DB MANAGER] Pool de conexiones cerrado.")

    async def get_tenant_connection(self, schema_name: str):
        """
        Obtiene una conexión del pool y fija el esquema (schema_path) 
        garantizando el aislamiento absoluto de datos por franquicia (Multi-Tenant).
        """
        if not self.pool:
            await self.connect()
        
        conn = await self.pool.acquire()
        try:
            # Asegura que las consultas operen dentro del esquema de la franquicia actual
            await conn.execute(f"SET search_path TO {schema_name}, public;")
            return conn
        except Exception as e:
            await self.pool.release(conn)
            raise RuntimeError(f"Error al configurar esquema multi-tenant '{schema_name}': {e}")

    async def release_connection(self, conn):
        """Devuelve la conexión al pool."""
        if self.pool and conn:
            await self.pool.release(conn)

db_manager = DatabaseManager()
