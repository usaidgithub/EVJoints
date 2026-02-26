import csv
import json
import math
from scipy.spatial import KDTree

# =====================================================
# CONFIG
# =====================================================

ROUTE_FILE = "sampled_with_elevation_50m.json"
STATIONS_FILE = "stations.csv"
OUTPUT_FILE = "filtered_stations.json"

MAX_DISTANCE_KM = 5
USER_PREFERENCE = "left"   # "left" or "right"

# =====================================================
# LOAD ROUTE
# =====================================================

with open(ROUTE_FILE) as f:
    route_points = json.load(f)

# IMPORTANT:
# For geometry math:
# x = longitude
# y = latitude
route_coords = [(p["lng"], p["lat"]) for p in route_points]

route_kdtree = KDTree(route_coords)

print("✅ Route KD-Tree loaded")
print("Total route points:", len(route_coords))


# =====================================================
# HAVERSINE DISTANCE (km)
# =====================================================

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


# =====================================================
# LEFT / RIGHT DETECTION USING CROSS PRODUCT
# =====================================================

def get_side_of_route(prev_pt, next_pt, station_pt):
    """
    Determines whether station lies left or right
    relative to travel direction of route.
    All inputs must be in (lon, lat) format.
    """

    ax, ay = prev_pt      # lon, lat
    bx, by = next_pt      # lon, lat
    cx, cy = station_pt   # lon, lat

    # 2D cross product
    cross = (bx - ax) * (cy - ay) - (by - ay) * (cx - ax)

    if cross > 0:
        return "left"
    elif cross < 0:
        return "right"
    else:
        return "on"


# =====================================================
# FILTER STATIONS
# =====================================================

relevant_stations = []

with open(STATIONS_FILE, newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)

    for row in reader:
        try:
            lat = float(row["latitude"])
            lon = float(row["longitude"])
        except:
            continue  # skip invalid rows

        # KDTree query MUST use (lon, lat)
        _, nearest_idx = route_kdtree.query((lon, lat))

        route_lon, route_lat = route_coords[nearest_idx]

        # Accurate distance using haversine (lat, lon)
        distance_km = haversine(lat, lon, route_lat, route_lon)

        if distance_km > MAX_DISTANCE_KM:
            continue

        # Avoid edge index issues
        if nearest_idx <= 0 or nearest_idx >= len(route_coords) - 1:
            continue

        prev_pt = route_coords[nearest_idx - 1]
        next_pt = route_coords[nearest_idx + 1]

        # Pass station as (lon, lat)
        side = get_side_of_route(
            prev_pt,
            next_pt,
            (lon, lat)
        )

        if side == USER_PREFERENCE:
            row["distance_to_route_km"] = round(distance_km, 3)
            row["nearest_route_index"] = int(nearest_idx)
            row["side"] = side
            relevant_stations.append(row)


# =====================================================
# SAVE OUTPUT
# =====================================================

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(relevant_stations, f, indent=2)

# =====================================================
# VERIFICATION
# =====================================================

print("\n✅ FILTER COMPLETE")
print("User preference:", USER_PREFERENCE)
print("Stations within", MAX_DISTANCE_KM, "km:", len(relevant_stations))

if relevant_stations:
    print("\nSample station:")
    s = relevant_stations[0]
    print("Name:", s.get("name"))
    print("City:", s.get("city"))
    print("Distance to route (km):", s["distance_to_route_km"])
    print("Side:", s["side"])