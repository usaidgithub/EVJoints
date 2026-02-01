import csv
import json
import math
from scipy.spatial import KDTree

# -----------------------------
# LOAD ROUTE POINTS
# -----------------------------
with open("sampled_with_elevation_50m.json") as f:
    route_points = json.load(f)

route_coords = [(p["lat"], p["lng"]) for p in route_points]
route_kdtree = KDTree(route_coords)

print("✅ Route KD-Tree loaded")

# -----------------------------
# HAVERSINE DISTANCE (km)
# -----------------------------
def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # Earth radius in km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)

    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(dlon / 2) ** 2
    )

    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

# -----------------------------
# LOAD STATIONS & FILTER
# -----------------------------
relevant_stations = []
MAX_DISTANCE_KM = 5

with open("stations.csv", newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)

    for row in reader:
        try:
            lat = float(row["latitude"])
            lon = float(row["longitude"])
        except:
            continue  # skip bad rows

        # Find nearest route point
        _, nearest_idx = route_kdtree.query((lat, lon))
        route_lat, route_lon = route_coords[nearest_idx]

        distance_km = haversine(lat, lon, route_lat, route_lon)

        if distance_km <= MAX_DISTANCE_KM:
            row["distance_to_route_km"] = round(distance_km, 3)
            row["nearest_route_index"] = int(nearest_idx)
            relevant_stations.append(row)

# -----------------------------
# SAVE OUTPUT
# -----------------------------
with open("relevant_stations_5km.json", "w", encoding="utf-8") as f:
    json.dump(relevant_stations, f, indent=2)

# -----------------------------
# VERIFICATION OUTPUT
# -----------------------------
print("\n✅ STEP 6 VERIFICATION")
print("Total route points:", len(route_coords))
print("Relevant charging stations:", len(relevant_stations))

if relevant_stations:
    print("\nSample station:")
    s = relevant_stations[0]
    print("Name:", s["name"])
    print("City:", s["city"])
    print("Distance to route (km):", s["distance_to_route_km"])
