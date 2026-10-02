#!/usr/bin/env python3
# Etiqueta: APP_CHANGO_ADMIN_JURISDICTION_02102026
# Proyecto: app chango
# Arquitectura: Administrative Jurisdiction & Multi-Vehicle Driver Governance

from datetime import datetime
from typing import Dict, Any, List, Optional

class AdminJurisdictionEngine:
    """
    Motor de gobernanza que respalda la jurisprudencia de acción de los administradores.
    Gestiona la asociación de hasta 5 unidades vehiculares por conductor y permite 
    la validación discrecional (aprobación/rechazo de excepciones documentales).
    """
    MAX_VEHICLES_PER_DRIVER = 5

    @staticmethod
    def evaluate_driver_vehicle_registration(
        driver_profile: Dict[str, Any], 
        vehicle_payload: Dict[str, Any], 
        admin_override: bool = False,
        admin_notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Evalúa el registro de un vehículo asociado a un conductor.
        - Verifica que el conductor no exceda el límite de 5 unidades.
        - Aplica el principio de exclusión por no concordancia chofer/vehículo.
        - Si existe 'admin_override=True', la plataforma asume la autorización 
          discrecional bajo la potestad innegable de la administración.
        """
        registered_vehicles: List[dict] = driver_profile.get("registered_vehicles", [])
        vehicle_id = vehicle_payload.get("plate_or_id")
        
        # 1. Límite estricto de unidades
        if len(registered_vehicles) >= AdminJurisdictionEngine.MAX_VEHICLES_PER_DRIVER:
            if not admin_override:
                return {
                    "status": "REJECTED",
                    "reason": f"Límite excedido: El conductor ya posee el máximo de {AdminJurisdictionEngine.MAX_VEHICLES_PER_DRIVER} unidades registradas."
                }

        # 2. Control de concordancia obligatoria
        driver_dni = driver_profile.get("dni")
        vehicle_owner_dni = vehicle_payload.get("owner_dni")
        is_concordant = (driver_dni == vehicle_owner_dni)

        if not is_concordant and not admin_override:
            print(f"[JURISDICTION BLOCK] Exclusión por no concordancia entre chofer (DNI: {driver_dni}) y titular del vehículo (DNI: {vehicle_owner_dni}).")
            return {
                "status": "EXCLUDED_NON_CONCORDANT",
                "authorized": False,
                "reason": "La no concordancia entre titular y chofer es excluyente, salvo autorización discrecional del administrador."
            }

        # 3. Aplicación de Potestad Discrecional del Administrador (Jurisprudencia de Acción)
        if admin_override:
            print(f"[ADMIN DISCRETION] Autorización discrecional aplicada por administrador. Motivo: {admin_notes}")
            authorization_status = "APPROVED_BY_ADMIN_JURISDICTION"
        else:
            authorization_status = "APPROVED_AUTOMATIC_COMPLIANCE"

        # Registro formal en la estructura del conductor
        vehicle_record = {
            "vehicle_id": vehicle_id,
            "model": vehicle_payload.get("model"),
            "category": vehicle_payload.get("category"), # TAXI, REMIS, PARTICULAR
            "linked_at": datetime.now().isoformat(),
            "status": "ACTIVE"
        }
        
        return {
            "status": authorization_status,
            "authorized": True,
            "assigned_vehicle": vehicle_record,
            "admin_discretion_applied": admin_override,
            "admin_notes": admin_notes,
            "timestamp": datetime.now().isoformat()
        }

if __name__ == "__main__":
    print("--- [APP CHANGO] Verificando Motor de Jurisprudencia de Administradores ---")
    
    # Perfil de conductor con un vehículo ya registrado
    driver = {
        "driver_id": "DRIVER-TUC-500",
        "dni": "23056760",
        "registered_vehicles": [{"vehicle_id": "AA123BB", "category": "TAXI"}]
    }
    
    # Intento de registrar un segundo vehículo con titularidad diferente (No concordancia)
    new_vehicle_non_concordant = {
        "plate_or_id": "CC789DD",
        "model": "Fiat Cronos 2024",
        "category": "PARTICULAR",
        "owner_dni": "99888777" # Titular diferente
    }
    
    print("\n[PRUEBA 1] Intento sin override (Debe ser excluido por no concordancia):")
    res_1 = AdminJurisdictionEngine.evaluate_driver_vehicle_registration(driver, new_vehicle_non_concordant, admin_override=False)
    print(json.dumps(res_1, indent=4))
    
    print("\n[PRUEBA 2] Intento con potestad discrecional del Administrador (Jurisprudencia de acción):")
    res_2 = AdminJurisdictionEngine.evaluate_driver_vehicle_registration(
        driver, 
        new_vehicle_non_concordant, 
        admin_override=True, 
        admin_notes="Excepción aprobada por gerencia general. Flota flitrada y auditada físicamente."
    )
    print(json.dumps(res_2, indent=4))
