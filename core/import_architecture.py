#!/usr/bin/env python3
# Etiqueta: APP_CHANGO_ARCHITECTURE_LOADER_02102026
# Proyecto: app chango
# Arquitectura: Microkernel / Schema Ledger

import hashlib
import json
import os

class PersistentRegistry:
    def __init__(self):
        self.ledger_file = "core/schema_ledger.json"
        self.original_creation = "20-06-2025"
        self.author_id = "20-23056760-4"
        self.current_update = "02-10-2026"
        self.updated_by = "genesis gravity soi-o"
        self.ledger = self._load_ledger()

    def _load_ledger(self) -> list:
        if os.path.exists(self.ledger_file):
            with open(self.ledger_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []

    def _save_ledger(self):
        with open(self.ledger_file, 'w', encoding='utf-8') as f:
            json.dump(self.ledger, f, indent=4)

    def _calculate_hash(self, previous_hash: str, schema_name: str, payload: dict) -> str:
        raw_string = f"{previous_hash}|{self.original_creation}|{self.author_id}|{schema_name}|{json.dumps(payload, sort_keys=True)}"
        return hashlib.sha256(raw_string.encode('utf-8')).hexdigest()

    def register(self, schema_name: str, payload: dict) -> dict:
        previous_hash = self.ledger[-1]["metadata"]["sha256_signature"] if self.ledger else "0" * 64
        signature = self._calculate_hash(previous_hash, schema_name, payload)
        
        entry = {
            "version": len(self.ledger) + 1,
            "schema_name": schema_name,
            "metadata": {
                "author": self.author_id,
                "created_at": self.original_creation,
                "updated_at": self.current_update,
                "updated_by": self.updated_by,
                "previous_hash": previous_hash,
                "sha256_signature": signature
            },
            "payload": payload
        }
        self.ledger.append(entry)
        self._save_ledger()
        return entry

if __name__ == "__main__":
    registry = PersistentRegistry()
    
    # 1. Esquema Génesis Base (si el ledger está vacío)
    if not registry.ledger:
        registry.register("sys_init", {"status": "ready", "architecture": "microkernel"})
    
    # 2. Desglose Estructural del Esquema "CHANGOAPP"
    chango_architecture_payload = {
        "domain": "hybrid_mobility_open_source",
        "nodes": {
            "frontend": ["CHANGO RIDER", "CHANGO DRIVER", "CHANGO CONTROL"],
            "gateway": ["API GATEWAY", "Auth", "RateLimit", "WebSocket", "REST"],
            "cores": {
                "auth": ["USERS", "DRIVERS", "VEHICLES"],
                "mobility": ["TRIP ENGINE", "MATCHING", "PRICING"],
                "voice": ["VOX ENGINE", "STT", "TTS", "INTENT ENGINE", "COMMAND BUS"]
            },
            "infrastructure": {
                "event_bus": "KAFKA",
                "realtime_db": "REDIS",
                "persistent_db": "POSTGRESQL",
                "gis": "POSTGIS",
                "map_data": "OPENSTREETMAP",
                "routing_eta": "VALHALLA"
            },
            "trip_state_machine": [
                "REQUESTED", "SEARCHING", "OFFERED", "ACCEPTED", 
                "DRIVER_ARRIVING", "PASSENGER_ONBOARD", "IN_PROGRESS", 
                "COMPLETED", "CANCELLED", "NO_DRIVER", "DRIVER_CANCELLED", 
                "PASSENGER_CANCELLED", "SYSTEM_ERROR"
            ],
            "event_topics": {
                "trip_events": ["RideRequested", "RideSearching", "RideOffered", "RideAccepted", "TripStarted", "TripCompleted"],
                "location_events": ["DriverOnline", "DriverOffline", "Tracking"],
                "payment_events": ["PaymentRequested", "PaymentCompleted", "PaymentFailed"],
                "system_events": ["SOSActivated", "IncidentCreated"]
            },
            "integration": ["GENESIS S.O.I.-O", "POLICY", "PLANNER", "AUDIT", "ORCHESTRATOR"]
        }
    }

    print("--- [APP CHANGO] Inyectando Blueprints Arquitectónicos ---")
    result = registry.register("chango_core_architecture", chango_architecture_payload)
    
    print(f"[+] Esquema registrado exitosamente en el Ledger Persistente.")
    print(f"    Versión: {result['version']}")
    print(f"    Autor: {result['metadata']['author']} (Fecha Origen: {result['metadata']['created_at']})")
    print(f"    Firma SHA-256: {result['metadata']['sha256_signature']}")
    print(f"    Hash Previo: {result['metadata']['previous_hash']}")
    print("\n[OK] El registro ha sido guardado físicamente en core/schema_ledger.json")
