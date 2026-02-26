import json
import folium

# -----------------------------
# 1. Load the sampled route JSON
# -----------------------------
with open("sampled_route_50m.json", "r") as f:
    route = json.load(f)

print("Total route points:", len(route))

# -----------------------------
# 2. Center map at first point
# -----------------------------
start_lat, start_lon = route[0]

m = folium.Map(
    location=[start_lat, start_lon],
    zoom_start=15,
    tiles="OpenStreetMap"
)

# -----------------------------
# 3. Draw Route Polyline
# -----------------------------
folium.PolyLine(
    route,
    color="blue",
    weight=5,
    opacity=0.8
).add_to(m)

# -----------------------------
# 4. Add Start Marker
# -----------------------------
folium.Marker(
    location=route[0],
    popup="Start Point",
    icon=folium.Icon(color="green")
).add_to(m)

# -----------------------------
# 5. Add End Marker
# -----------------------------
folium.Marker(
    location=route[-1],
    popup="End Point",
    icon=folium.Icon(color="red")
).add_to(m)

# -----------------------------
# 6. Save Offline Map
# -----------------------------
output_file = "route_sampling_50m.html"
m.save(output_file)

print("✅ Offline route map saved as:", output_file)
