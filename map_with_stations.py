import json
import folium

# -----------------------------
# LOAD ROUTE POINTS
# -----------------------------
with open("sampled_with_elevation_50m.json") as f:
    route_points = json.load(f)

route_coords = [(p["lat"], p["lng"]) for p in route_points]

print("✅ Route loaded:", len(route_coords), "points")

# -----------------------------
# LOAD RELEVANT STATIONS
# -----------------------------
with open("relevant_stations_5km.json") as f:
    stations = json.load(f)

print("✅ Stations loaded:", len(stations))

# -----------------------------
# MAP CENTER = MIDPOINT OF ROUTE
# -----------------------------
mid_index = len(route_coords) // 2
map_center = route_coords[mid_index]

m = folium.Map(location=map_center, zoom_start=9)

# -----------------------------
# DRAW ROUTE POLYLINE
# -----------------------------
folium.PolyLine(
    route_coords,
    weight=5,
    color="blue",
    opacity=0.8
).add_to(m)

# -----------------------------
# MARK SOURCE + DESTINATION
# -----------------------------
folium.Marker(
    route_coords[0],
    popup="SOURCE (Mumbai)",
    icon=folium.Icon(color="green")
).add_to(m)

folium.Marker(
    route_coords[-1],
    popup="DESTINATION (Pune)",
    icon=folium.Icon(color="red")
).add_to(m)

# -----------------------------
# ADD STATION MARKERS
# -----------------------------
for s in stations:
    lat = float(s["latitude"])
    lon = float(s["longitude"])

    name = s["name"]
    city = s["city"]
    dist = s["distance_to_route_km"]

    popup_text = f"""
    <b>{name}</b><br>
    City: {city}<br>
    Distance to Route: {dist} km
    """

    folium.CircleMarker(
        location=(lat, lon),
        radius=5,
        color="orange",
        fill=True,
        fill_opacity=0.8,
        popup=folium.Popup(popup_text, max_width=300)
    ).add_to(m)

# -----------------------------
# SAVE MAP OUTPUT
# -----------------------------
output_file = "route_with_stations.html"
m.save(output_file)

print("\n✅ DONE! Open this file in browser:")
print("   ", output_file)
