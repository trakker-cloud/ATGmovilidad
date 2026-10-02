#!/usr/bin/env python3
# Etiqueta: APP_CHANGO_CORPORATE_ALIAS_GATEWAY_02102026
# Proyecto: app chango
# Arquitectura: Standby Corporate Alias Payment Gateway (Feature Flag Protected)

from datetime import datetime
from typing import Dict, Any, Optional

class CorporateAliasPaymentGateway:
    """
    Pasarela de pagos basada en cuenta empresa con Alias centralizado (ej. 'changocash').
    Incluye un interruptor de activación (Standby Mode) para respetar los tiempos 
    de regularización fiscal y documental ante ARCA antes de su despliegue definitivo.
    """
    def __init__(self, franchise_alias: str = "changocash", is_active: bool = False):
        self.franchise_alias = franchise_alias
        self.is_active = is_active  # False = En espera de papeles; True = Operativo real
        self.bank_entity = "Cuenta Corriente Empresa (PSP / Banco Interoperable)"

    def set_gateway_status(self, active: bool, admin_auth_token: str) -> Dict[str, Any]:
        """Permite al administrador activar o desactivar la pasarela cuando la documentación esté lista."""
        if admin_auth_token != "GENESIS_ADMIN_SECURE_KEY_2026":
            return {"status": "UNAUTHORIZED", "message": "Token de administrador inválido."}
            
        self.is_active = active
        status_str = "ACTIVA (Producción)" if active else "STANDBY (En espera de trámites fiscales)"
        print(f"[GATEWAY CONFIG] El estado de la pasarela 'changocash' ha cambiado a: {status_str}")
        return {
            "status": "SUCCESS",
            "gateway_alias": self.franchise_alias,
            "is_active": self.is_active,
            "timestamp": datetime.now().isoformat()
        }

    def generate_alias_payment_request(self, trip_id: str, amount_ars: float, passenger_id: str) -> Dict[str, Any]:
        """
        Genera la orden de pago por transferencia al alias centralizado.
        Si la pasarela está en Standby, advierte al sistema que el cobro debe realizarse 
        por medios alternativos (ej. efectivo) hasta completar el alta formal.
        """
        if not self.is_active:
            print(f"[GATEWAY STANDBY] La pasarela con alias '{self.franchise_alias}' está inactiva (Pendiente de papeles ARCA).")
            return {
                "status": "GATEWAY_STANDBY",
                "message": "Pasarela digital en espera de regularización fiscal. Utilice cobro en efectivo.",
                "fallback_method": "CASH_COLLECTION",
                "trip_id": trip_id,
                "amount_ars": amount_ars
            }

        print(f"[GATEWAY ACTIVE] Generando instrucción de transferencia para viaje {trip_id} por ${amount_ars} al alias '{self.franchise_alias}'.")
        return {
            "status": "PAYMENT_REQUEST_GENERATED",
            "gateway_status": "ACTIVE",
            "trip_id": trip_id,
            "passenger_id": passenger_id,
            "amount_ars": amount_ars,
            "payment_details": {
                "alias": self.franchise_alias,
                "provider": self.bank_entity,
                "concept": f"Viaje Chango #{trip_id[-6:]}"
            },
            "timestamp": datetime.now().isoformat()
        }

if __name__ == "__main__":
    print("--- [APP CHANGO] Verificando Pasarela con Interruptor de Standby Fiscal ---")
    
    gateway = CorporateAliasPaymentGateway(franchise_alias="changocash", is_active=False)
    
    # 1. Intentar generar pago mientras está en Standby (Debe derivar a efectivo)
    print("\n[PRUEBA 1] Intento de cobro digital con pasarela en Standby:")
    req_standby = gateway.generate_alias_payment_request("TRIP-999", 3500.0, "PASS-01")
    print(req_standby)
    
    # 2. Simular que ya llegaron los papeles de ARCA y el admin activa la pasarela
    print("\n[PRUEBA 2] Activación formal de la pasarela por el administrador:")
    activation = gateway.set_gateway_status(active=True, admin_auth_token="GENESIS_ADMIN_SECURE_KEY_2026")
    print(activation)
    
    # 3. Generar pago digital ahora que está activa
    print("\n[PRUEBA 3] Intento de cobro digital con pasarela ya ACTIVA:")
    req_active = gateway.generate_alias_payment_request("TRIP-999", 3500.0, "PASS-01")
    print(req_active)
