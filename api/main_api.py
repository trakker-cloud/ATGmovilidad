#!/usr/bin/env python3
# Etiqueta: APP_CHANGO_FASTAPI_GATEWAY_02102026
# Proyecto: app chango
# Arquitectura: FastAPI Production Gateway, REST Endpoints & Real-time WebSockets

from fastapi import FastAPI, Depends, HTTPException, status, WebSocket, WebSocketDisconnect
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import List, Optional
import sys
import os

# Asegurar ruta raíz del proyecto
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.persistence.sqlite_wal_engine import ChangoPersistenceEngine
from core.spatial.spatial_dispatch_engine import SpatialDispatchEngine
from core.payments.corporate_alias_gateway import CorporateAliasPaymentGateway
from core.security.jwt_rbac_engine import RBACSecurityEngine

# Inicializar aplicación FastAPI
app = FastAPI(
    title="App Chango Microkernel API",
    description="Backend oficial de movilidad urbana autónoma para San Miguel de Tucumán",
    version="1.0.0"
)

# Instanciar motores globales del microkernel
db = ChangoPersistenceEngine(db_path="data/chango_runtime.db")
gateway = CorporateAliasPaymentGateway(franchise_alias="changocash", is_active=False)
security_scheme = HTTPBearer()

# --- Modelos de Pydantic para Validación de Entradas ---
class TokenRequest(BaseModel):
    user_id: str
    role: str
    tenant_id: str = "tucuman_central"

class DispatchRequest(BaseModel):
    pickup_lat: float
    pickup_lon: float
    max_radius_km: float = 3.5

class PaymentRequest(BaseModel):
    trip_id: str
    amount_ars: float
    passenger_id: str

# --- Endpoints REST ---

@app.get("/")
def health_check():
    return {
        "system": "app chango microkernel",
        "status": "ONLINE",
        "region": "San Miguel de Tucumán",
        "persistence": "SQLite WAL Active"
    }

@app.post("/api/v1/auth/token")
def generate_token(payload: TokenRequest):
    """Emite un token JWT cifrado según el rol y tenant del usuario."""
    try:
        token = RBACSecurityEngine.create_access_token(payload.user_id, payload.role, payload.tenant_id)
        return {"status": "SUCCESS", "access_token": token, "token_type": "bearer"}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@app.post("/api/v1/dispatch/find-nearest")
def find_nearest_drivers(req: DispatchRequest):
    """Busca y ordena mediante indexación espacial a los conductores disponibles cercanos."""
    # Simulación de flota activa obtenida de la base persistente o memoria
    mock_active_fleet = [
        {"driver_id": "DRIVER-TUC-01", "lat": -26.8320, "lon": -65.2050, "elite": True},
        {"driver_id": "DRIVER-TUC-02", "lat": -26.8500, "lon": -65.2200, "elite": False}
    ]
    matched = SpatialDispatchEngine.find_nearest_available_drivers(
        req.pickup_lat, req.pickup_lon, mock_active_fleet, req.max_radius_km
    )
    return {"status": "SUCCESS", "drivers_matched": len(matched), "drivers": matched}

@app.post("/api/v1/payments/request")
def request_corporate_payment(req: PaymentRequest):
    """Genera instrucción de cobro al alias corporativo respetando el modo Standby fiscal."""
    payment_res = gateway.generate_alias_payment_request(req.trip_id, req.amount_ars, req.passenger_id)
    return payment_res

# --- WebSockets para Monitoreo y Despacho en Tiempo Real ---

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

@app.websocket("/ws/v1/telemetry")
async def websocket_telemetry_endpoint(websocket: WebSocket):
    """Canal WebSocket bidireccional para eventos de flota en tiempo real."""
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            print(f"[WS INCOMING] Telemetría recibida: {data}")
            await manager.broadcast(f"ECO_ACK: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        print("[WS DISCONNECT] Cliente desconectado del canal de telemetría.")
