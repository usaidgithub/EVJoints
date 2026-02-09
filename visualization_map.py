import json
import folium

# Load route
with open("sampled_with_elevation_50m.json") as f:
    route = json.load(f)

# Load stations map-ready
with open("map_visualization.json") as f:
    stations = json.load(f)

# Center map at source
start = route[0]
m = folium.Map(location=[start["lat"], start["lng"]], zoom_start=9)

# -----------------------------
# Draw Route Polyline
# -----------------------------
route_coords = [(p["lat"], p["lng"]) for p in route]

folium.PolyLine(
    route_coords,
    weight=4
).add_to(m)

# -----------------------------
# Plot ALL Stations + Detour Points
# -----------------------------
for s in stations:

    # Station Marker
    folium.Marker(
        location=[s["station_lat"], s["station_lon"]],
        popup=f"""
        <b>{s['name']}</b><br>
        Arrival SOC: {s['arrival_soc']}%<br>
        Energy Used: {s['energy_used_kwh']} kWh
        """
    ).add_to(m)

    # Detour Point Marker
    folium.CircleMarker(
        location=[s["detour_lat"], s["detour_lon"]],
        radius=4,
        popup=f"Detour Point idx={s['best_route_idx']}"
    ).add_to(m)

    # Line connecting detour → station
    folium.PolyLine(
        [(s["detour_lat"], s["detour_lon"]),
         (s["station_lat"], s["station_lon"])],
        weight=2
    ).add_to(m)

# Save map
m.save("detour_map.html")

print("✅ Map saved: detour_map.html")
print("Total Stations Plotted:", len(stations))
