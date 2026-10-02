#!/usr/bin/env python3
# Etiqueta: APP_CHANGO_DYNAMIC_ADMIN_PRICING_02102026
# Proyecto: app chango
# Arquitectura: Dynamic Admin-Controlled Pricing & Commission Engine

from datetime import datetime
from typing import Dict, Any, Optional

class AdminControlledPricingManager:
    """
    Gestiona la configuración tarifaria y de comisiones por franquicia (Tenant).
    Permite al administrador autorizado modificar banderas, costo por kilómetro,
    minutos y porcentaje de comisión en tiempo real.
    """
    def __init__(self):
        # Base de datos simulada en memoria para configuraciones tarifarias por tenant
        self._tenant_tariffs: Dict[str, Dict[str, float]] = {
            "app_chango_root": {
                "base_fare": 800.00,
                "price_per_km": 650.00,
                "price_per_min": 120.00,
                "minimum_fare": 1500.00,
                "platform_commission_pct": 10.0
            }
        }

    def update_tenant_tariff(
        self, 
        tenant_id: str, 
        admin_token: str, 
        new_settings: Dict[str, float]
    ) -> Dict[str, Any]:
        """
        Permite al administrador autorizado modificar la tarifa y comisión en tiempo real.
        Valida el token de administración antes de aplicar los cambios.
        """
        # Validación de seguridad del Administrador
        if admin_token != "GENESIS_ADMIN_SECURE_KEY_2026":
            print(f"[SECURITY ALERT] Intento no autorizado de modificar tarifas en tenant '{tenant_id}'.")
            return {"status": "UNAUTHORIZED", "message": "Token de administración inválido."}

        if tenant_id not in self._tenant_tariffs:
            # Inicializar con valores por defecto si el tenant es nuevo
            self._tenant_tariffs[tenant_id] = self._tenant_tariffs["app_chango_root"].copy()

        current_tariff = self._tenant_tariffs[tenant_id]

        # Actualizar campos permitidos si se proporcionan
        for key in ["base_fare", "price_per_km", "price_per_min", "minimum_fare", "platform_commission_pct"]:
            if key in new_settings:
                current_tariff[key] = float(new_settings[key])

        print(f"[ADMIN PRICING] Tarifas actualizadas exitosamente para la franquicia '{tenant_id}'.")
        print(f"                Nueva configuración: {current_tariff}")

        return {
            "status": "SUCCESS",
            "tenant_id": tenant_id,
            "updated_tariff": current_tariff,
            "timestamp": datetime.now().isoformat()
        }

    def get_current_tariff(self, tenant_id: str) -> Dict[str, float]:
        """Obtiene la tarifa vigente para el cálculo de viajes del tenant."""
        return self._tenant_tariffs.get(tenant_id, self._tenant_tariffs["app_chango_root"])

if __name__ == "__main__":
    print("--- [APP CHANGO] Verificando Control Dinámico de Tarifas por Administrador ---")
    
    manager = AdminControlledPricingManager()
    
    # 1. Consultar tarifa inicial por defecto
    print("\n[INFO] Tarifa inicial vigente:", manager.get_current_tariff("app_chango_root"))
    
    # 2. Modificación dinámica por administrador autorizado (Ej: Aumento de bandera y comisión)
    new_config = {
        "base_fare": 1100.00,
        "price_per_km": 750.00,
        "platform_commission_pct": 12.0 # Modificación de comisión de la app
    }
    
    print("\n[ACCIÓN ADMIN] Ejecutando modificación de tarifas...")
    result = manager.update_tenant_tariff(
        tenant_id="app_chango_root",
        admin_token="GENESIS_ADMIN_SECURE_KEY_2026",
        new_settings=new_config
    )
    
    print("\n[RESULTADO DE ACTUALIZACIÓN]:")
    print(result)
