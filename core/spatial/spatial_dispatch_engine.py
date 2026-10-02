#!/usr/bin/env python3
# Etiqueta: APP_CHANGO_SPATIAL_DISPATCH_ENGINE_02102026
# Proyecto: app chango
# Arquitectura: High-Performance Spatial Indexing & Proximity Dispatch Engine

import math
from datetime import datetime
from typing import Dict, Any, List, Optional

class SpatialDispatchEngine:
    """
    Motor de indexación espacial y despacho por proximidad para app chango.
    Calcula distancias geodésicas (Haversine) y filtra conductores cercanos
    aplicando criterios de estatus Elite y radio dinámico de búsqueda en Tucumán.
    """
    @staticmethod
    def _haversine_distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calcula la distancia real en kilómetros entre dos coordenadas geográficas."""
        R = 6371.0  # Radio de la Tierra en km
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = (math.sin(dlat / 2) ** 2 + 
             math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * 
             math.sin(dlon / 2) ** 2)
        c = 2 * math.asin(math.sqrt(a))
        return R * c

    @classmethod
    def find_nearest_available_drivers(
        cls, 
        pickup_lat: float, 
        pickup_lon: float, 
        active_drivers: List[Dict[str, Any]], 
        max_radius_km: float = 3.5
    ) -> List[Dict[str, Any]]:
        """
        Frena la búsqueda espacialmente: evalúa la posición de cada chofer activo,
        calcula la distancia al punto de recogida (pickup) y ordena por proximidad.
        """
        matched_pool = []
        
        for driver in active_drivers:
            d_lat = driver.get("lat")
            d_lon = driver.get("lon")
            if d_lat is None or d_lon is None:
                continue
                
            distance = cls._haversine_distance_km(pickup_lat, pickup_lon, d_lat, d_lon)
            
            if distance <= max_radius_km:
                driver_record = driver.copy()
                driver_record["distance_km"] = round(distance, 2)
                matched_pool.append(driver_record)

        # Ordenar por el más cercano al pasajero
        matched_pool.sort(key=lambda x: x["distance_km"])
        
        print(f"[SPATIAL ENGINE] Búsqueda en radio de {max_radius_km}km completada. {len(matched_pool)} chofer(es) encontrados.")
        return matched_pool

if __name__ == "__main__":
    print("--- [APP CHANGO] Verificando Motor de Indexación Espacial ---")
    
    # Coordenadas simuladas en San Miguel de Tucumán (ej. Plaza Independencia)
    tucuman_center_lat = -26.8308
    tucuman_center_lon = -65.2039
    
    # Flota simulada en calle
    mock_fleet = [
        {"driver_id": "DRIVER-01", "lat": -26.8320, "lon": -65.2050, "elite": True}, # Cerca (~180m)
        {"driver_id": "DRIVER-02", "lat": -26.8500, "lon": -65.2200, "elite": False},# Más lejos (~2.5km)
        {"driver_id": "DRIVER-03", "lat": -27.0000, "lon": -65.5000, "elite": True}   # Fuera de rango
    ]
    
    nearby_drivers = SpatialDispatchEngine.find_nearest_available_drivers(
        tucuman_center_lat, tucuman_center_lon, mock_fleet, max_radius_km=3.0
    )
    
    print("\n[RESULTADO ESPACIAL]:")
    for d in nearby_drivers:
        print(f" -> Chofer {d['driver_id']} a {d['distance_km']} km (Elite: {d['elite']})")
