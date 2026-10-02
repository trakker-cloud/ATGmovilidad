#!/usr/bin/env python3
# Etiqueta: APP_CHANGO_GEO_MATCHING_02102026
# Proyecto: app chango
# Arquitectura: Redis GEO / H3 Spatial Indexing / Matching Engine

import h3
import redis
import json
from typing import List, Dict, Optional

class GeoMatchingEngine:
    """
    Motor geoespacial de alta velocidad para la localización de conductores
    y emparejamiento (matching) basado en celdas hexagonales H3 y Redis.
    """
    def __init__(self, redis_host: str = "localhost", redis_port: int = 6379, resolution: int = 8):
        # Resolución 8 de H3 otorga hexágonos con un área promedio de ~0.7 km², 
        # ideal para densidad urbana en Tucumán.
        self.resolution = resolution
        try:
            self.redis_client = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)
            self.redis_client.ping()
            print("[GEO ENGINE] Conexión establecida con Redis Cache.")
        except redis.ConnectionError:
            print("[GEO WARNING] No se pudo conectar a Redis local. Operando en modo mock/memoria.")
            self.redis_client = None

    def update_driver_location(self, tenant_id: str, driver_id: str, lat: float, lng: float, status: str = "ONLINE"):
        """
        Actualiza la posición GPS de un conductor y calcula su celda H3 correspondiente.
        """
        # Calcular el índice H3 basado en latitud y longitud
        h3_index = h3.latlng_to_cell(lat, lng, self.resolution)
        
        driver_data = {
            "driver_id": driver_id,
            "lat": lat,
            "lng": lng,
            "h3_index": h3_index,
            "status": status
        }
        
        if self.redis_client:
            # Clave única por inquilino y celda H3 para segmentar flotas en modo Multi-Tenant
            redis_key = f"tenant:{tenant_id}:h3:{h3_index}"
            # Guardamos los datos del conductor en un Hash de Redis
            self.redis_client.hset(redis_key, driver_id, json.dumps(driver_data))
            # TTL de 30 segundos para limpiar automáticamente conductores que pierdan señal
            self.redis_client.expire(redis_key, 30)
            
        print(f"[GEO] Conductor {driver_id} actualizado en celda H3: {h3_index}")
        return h3_index

    def find_nearby_drivers(self, tenant_id: str, lat: float, lng: float, k_ring_size: int = 1) -> List[Dict]:
        """
        Busca conductores cercanos utilizando la celda H3 actual del pasajero 
        y sus hexágonos circundantes (K-Ring).
        """
        passenger_h3 = h3.latlng_to_cell(lat, lng, self.resolution)
        
        # Obtiene la celda actual y las vecinas (radio de búsqueda inteligente)
        surrounding_cells = h3.grid_disk(passenger_h3, k_ring_size)
        
        available_drivers = []
        
        if self.redis_client:
            for cell in surrounding_cells:
                redis_key = f"tenant:{tenant_id}:h3:{cell}"
                drivers_in_cell = self.redis_client.hgetall(redis_key)
                
                for driver_id, raw_data in drivers_in_cell.items():
                    driver = json.loads(raw_data)
                    if driver.get("status") == "ONLINE":
                        available_drivers.append(driver)
        
        print(f"[MATCHING] Pasajero en celda {passenger_h3}. Conductores encontrados en radio H3: {len(available_drivers)}")
        return available_drivers

if __name__ == "__main__":
    print("--- [APP CHANGO] Verificando Motor de Matching Georreferenciado ---")
    
    # Simulación de prueba para San Miguel de Tucumán (Ej: Plaza Independencia)
    tucuman_lat = -26.8083
    tucuman_lng = -65.2176
    
    engine = GeoMatchingEngine()
    
    # Simulamos la actualización de un conductor en la zona
    engine.update_driver_location("app_chango", "DRIVER-TUC-007", tucuman_lat, tucuman_lng, "ONLINE")
    
    # Buscamos conductores cercanos para un pasajero en las adyacencias
    candidates = engine.find_nearby_drivers("app_chango", tucuman_lat, tucuman_lng, k_ring_size=1)
    
    print(f"\n[OK] Candidatos listos para el despacho: {len(candidates)}")
    if candidates:
        print(f"     Primer candidato: {candidates[0]['driver_id']} en celda {candidates[0]['h3_index']}")
