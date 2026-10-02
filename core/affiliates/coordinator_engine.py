#!/usr/bin/env python3
# Etiqueta: APP_CHANGO_COORDINATOR_SCANNER_90DAYS_02102026
# Proyecto: app chango
# Architecture: Advanced Affiliate Engine with 90-Day Lock & Coordinator In-App Scanner

from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

class MasterRegistryDatabase:
    """
    Padrón Central de Conductores de la App Chango.
    Registra el estado actual, el coordinador asignado y la fecha de última vinculación.
    """
    def __init__(self):
        # driver_id -> { "name": str, "current_coordinator": Optional[str], "last_linked_date": datetime, ... }
        self.drivers_registry: Dict[str, Dict[str, Any]] = {}

    def register_or_update_driver(self, driver_id: str, driver_data: dict, coordinator_id: Optional[str]) -> Dict[str, Any]:
        now = datetime.now()
        
        if driver_id in self.drivers_registry:
            driver = self.drivers_registry[driver_id]
            current_coord = driver.get("current_coordinator")
            last_linked = driver.get("last_linked_date")
            
            # Verificar regla de los 90 días si ya tenía un coordinador distinto
            if current_coord and current_coord != coordinator_id:
                if last_linked and (now - last_linked) < timedelta(days=90):
                    days_passed = (now - last_linked).days
                    remaining_days = 90 - days_passed
                    print(f"[RULE LOCK] Cambio denegado para {driver_id}. Faltan {remaining_days} días para cumplir el ciclo de 90 días.")
                    return {
                        "status": "LOCKED_BY_90_DAYS",
                        "message": f"Debe esperar {remaining_days} días más para cambiar de coordinador."
                    }
            
            # Actualizar coordinador y reiniciar el contador de 90 días
            driver["current_coordinator"] = coordinator_id
            driver["last_linked_date"] = now
            print(f"[MASTER DB] Conductor {driver_id} reasignado al coordinador {coordinator_id}. Ciclo de 90 días reiniciado.")
        else:
            # Nuevo registro en el padrón central
            self.drivers_registry[driver_id] = {
                **driver_data,
                "current_coordinator": coordinator_id,
                "last_linked_date": now,
                "global_status": "ACTIVE"
            }
            print(f"[MASTER DB] Nuevo conductor {driver_id} ingresado al padrón central bajo coordinador {coordinator_id}.")

        return {"status": "SUCCESS", "driver_id": driver_id, "current_coordinator": coordinator_id}

# Instancia global del padrón maestro
master_db = MasterRegistryDatabase()

class CoordinatorScannerEngine:
    """
    Motor de la sub-app para coordinadores dotado de escáner nativo 
    para captar conductores mediante código QR / identificador y validar la regla de 90 días.
    """
    def __init__(self):
        self._coordinators: Dict[str, Dict[str, Any]] = {
            "COORD-TUC-01": {
                "coordinator_id": "COORD-TUC-01",
                "name": "Carlos Gomez",
                "invite_code": "CHANGO_CG01",
                "commission_pct": 2.5
            }
        }

    def scan_driver_identifier(self, coordinator_id: str, scanned_driver_id: str) -> Dict[str, Any]:
        """
        Función del escáner integrado en la sub-app del coordinador.
        Permite escanear el identificador o QR de un chofer ya registrado en la app
        para incorporarlo a su red, respetando la regla de bloqueo de 90 días.
        """
        if coordinator_id not in self._coordinators:
            return {"status": "ERROR", "message": "Coordinador no autorizado o inexistente."}

        # Verificar si el conductor existe en el padrón global
        driver_info = master_db.drivers_registry.get(scanned_driver_id)
        
        if not driver_info:
            return {
                "status": "NOT_FOUND", 
                "message": "El identificador escaneado no corresponde a un conductor registrado en la app."
            }

        # Intentar vincular aplicando validación de 90 días en el padrón central
        result = master_db.register_or_update_driver(
            driver_id=scanned_driver_id,
            driver_data=driver_info,
            coordinator_id=coordinator_id
        )

        if result["status"] == "LOCKED_BY_90_DAYS":
            return result

        print(f"[SCANNER SUCCESS] El coordinador {coordinator_id} absorbió con éxito al conductor {scanned_driver_id} vía escáner.")
        return {
            "status": "SCANNER_RECRUITMENT_SUCCESS",
            "message": "Conductor incorporado exitosamente a su red mediante escáner.",
            "driver_id": scanned_driver_id,
            "timestamp": datetime.now().isoformat()
        }

if __name__ == "__main__":
    print("--- [APP CHANGO] Verificando Escáner de Coordinadores y Regla de 90 Días ---")
    
    engine = CoordinatorScannerEngine()
    coord_id = "COORD-TUC-01"
    
    # 1. Registrar inicialmente a un conductor en el sistema (ej. sin coordinador previo o con COORD-TUC-01)
    master_db.register_or_update_driver(
        "DRIVER-TUC-101", 
        {"name": "Marcos Paz", "vehicle": "Chevrolet Classic"}, 
        coordinator_id="COORD-TUC-01"
    )
    
    # 2. Simular escaneo inmediato (Debería permitirlo por ser el mismo o estar en periodo inicial)
    print("\n[PRUEBA 1] Escaneo con el escáner del coordinador:")
    scan_res_1 = engine.scan_driver_identifier(coord_id, "DRIVER-TUC-101")
    print(scan_res_1)
    
    # 3. Intentar cambiar de coordinador antes de los 90 días (Simularemos que intenta irse con otro coordinador ficticio)
    # Forzamos la fecha de vinculación a ayer para probar la restricción de los 90 días
    master_db.drivers_registry["DRIVER-TUC-101"]["last_linked_date"] = datetime.now() - timedelta(days=10)
    
    print("\n[PRUEBA 2] Intento de cambio de coordinador antes de cumplir 90 días:")
    # Intentamos registrarlo bajo otro coordinador ('COORD-TUC-02')
    lock_test = master_db.register_or_update_driver(
        "DRIVER-TUC-101", 
        {"name": "Marcos Paz"}, 
        coordinator_id="COORD-TUC-02"
    )
    print(lock_test)
