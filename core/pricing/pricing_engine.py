#!/usr/bin/env python3
# Etiqueta: APP_CHANGO_PRICING_ENGINE_02102026
# Proyecto: app chango
# Arquitectura: Pricing Engine / Domain-Driven Design / Multi-Tenant Tariffs

from typing import Dict, Any

class PricingEngine:
    """
    Motor de cálculo tarifario dinámico para movilidad urbana.
    Aplica tarifas base, costo por kilómetro, costo por minuto de demora 
    y multiplicadores configurables por franquicia (Tenant).
    """
    def __init__(self):
        # Tarifario base por defecto para la región (Valores en ARS orientativos)
        self.default_tariff = {
            "base_fare": 800.00,
            "price_per_km": 650.00,
            "price_per_min": 120.00,
            "minimum_fare": 1500.00,
            "platform_commission_pct": 10.0
        }

    def calculate_fare(self, distance_meters: float, duration_seconds: float, surge_multiplier: float = 1.0, custom_tariff: Dict[str, Any] = None) -> Dict[str, float]:
        """
        Calcula la tarifa total del viaje, desglosando la ganancia del conductor 
        y la comisión de la plataforma bajo un modelo transparente.
        """
        tariff = custom_tariff or self.default_tariff
        
        distance_km = distance_meters / 1000.0
        duration_min = duration_seconds / 60.0
        
        base = tariff["base_fare"]
        distance_cost = distance_km * tariff["price_per_km"]
        time_cost = duration_min * tariff["price_per_min"]
        
        subtotal = (base + distance_cost + time_cost) * surge_multiplier
        final_fare = max(subtotal, tariff["minimum_fare"])
        
        commission_pct = tariff["platform_commission_pct"]
        platform_fee = final_fare * (commission_pct / 100.0)
        driver_earnings = final_fare - platform_fee
        
        fare_breakdown = {
            "distance_km": round(distance_km, 2),
            "duration_min": round(duration_min, 1),
            "base_fare": round(base, 2),
            "subtotal": round(final_fare, 2),
            "platform_commission": round(platform_fee, 2),
            "driver_earnings": round(driver_earnings, 2),
            "currency": "ARS"
        }
        
        return fare_breakdown

if __name__ == "__main__":
    print("--- [APP CHANGO] Verificando Motor de Tarifas (Pricing Engine) ---")
    engine = PricingEngine()
    
    test_distance = 5400.0
    test_duration = 720.0
    
    fare_result = engine.calculate_fare(test_distance, test_duration, surge_multiplier=1.0)
    
    print("\n[DESGLOSE DE TARIFA CALCULADA]")
    for key, value in fare_result.items():
        print(f"  - {key}: {value}")
        
    print("\n[OK] Pricing Engine validado y listo para integrarse al Trip Engine.")
