#!/usr/bin/env python3
# Etiqueta: APP_CHANGO_MULTITENANT_ORCHESTRATOR_02102026
# Proyecto: app chango
# Arquitectura: Microkernel / Multi-Tenant API Gateway

import asyncio
from fastapi import FastAPI, APIRouter, Request, HTTPException
import uvicorn
from datetime import datetime

class TenantRegistry:
    """
    Registro en memoria de las franquicias operativas.
    En producción, esto será cacheado en Redis desde PostgreSQL.
    """
    def __init__(self):
        # 'app_chango' es el tenant (inquilino) raíz o "Root"
        self.tenants = {
            "app_chango": {
                "brand_name": "App Chango",
                "db_schema": "schema_chango_root",
                "active_verticals": ["urban_mobility"],
                "status": "active"
            },
            "taxi_express_tuc": {
                "brand_name": "Taxi Express Tucumán",
                "db_schema": "schema_taxi_express",
                "active_verticals": ["urban_mobility"],
                "status": "active"
            },
            "agro_logistica_noa": {
                "brand_name": "Agro Logística NOA",
                "db_schema": "schema_agro_noa",
                "active_verticals": ["cargo_logistics", "rural_transit"],
                "status": "active"
            }
        }

    def get_tenant(self, tenant_id: str):
        return self.tenants.get(tenant_id)

class MobilityOSPlatform:
    def __init__(self):
        self.app = FastAPI(
            title="Mobility OS - White Label Gateway",
            description="Motor Híbrido Orquestado por Genesis S.O.I.-O",
            version="1.1.0"
        )
        self.tenant_registry = TenantRegistry()
        self.active_domains = {}
        
        self._setup_tenant_middleware()
        self._setup_base_routes()

    def _setup_tenant_middleware(self):
        """
        Intercepta todo el tráfico y aísla el contexto por franquicia.
        El Frontend/App Mobile debe enviar el header 'X-Franchise-ID'.
        """
        @self.app.middleware("http")
        async def tenant_isolation_layer(request: Request, call_next):
            start_time = datetime.now()
            
            # Identificación de la Franquicia (Si no envía, por defecto es app_chango)
            tenant_id = request.headers.get("X-Franchise-ID", "app_chango")
            tenant_config = self.tenant_registry.get_tenant(tenant_id)
            
            if not tenant_config or tenant_config["status"] != "active":
                # Bloqueo a nivel de Microkernel si la franquicia está suspendida o no existe
                print(f"[AUDIT BLOCK] Intento de acceso a franquicia inválida: {tenant_id}")
                return HTTPException(status_code=403, detail="Franquicia inactiva o no autorizada")

            # Inyectamos la configuración del inquilino en el estado del request 
            # para que el Event Bus y los módulos sepan en qué BD escribir.
            request.state.tenant = tenant_id
            request.state.brand = tenant_config["brand_name"]
            request.state.db_schema = tenant_config["db_schema"]

            response = await call_next(request)
            
            process_time = (datetime.now() - start_time).total_seconds()
            print(f"[AUDIT] Tenant: {tenant_id.upper()} | {request.method} {request.url.path} - {process_time}s")
            
            # Inyectamos el nombre de la marca en la respuesta para el Frontend
            response.headers["X-Powered-By"] = "Genesis Mobility OS"
            response.headers["X-Brand-Context"] = tenant_config["brand_name"]
            return response

    def _setup_base_routes(self):
        @self.app.get("/")
        async def os_heartbeat(request: Request):
            return {
                "system": "Genesis Mobility OS",
                "tenant_context": request.state.tenant,
                "brand_active": request.state.brand,
                "timestamp": datetime.now().isoformat()
            }

    def mount_vertical(self, name: str, prefix: str):
        router = APIRouter(prefix=prefix, tags=[name.upper()])
        
        @router.get("/health")
        async def vertical_health(request: Request):
            # Valida si la franquicia actual compró/tiene activo este vertical
            tenant_config = self.tenant_registry.get_tenant(request.state.tenant)
            if name not in tenant_config["active_verticals"]:
                raise HTTPException(status_code=403, detail=f"El vertical {name} no está habilitado para {tenant_config['brand_name']}")
                
            return {
                "vertical": name, 
                "franchise": request.state.brand,
                "database_target": request.state.db_schema,
                "status": "ready"
            }
            
        self.app.include_router(router)
        self.active_domains[name] = prefix
        print(f"[+] Vertical Acoplada: {name.upper()} (Ruta: {prefix})")

if __name__ == "__main__":
    print("--- [APP CHANGO] Inicializando Mobility OS (Modo Multi-Tenant) ---")
    platform = MobilityOSPlatform()
    
    platform.mount_vertical("urban_mobility", "/api/v1/urban")
    platform.mount_vertical("cargo_logistics", "/api/v1/cargo")
    platform.mount_vertical("rural_transit", "/api/v1/rural")
    
    print("\n[READY] Gateway operativo. Esperando conexiones de franquicias...")
    uvicorn.run(platform.app, host="0.0.0.0", port=8000, log_level="warning")
