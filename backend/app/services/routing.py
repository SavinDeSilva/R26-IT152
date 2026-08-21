from __future__ import annotations

import math


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Great-circle distance between two WGS84 points in kilometres."""
    r = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


def nearest_entity(lat: float, lng: float, entities, lat_attr="latitude", lng_attr="longitude"):
    """
    Return (entity, distance_km) for the closest entity that has coordinates.
    Entities missing lat/lng are skipped.
    """
    best = None
    best_dist = None
    for entity in entities:
        elat = getattr(entity, lat_attr, None)
        elng = getattr(entity, lng_attr, None)
        if elat is None or elng is None:
            continue
        dist = haversine_km(lat, lng, float(elat), float(elng))
        if best_dist is None or dist < best_dist:
            best = entity
            best_dist = dist
    return best, best_dist
