import json
import folium

# -----------------------------
# LOAD ROUTE + FINAL MAP DATA
# -----------------------------
with open("sampled_with_elevation_50m.json") as f:
    route = json.load(f)

with open("map_visualization.json") as f:
    stations = json.load(f)

# -----------------------------
# SOURCE POINT (Route Start)
# -----------------------------
SOURCE = (route[0]["lat"], route[0]["lng"])

# Create map
m = folium.Map(location=SOURCE, zoom_start=9)

# -----------------------------
# DRAW FULL ROUTE
# -----------------------------
route_coords = [(p["lat"], p["lng"]) for p in route]

folium.PolyLine(
    route_coords,
    weight=4,
    tooltip="Main Route"
).add_to(m)

# -----------------------------
# MARK SOURCE POINT
# -----------------------------
folium.Marker(
    location=SOURCE,
    popup="🚩 Source Location",
    icon=folium.Icon(icon="play")
).add_to(m)

# -----------------------------
# PLOT STATIONS + DETOURS
# -----------------------------
for s in stations:

    # Values already computed
    source_to_detour = s["source_to_detour_km"]
    total_distance = s["total_distance_km"]
    soc = s["arrival_soc"]
    energy = s["energy_used_kwh"]

    # Popup info
    popup_text = f"""
    <b>{s['name']}</b><br><br>

    🚗 <b>Distance Breakdown</b><br>
    Source → Detour: {source_to_detour:.2f} km<br>
    Total Trip Distance: {total_distance:.2f} km<br><br>

    🔋 Arrival SOC: <b>{soc}%</b><br>
    ⚡ Energy Used: {energy} kWh<br>
    """

    # -----------------------------
    # STATION MARKER
    # -----------------------------
    folium.Marker(
        location=[s["station_lat"], s["station_lon"]],
        popup=popup_text,
        icon=folium.Icon(icon="flash")
    ).add_to(m)

    # -----------------------------
    # DETOUR POINT MARKER
    # -----------------------------
    folium.CircleMarker(
        location=[s["detour_lat"], s["detour_lon"]],
        radius=5,
        popup=f"📍 Detour Point (idx={s['best_route_idx']})",
        color="red",
        fill=True,
        fill_opacity=0.8
    ).add_to(m)

    # -----------------------------
    # LINE: Detour → Station
    # -----------------------------
    folium.PolyLine(
        [(s["detour_lat"], s["detour_lon"]),
         (s["station_lat"], s["station_lon"])],
        weight=2,
        color="orange",
        tooltip="Detour Connection"
    ).add_to(m)

# -----------------------------
# SAVE FINAL MAP
# -----------------------------
m.save("detour_map.html")

print("✅ Final Detour Map Saved: detour_map.html")
print("Total Stations Plotted:", len(stations))
