import json
import folium
import math

# -----------------------------
# HAVERSINE FUNCTION
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
# LOAD ROUTE + STATIONS
# -----------------------------
with open("sampled_with_elevation_50m.json") as f:
    route = json.load(f)

with open("map_visualization.json") as f:
    stations = json.load(f)

# Source point (route start)
SOURCE = (19.110394346916838, 72.9255527657633)

# Create map
m = folium.Map(location=SOURCE, zoom_start=9)

# -----------------------------
# DRAW ROUTE POLYLINE
# -----------------------------
route_coords = [(p["lat"], p["lng"]) for p in route]

folium.PolyLine(route_coords, weight=4).add_to(m)

# -----------------------------
# PLOT ALL STATIONS + DETOURS
# -----------------------------
SAMPLING_STEP_KM = 0.05  # 50m = 0.05 km

for s in stations:

    # --- Distance Source → Detour (approx via route index)
    idx = s["best_route_idx"]
    source_to_detour_km = idx * SAMPLING_STEP_KM

    # --- Distance Detour → Station (haversine)
    detour_to_station_km = haversine(
        s["detour_lat"], s["detour_lon"],
        s["station_lat"], s["station_lon"]
    )

    # --- Total distance
    total_distance_km = source_to_detour_km + detour_to_station_km

    # -----------------------------
    # Station Marker Popup
    # -----------------------------
    popup_text = f"""
    <b>{s['name']}</b><br><br>

    🚗 <b>Distance Breakdown</b><br>
    Source → Detour: {source_to_detour_km:.2f} km<br>
    Detour → Station: {detour_to_station_km:.2f} km<br>
    <b>Total Distance: {total_distance_km:.2f} km</b><br><br>

    🔋 Arrival SOC: {s['arrival_soc']}%<br>
    ⚡ Energy Used: {s['energy_used_kwh']} kWh<br>
    """

    folium.Marker(
        location=[s["station_lat"], s["station_lon"]],
        popup=popup_text
    ).add_to(m)

    # -----------------------------
    # Detour Point Marker
    # -----------------------------
    folium.CircleMarker(
        location=[s["detour_lat"], s["detour_lon"]],
        radius=4,
        popup=f"Detour Point idx={idx}"
    ).add_to(m)

    # -----------------------------
    # Line Connection
    # -----------------------------
    folium.PolyLine(
        [(s["detour_lat"], s["detour_lon"]),
         (s["station_lat"], s["station_lon"])],
        weight=2
    ).add_to(m)

# Save map
m.save("detour_map.html")

print("✅ Map saved: detour_map.html")
print("Total Stations Plotted:", len(stations))
