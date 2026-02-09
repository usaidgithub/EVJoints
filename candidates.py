import json
import math
from scipy.spatial import KDTree

# -----------------------------
# HAVERSINE DISTANCE (km)
# -----------------------------
def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # Earth radius km

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
# FIX: Convert lat/lon → XY meters
# -----------------------------
def latlon_to_xy(lat, lon, ref_lat):
    """
    Convert lat/lon degrees into local Cartesian meters
    so KDTree works correctly.
    """
    R = 6371000  # Earth radius in meters

    x = math.radians(lon) * R * math.cos(math.radians(ref_lat))
    y = math.radians(lat) * R

    return (x, y)


# -----------------------------
# LOAD ROUTE POINTS
# -----------------------------
with open("sampled_with_elevation_50m.json") as f:
    route_points = json.load(f)

print("✅ Loaded route points:", len(route_points))

# Reference latitude (for projection)
ref_lat = route_points[0]["lat"]

# Build route coordinates in meters
route_xy = [
    latlon_to_xy(p["lat"], p["lng"], ref_lat)
    for p in route_points
]

# KDTree built correctly in projected space
route_kdtree = KDTree(route_xy)

print("✅ Route KDTree built in METERS")


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
MAX_VALID_KM = 5.0  # safety cutoff

for station in stations:

    lat = float(station["latitude"])
    lon = float(station["longitude"])

    # Convert station to XY meters
    station_xy = latlon_to_xy(lat, lon, ref_lat)

    # Query KDTree for nearest points
    distances, indices = route_kdtree.query(station_xy, k=TOP_K)

    candidates = []

    for idx in indices:

        route_lat = route_points[idx]["lat"]
        route_lon = route_points[idx]["lng"]

        # True haversine distance check
        dist_km = haversine(lat, lon, route_lat, route_lon)

        # Reject wrong far matches
        if dist_km > MAX_VALID_KM:
            continue

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

print("\n✅ STEP 7 DONE (Fixed)")
print("Saved → stations_with_candidates.json")


# -----------------------------
# DEBUG CHECK: route_idx=0 issue
# -----------------------------
count0 = 0
for s in stations:
    for c in s["candidate_detours"]:
        if c["route_idx"] == 0:
            count0 += 1

print("\n🔍 Stations containing route_idx=0 candidates:", count0)
