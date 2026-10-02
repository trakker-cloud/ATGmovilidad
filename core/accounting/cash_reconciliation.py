#!/usr/bin/env python3
# Etiqueta: APP_CHANGO_CASH_RECONCILIATION_02102026
# Proyecto: app chango
# Arquitectura: Cash vs. Digital Ledger & Commission Reconciliation Engine

from datetime import datetime
from typing import Dict, Any, List

class CashReconciliationEngine:
    """
    Gestiona la conciliación contable de los viajes cobrados en efectivo en la calle.
    Calcula la comisión exigida por la plataforma, registra la deuda corriente del conductor
    y audita el balance diario de la franquicia.
    """
    def __init__(self, default_commission_pct: float = 10.0):
        self.default_commission_pct = default_commission_pct
        # Libro mayor de deudas por comisiones de conductores (driver_id -> balance_deuda_ars)
        self.driver_commission_ledger: Dict[str, float] = {}

    def process_cash_trip(self, driver_id: str, trip_id: str, gross_fare: float) -> Dict[str, Any]:
        """
        Procesa un viaje abonado en efectivo. El conductor retiene el total 
        pero acumula una deuda de comisión a favor de la plataforma.
        """
        commission_debt = round(gross_fare * (self.default_commission_pct / 100.0), 2)
        driver_net = round(gross_fare - commission_debt, 2)

        # Actualizar libro mayor del conductor
        current_debt = self.driver_commission_ledger.get(driver_id, 0.0)
        new_total_debt = round(current_debt + commission_debt, 2)
        self.driver_commission_ledger[driver_id] = new_total_debt

        print(f"[ACCOUNTING CASH] Viaje {trip_id} en efectivo por ${gross_fare} para chofer {driver_id}.")
        print(f"                  Comisión generada para la app: ${commission_debt}. Deuda total acumulada: ${new_total_debt}")

        return {
            "status": "CASH_TRIP_RECORDED",
            "trip_id": trip_id,
            "driver_id": driver_id,
            "gross_fare_ars": gross_fare,
            "driver_net_earnings_ars": driver_net,
            "platform_commission_added_ars": commission_debt,
            "driver_total_debt_ars": new_total_debt,
            "timestamp": datetime.now().isoformat()
        }

    def settle_driver_debt(self, driver_id: str, payment_amount: float) -> Dict[str, Any]:
        """
        Registra el pago o liquidación de la deuda de comisiones por parte del conductor 
        (vía transferencia a la cuenta empresa 'changocash' o pago en central).
        """
        current_debt = self.driver_commission_ledger.get(driver_id, 0.0)
        
        if payment_amount > current_debt:
            print(f"[SETTLEMENT WARNING] El pago (${payment_amount}) supera la deuda actual (${current_debt}) del chofer {driver_id}.")
        
        remaining_debt = max(0.0, round(current_debt - payment_amount, 2))
        self.driver_commission_ledger[driver_id] = remaining_debt

        print(f"[SETTLEMENT] Liquidación procesada para chofer {driver_id}. Pagó: ${payment_amount}. Deuda restante: ${remaining_debt}")

        return {
            "status": "DEBT_SETTLED",
            "driver_id": driver_id,
            "amount_paid_ars": payment_amount,
            "remaining_debt_ars": remaining_debt,
            "timestamp": datetime.now().isoformat()
        }

if __name__ == "__main__":
    print("--- [APP CHANGO] Verificando Motor de Conciliación Contable (Efectivo) ---")
    
    engine = CashReconciliationEngine(default_commission_pct=10.0)
    driver_target = "DRIVER-TUC-001"
    
    # 1. Simular dos viajes en efectivo realizados por el chofer
    print("\n[PRUEBA 1] Registro de viajes en efectivo:")
    engine.process_cash_trip(driver_target, "TRIP-01", gross_fare=4000.0)
    engine.process_cash_trip(driver_target, "TRIP-02", gross_fare=6000.0)
    
    # El chofer acumuló $1000 de deuda en comisiones ($400 + $600)
    print(f"\n[ESTADO LEDGER] Deuda actual del chofer {driver_target}: ${engine.driver_commission_ledger[driver_target]}")
    
    # 2. Simular que el chofer liquida su deuda transfiriendo al alias centralizado 'changocash'
    print("\n[PRUEBA 2] Liquidación de comisiones acumuladas:")
    engine.settle_driver_debt(driver_target, payment_amount=1000.0)
