import json
import logging
from kafka import KafkaProducer
from kafka.errors import NoBrokersAvailable

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("EventBus-Kernel")

class EventBus:
    """
    Motor de eventos central del microkernel (EDA).
    Implementa patrón Singleton para unificar el canal de publicación.
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(EventBus, cls).__new__(cls)
            cls._instance._initialize_bus()
        return cls._instance

    def _initialize_bus(self):
        self.bootstrap_servers = ['localhost:9092']
        self.producer = None
        logger.info("[EVENT BUS] Inicializando puente asíncrono de eventos...")
        
        try:
            # Configurado con timeout bajo (2000ms) para no bloquear el runtime si Kafka está caído
            self.producer = KafkaProducer(
                bootstrap_servers=self.bootstrap_servers,
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                api_version_auto_timeout_ms=2000,
                request_timeout_ms=2000
            )
            logger.info("[EVENT BUS] Conectado a Apache Kafka (Broker Operativo).")
        except NoBrokersAvailable:
            logger.warning("[EVENT BUS] Advertencia: Broker Kafka no detectado en localhost:9092.")
            logger.warning("[EVENT BUS] El microkernel operará en modo degradado (Fallback: RAM/Console).")

    def publish(self, event_name: str, payload: dict):
        """Publica un evento en el bus distribuido."""
        if self.producer:
            try:
                self.producer.send(event_name, payload)
                self.producer.flush()
                logger.info(f"[EVENT BUS] Topico '{event_name}' -> Emitido con éxito.")
            except Exception as e:
                logger.error(f"[EVENT BUS] Fallo al emitir evento: {str(e)}")
        else:
            # Ruta de contingencia para evitar pánico del kernel
            logger.info(f"[EVENT BUS FALLBACK] {event_name} | Datos: {payload}")
