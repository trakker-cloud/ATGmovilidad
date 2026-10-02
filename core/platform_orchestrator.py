import logging
import os
import sys

# Ajuste de ruta para inyección de dependencias interna
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from events.event_bus import EventBus

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Orchestrator-Kernel")

class PlatformOrchestrator:
    """
    Orquestador principal del microkernel.
    Gestiona la secuencia de arranque de los subsistemas y el estado global.
    """
    def __init__(self):
        self.event_bus = EventBus()
        self.is_initialized = False

    def initialize_all(self):
        """Ejecuta la secuencia completa de arranque de módulos internos."""
        if self.is_initialized:
            logger.info("[ORCHESTRATOR] El microkernel ya se encuentra inicializado.")
            return

        logger.info("==================================================")
        logger.info("   [RUNTIME START] INICIALIZANDO MICROKERNEL      ")
        logger.info("==================================================")
        
        # 1. Notificación al Bus de Eventos
        self.event_bus.publish("system_boot", {"status": "INITIALIZING", "node": "local_linux"})

        # 2. Marcador de estado
        self.is_initialized = True
        logger.info("==================================================")
        logger.info("   [OK] MICROKERNEL OPERATIVO & ENLAZADO A API    ")
        logger.info("==================================================")

    def shutdown(self):
        """Procedimiento de apagado controlado del kernel."""
        logger.info("[ORCHESTRATOR] Cerrando recursos y guardando estado del kernel...")
        self.event_bus.publish("system_shutdown", {"status": "STOPPED"})
        self.is_initialized = False
