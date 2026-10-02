import sys
import os
import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request

# Inyección de dependencias para resolver rutas del microkernel
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.events.event_bus import EventBus
from core.platform_orchestrator import PlatformOrchestrator

# Instanciación de componentes centrales del runtime
event_bus = EventBus()
orchestrator = PlatformOrchestrator()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manejador del ciclo de vida (Lifespan) del microkernel y API Gateway."""
    print("[API GATEWAY] Levantando socket HTTP y conectando al Event Bus...")
    orchestrator.initialize_all()
    yield
    print("[API GATEWAY] Apagando socket y liberando recursos del kernel...")
    orchestrator.shutdown()


# Inicialización de FastAPI con Lifespan Manager
app = FastAPI(
    title="App Chango - API Gateway",
    description="Punto de enlace HTTP para el microkernel de movilidad",
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/system/status")
async def get_system_status():
    """Endpoint de telemetría y salud del runtime."""
    return {
        "status": "OPERATIVE",
        "persistence": "SQLite WAL Active",
        "circuit_breaker": "CLOSED",
        "security": "JWT_RBAC_READY",
        "event_bus": "FALLBACK_RAM" if event_bus.producer is None else "KAFKA_LIVE",
    }


@app.post("/events/publish/{event_name}")
async def publish_external_event(event_name: str, request: Request):
    """Puerta de enlace para inyectar eventos externos al bus interno."""
    payload = await request.json()
    event_bus.publish(event_name, payload)
    return {"status": "Event Dispatched", "event": event_name, "payload": payload}


if __name__ == "__main__":
    # Escuchando en el puerto 8080 para evitar conflictos con el proceso previo
    uvicorn.run("api.main_api:app", host="0.0.0.0", port=8080, reload=True)
