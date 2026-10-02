#!/usr/bin/env python3
# Etiqueta: APP_CHANGO_WS_GATEWAY_02102026
# Proyecto: app chango
# Arquitectura: FastAPI WebSocket Connection Manager / Real-time Gateway

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict, List
import json

class ConnectionManager:
    """
    Gestor de conexiones activas por WebSocket para pasajeros y conductores,
    segmentado por Franquicia (Multi-Tenant).
    """
    def __init__(self):
        # Estructura: { tenant_id: { user_id: WebSocket } }
        self.active_connections: Dict[str, Dict[str, WebSocket]] = {}

    async def connect(self, tenant_id: str, user_id: str, websocket: WebSocket):
        await websocket.accept()
        if tenant_id not in self.active_connections:
            self.active_connections[tenant_id] = {}
        self.active_connections[tenant_id][user_id] = websocket
        print(f"[WS GATEWAY] Usuario {user_id} conectado a la franquicia '{tenant_id}'.")

    def disconnect(self, tenant_id: str, user_id: str):
        if tenant_id in self.active_connections:
            if user_id in self.active_connections[tenant_id]:
                del self.active_connections[tenant_id][user_id]
                print(f"[WS GATEWAY] Usuario {user_id} desconectado de '{tenant_id}'.")

    async def send_personal_message(self, tenant_id: str, user_id: str, message: dict):
        if tenant_id in self.active_connections and user_id in self.active_connections[tenant_id]:
            websocket = self.active_connections[tenant_id][user_id]
            await websocket.send_text(json.dumps(message))

manager = ConnectionManager()
router = APIRouter(prefix="/ws", tags=["WebSocket Gateway"])

@router.websocket("/connect/{tenant_id}/{user_id}")
async def websocket_endpoint(websocket: WebSocket, tenant_id: str, user_id: str):
    """
    Punto de entrada WebSocket para dispositivos móviles.
    Mantiene la sesión bidireccional viva para telemetría y alertas de viaje.
    """
    await manager.connect(tenant_id, user_id, websocket)
    try:
        while True:
            data = await websocket.receive_text()
            packet = json.loads(data)
            # Procesamiento de mensajes entrantes desde el móvil (ej. pings de GPS)
            print(f"[WS RECV] Tenant: {tenant_id} | User: {user_id} | Data: {packet}")
            
            # Eco de confirmación temporal
            await websocket.send_text(json.dumps({"status": "received", "echo": packet}))
            
    except WebSocketDisconnect:
        manager.disconnect(tenant_id, user_id)

if __name__ == "__main__":
    print("[INFO] Módulo WebSocket Gateway cargado correctamente.")
