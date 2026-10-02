#!/usr/bin/env python3
# Etiqueta: APP_CHANGO_SCHEMA_REGISTRY_V1_02102026
# Proyecto: app chango (Movilidad Urbana - Tucumán, Argentina)
# Arquitectura: Microkernel / Domain-Driven Design / Event Bus

import hashlib
import json
from datetime import datetime

class AppChangoSchemaRegistry:
    def __init__(self):
        # Metadatos de identificación e inmutabilidad
        self.project_name = "app chango"
        self.domain = "movilidad urbana"
        self.location = "san miguel de tucuman, argentina"
        
        # Trazabilidad de autoría y linaje
        self.original_creation = "20-06-2025"
        self.author_id = "20-23056760-4"
        self.current_update = "02-10-2026"
        self.updated_by = "genesis gravity soi-o"
        
        # Libro diario apendicular (Append-Only Registry)
        self.schema_ledger = []

    def _calculate_hash(self, previous_hash: str, schema_name: str, payload: dict) -> str:
        """Calcula el hash SHA-256 encadenado garantizando la inmutabilidad."""
        raw_string = f"{previous_hash}|{self.original_creation}|{self.author_id}|{schema_name}|{json.dumps(payload, sort_keys=True)}"
        return hashlib.sha256(raw_string.encode('utf-8')).hexdigest()

    def register_schema(self, schema_name: str, payload: dict) -> dict:
        """Registra una nueva entrada o actualización en el historial de app chango."""
        # Obtener el hash del bloque anterior (cadena apendicular)
        previous_hash = self.schema_ledger[-1]["metadata"]["sha256_signature"] if self.schema_ledger else "0" * 64
        
        signature = self._calculate_hash(previous_hash, schema_name, payload)
        
        entry = {
            "version": len(self.schema_ledger) + 1,
            "metadata": {
                "project": self.project_name,
                "domain": self.domain,
                "origin": self.location,
                "author": self.author_id,
                "created_at": self.original_creation,
                "updated_at": self.current_update,
                "updated_by": self.updated_by,
                "previous_hash": previous_hash,
                "sha256_signature": signature
            },
            "schema_name": schema_name,
            "payload": payload
        }
        
        self.schema_ledger.append(entry)
        return entry

    def print_audit_chain(self):
        """Imprime la cadena de auditoría completa de app chango."""
        print(f"\n================ LIBRO DIARIO DE ESQUEMAS - {self.project_name.upper()} ================")
        for block in self.schema_ledger:
            print(f"Versión: {block['version']} | Esquema: {block['schema_name']}")
            print(f"Hash Actual: {block['metadata']['sha256_signature']}")
            print(f"Hash Previo: {block['metadata']['previous_hash']}")
            print("-" * 75)

if __name__ == "__main__":
    registry = AppChangoSchemaRegistry()
    
    # Registro de bloque génesis base
    init_payload = {
        "system_status": "ready",
        "scope": "tucuman_urban_mobility",
        "architecture": "microkernel"
    }
    
    registry.register_schema("app_chango_core_init", init_payload)
    registry.print_audit_chain()
    print("[APP CHANGO READY] Listo para recibir y procesar los esquemas de código.")
