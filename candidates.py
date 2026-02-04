import json
import math
from scipy.spatial import KDTree

# -----------------------------
# HAVERSINE DISTANCE (km)
# -----------------------------
def haversine(lat1, lon1, lat2, lon2):
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)

    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(dlon / 2) ** 2
    )
    return 2 * R * math.atan2(math.sqrt(a), math.sqrt(1 - a))


# -----------------------------
# LOAD ROUTE + KD-TREE
# -----------------------------
with open("sampled_with_elevation_50m.json") as f:
    route_points = json.load(f)

route_coords = [(p["lat"], p["lng"]) for p in route_points]
route_kdtree = KDTree(route_coords)

print("✅ Route KD-Tree ready")


# -----------------------------
# LOAD FILTERED STATIONS
# -----------------------------
with open("relevant_stations_5km.json") as f:
    stations = json.load(f)

print("✅ Loaded relevant stations:", len(stations))


# -----------------------------
# STEP 7: Top-K Candidate Points
# -----------------------------
TOP_K = 5

for station in stations:
    lat = float(station["latitude"])
    lon = float(station["longitude"])

    # Query top-K nearest route points
    distances, indices = route_kdtree.query((lat, lon), k=TOP_K)

    candidates = []

    for d, idx in zip(distances, indices):
        route_lat, route_lon = route_coords[idx]

        dist_km = haversine(lat, lon, route_lat, route_lon)

        candidates.append({
            "route_idx": int(idx),
            "distance_km": round(dist_km, 3)
        })

    # Attach candidate list
    station["candidate_detours"] = candidates


# -----------------------------
# SAVE OUTPUT
# -----------------------------
with open("stations_with_candidates.json", "w", encoding="utf-8") as f:
    json.dump(stations, f, indent=2)

print("\n✅ STEP 7 DONE")
print("Saved → stations_with_candidates.json")
