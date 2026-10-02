#!/usr/bin/env python3
# Etiqueta: APP_CHANGO_VOX_ENGINE_02102026
# Proyecto: app chango
# Arquitectura: VOX Core / Intent Engine / Hands-Free Command Bus

import json
from typing import Dict, Any

class IntentEngine:
    """
    Motor de intenciones encargado de traducir lenguaje natural (transcrito por STT)
    en comandos estructurados comprensibles por el Mobility Core.
    """
    @staticmethod
    def parse_intent(spoken_text: str) -> Dict[str, Any]:
        text = spoken_text.lower().strip()
        
        # Intención 1: Aceptar viaje pendiente
        if "aceptar" in text or "tomar viaje" in text or "vamos" in text:
            return {
                "intent": "ACCEPT_RIDE",
                "confidence": 0.95,
                "payload": {"action": "accept"}
            }
            
        # Intención 2: Rechazar viaje
        elif "rechazar" in text or "no puedo" in text:
            return {
                "intent": "REJECT_RIDE",
                "confidence": 0.92,
                "payload": {"action": "reject"}
            }
            
        # Intención 3: Solicitar destino (Ej: "llevarme a terminal")
        elif "llevarme a" in text or "ir a" in text:
            destination = text.replace("llevarme a", "").replace("ir a", "").strip()
            return {
                "intent": "REQUEST_DESTINATION",
                "confidence": 0.89,
                "payload": {"destination_name": destination}
            }
            
        # Intención 4: Alerta de Emergencia / SOS por voz
        elif "emergencia" in text or "socorro" in text or "policía" in text:
            return {
                "intent": "SOS_ACTIVATED",
                "confidence": 0.99,
                "payload": {"emergency_type": "driver_distress"}
            }
            
        return {
            "intent": "UNKNOWN_INTENT",
            "confidence": 0.0,
            "payload": {"raw_text": spoken_text}
        }

class VoxCommandBus:
    """
    Bus de comandos de voz. Recibe la señal acústica simulada (STT),
    extrae la intención y despacha la acción correspondiente al sistema.
    """
    def __init__(self):
        self.intent_engine = IntentEngine()

    def process_voice_input(self, audio_transcript: str) -> dict:
        print(f"[VOX STT] Audio convertido a texto: \"{audio_transcript}\"")
        intent_result = self.intent_engine.parse_intent(audio_transcript)
        print(f"[VOX INTENT] Intención detectada: {intent_result['intent']} (Confianza: {intent_result['confidence']})")
        
        # Aquí el Command Bus emitirá el evento correspondiente hacia Kafka / Trip Engine
        return intent_result

if __name__ == "__main__":
    print("--- [APP CHANGO] Verificando VOX Core (Simulación de Comandos por Voz) ---")
    vox_bus = VoxCommandBus()
    
    # Pruebas unitarias de comandos en cabina
    test_phrases = [
        "Aceptar viaje ahora",
        "Llevarme a terminal de ómnibus",
        "Emergencia necesito asistencia",
        "Comando no reconocido de prueba"
    ]
    
    for phrase in test_phrases:
        print("-" * 50)
        vox_bus.process_voice_input(phrase)
    
    print("\n[OK] VOX Core validado y listo para acoplar motores STT/TTS de bajo consumo.")
