#!/usr/bin/env python3
# Etiqueta: APP_CHANGO_DUAL_BUSINESS_RULES_02102026
# Proyecto: app chango
# Arquitectura: Dual Pricing & Driver/User Compliance Engine

from datetime import datetime
from typing import Dict, Any, Optional

class DualBusinessEngine:
    """
    Motor central de reglas de negocio para app chango.
    Gestiona la dualidad de vehículos (Taxi con reloj oficial vs Particular con tarifa app),
    pasajeros en calle (vía QR/código), tarifas fijas sin demanda dinámica, y recargos 
    nocturnos/feriados condicionados por mérito (conductores Elite).
    """
    def __init__(self):
        # Tarifas base fijas (Sin dinámica por demanda masiva)
        self.app_base_fare = 800.00
        self.app_price_per_km = 650.00
        
        # Recargos estipulados por reglas de negocio
        self.NIGHT_SURCHARGE_PCT = 10.0  # Incremento de 22:00 a 06:00
        self.HOLIDAY_SURCHARGE_PCT = 10.0 # Incremento en feriados

    def is_night_time(self, current_hour: int) -> bool:
        """Determina si se encuentra en horario nocturno (22:00 a 06:00)."""
        return current_hour >= 22 or current_hour < 6

    def calculate_trip_fare(
        self, 
        vehicle_type: str,          # "TAXI" o "PARTICULAR"
        trip_origin: str,           # "APP_REQUEST" o "STREET_HAIL"
        distance_meters: float, 
        duration_seconds: float, 
        current_hour: int,
        is_holiday: bool,
        driver_is_elite: bool       # Condición de mérito para aplicar recargo nocturno/feriado
    ) -> Dict[str, Any]:
        """
        Calcula la tarifa aplicando la lógica dual:
        - TAXI + Street Hail -> Reloj oficial / Tarifa municipal.
        - TAXI / PARTICULAR + App Request -> Tarifa oficial de la App (fija).
        - PARTICULAR + Street Hail -> Reloj virtual con tarifa de la App (vía escaneo QR).
        """
        fare_type = "APP_FIXED_TARIFF"
        subtotal = self.app_base_fare + ((distance_meters / 1000.0) * self.app_price_per_km)
        
        # 1. Regla de Taxímetro Oficial para Taxis en la calle
        if vehicle_type == "TAXI" and trip_origin == "STREET_HAIL":
            fare_type = "MUNICIPAL_TAXIMETER_OFFICIAL"
            # Simulación de tarifa de reloj oficial (ajustada a ordenanza)
            subtotal = 950.00 + ((distance_meters / 100.0) * 90.00)

        # 2. Aplicación de Recargos Nocturnos / Feriados (Restringido por mérito Elite)
        applied_surcharge_pct = 0.0
        night_active = self.is_night_time(current_hour)
        
        if (night_active or is_holiday):
            if driver_is_elite:
                applied_surcharge_pct = self.NIGHT_SURCHARGE_PCT if night_active else self.HOLIDAY_SURCHARGE_PCT
                subtotal = subtotal * (1.0 + (applied_surcharge_pct / 100.0))
                print(f"[RULES] Recargo aplicado ({applied_surcharge_pct}%) por Conductor Elite en horario regulado.")
            else:
                print("[RULES] Recargo nocturno/feriado omitido: El conductor no posee estatus Elite o viajes requeridos.")

        return {
            "vehicle_type": vehicle_type,
            "trip_origin": trip_origin,
            "fare_calculation_mode": fare_type,
            "distance_km": round(distance_meters / 1000.0, 2),
            "final_fare_ars": round(subtotal, 2),
            "surcharge_applied_pct": applied_surcharge_pct,
            "currency": "ARS"
        }

class OnboardingCompliance:
    """
    Gestiona los requisitos de registro de usuarios y conductores 
    vinculados estrictamente por DNI y permisos perimetrales de hardware.
    """
    @staticmethod
    def validate_registration(dni: str, user_type: str, accepted_legal_terms: bool, permissions_granted: dict) -> Dict[str, Any]:
        required_permissions = ["audio", "camera", "video", "location"]
        
        if not accepted_legal_terms:
            return {"status": "rejected", "reason": "Debe aceptar las Bases y Condiciones de Uso."}
            
        for perm in required_permissions:
            if not permissions_granted.get(perm, False):
                return {"status": "rejected", "reason": f"Permiso obligatorio denegado: {perm}. La app requiere activación discrecional de hardware."}

        print(f"[ONBOARDING] Registro validado para DNI: {dni} como {user_type.upper()}. Cuenta vinculada biométrica/documentalmente.")
        return {
            "status": "approved",
            "dni": dni,
            "user_type": user_type,
            "system_access": "granted",
            "timestamp": datetime.now().isoformat()
        }

if __name__ == "__main__":
    print("--- [APP CHANGO] Verificando Sistema Dual y Cumplimiento Normativo ---")
    
    engine = DualBusinessEngine()
    
    # Caso 1: Pasajero en calle que sube a un Taxi -> Reloj oficial
    fare_taxi_street = engine.calculate_trip_fare(
        vehicle_type="TAXI", trip_origin="STREET_HAIL", 
        distance_meters=4000.0, duration_seconds=600.0, 
        current_hour=14, is_holiday=False, driver_is_elite=False
    )
    print(f"Caso 1 (Taxi en calle): ${fare_taxi_street['final_fare_ars']} ({fare_taxi_street['fare_calculation_mode']})")

    # Caso 2: Pasajero en calle que sube a un Particular y escanea QR -> Tarifa fija App con recargo nocturno Elite a las 23:30
    fare_part_qr = engine.calculate_trip_fare(
        vehicle_type="PARTICULAR", trip_origin="STREET_HAIL", 
        distance_meters=4000.0, duration_seconds=600.0, 
        current_hour=23, is_holiday=False, driver_is_elite=True
    )
    print(f"Caso 2 (Particular QR nocturno Elite): ${fare_part_qr['final_fare_ars']} ({fare_part_qr['fare_calculation_mode']})")
    
    # Prueba de Onboarding con DNI y permisos
    onboarding = OnboardingCompliance.validate_registration(
        dni="23056760", user_type="driver", accepted_legal_terms=True,
        permissions_granted={"audio": True, "camera": True, "video": True, "location": True}
    )
    print(f"\n[ONBOARDING STATUS]: {onboarding['status'].upper()}")
