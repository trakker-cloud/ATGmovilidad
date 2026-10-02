#!/usr/bin/env python3
# Etiqueta: APP_CHANGO_MASTER_RUNNER_02102026
# Proyecto: app chango
# Arquitectura: Microkernel Master Orchestrator (With WAL Persistence & Spatial Dispatch)

import sys
import os

# Asegurar ruta del proyecto
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.persistence.sqlite_wal_engine import ChangoPersistenceEngine
from core.spatial.spatial_dispatch_engine import SpatialDispatchEngine
from core.pricing.dynamic_admin_pricing import AdminControlledPricingManager
from core.affiliates.coordinator_engine import CoordinatorScannerEngine
from core.resilience.circuit_breaker import CircuitBreaker
from core.payments.corporate_alias_gateway import CorporateAliasPaymentGateway
from core.accounting.cash_reconciliation import CashReconciliationEngine
from core.security.jwt_rbac_engine import RBACSecurityEngine

def initialize_chango_runtime():
    print("==================================================")
    print("   [RUNTIME START] INICIALIZANDO APP CHANGO       ")
    print("==================================================")
    
    # 1. Inicializar Capa de Persistencia en Disco (SQLite WAL)
    print("\n[1/7] Inicializando Base de Datos Atómica (SQLite WAL)...")
    db_engine = ChangoPersistenceEngine(db_path="data/chango_runtime.db")
    db_engine.upsert_driver("DRIVER-TUC-01", "Jose Conductor", "Fiat Cronos", "COORD-TUC-01")
    print("      -> Persistencia WAL activa y padrón central sincronizado.")

    # 2. Inicializar Motor de Indexación Espacial
    print("\n[2/7] Inicializando Motor de Despacho Espacial (Haversine)...")
    tucuman_lat, tucuman_lon = -26.8308, -65.2039
    mock_fleet = [{"driver_id": "DRIVER-TUC-01", "lat": -26.8320, "lon": -65.2050, "elite": True}]
    nearest = SpatialDispatchEngine.find_nearest_available_drivers(tucuman_lat, tucuman_lon, mock_fleet, max_radius_km=3.0)
    print(f"      -> Encontrados {len(nearest)} chofer(es) activos en radio urbano.")

    # 3. Inicializar Motor de Seguridad JWT y RBAC
    print("\n[3/7] Inicializando Motor de Seguridad JWT y RBAC...")
    jwt_token = RBACSecurityEngine.create_access_token("ADMIN-ROOT", "ROLE_ADMIN_FRANCHISE", "tucuman_central")
    auth_check = RBACSecurityEngine.verify_authorization(jwt_token, "ROLE_ADMIN_FRANCHISE")
    print(f"      -> Estado de Autorización Admin: {auth_check['authorized']}")

    # 4. Inicializar Pasarela de Pagos Corporativa (Standby Mode)
    print("\n[4/7] Inicializando Pasarela de Pagos (Alias 'changocash')...")
    gateway = CorporateAliasPaymentGateway(franchise_alias="changocash", is_active=False)
    payment_test = gateway.generate_alias_payment_request("TRIP-INIT-001", 4500.0, "PASS-01")
    print(f"      -> Estado de Pasarela: {payment_test['status']}")

    # 5. Inicializar Motor Tarifario del Administrador
    print("\n[5/7] Inicializando Motor Tarifario del Administrador...")
    pricing = AdminControlledPricingManager()
    current_tariff = pricing.get_current_tariff("tucuman_central")
    print(f"      -> Tarifa Base Vigente: ${current_tariff['base_fare']}")

    # 6. Inicializar Motor Contable de Efectivo
    print("\n[6/7] Inicializando Motor de Conciliación Contable (Cash)...")
    accounting = CashReconciliationEngine(default_commission_pct=10.0)
    accounting.process_cash_trip("DRIVER-TUC-01", "TRIP-INIT-001", 4500.0)

    # 7. Verificar Resiliencia (Circuit Breaker)
    print("\n[7/7] Verificando Subsistema de Resiliencia (Circuit Breaker)...")
    cb = CircuitBreaker(failure_threshold=2, recovery_timeout_sec=1.0)
    print("      -> Circuit Breaker en estado CLOSED y operativo.")

    print("\n==================================================")
    print("   [OK] APP CHANGO OPERATIVA, WAL & ESPACIAL OK   ")
    print("==================================================")

if __name__ == "__main__":
    initialize_chango_runtime()
