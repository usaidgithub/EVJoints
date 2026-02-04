import json
import folium

# -----------------------------
# LOAD ROUTE POINTS
# -----------------------------
with open("sampled_with_elevation_50m.json") as f:
    route_points = json.load(f)

route_coords = [(p["lat"], p["lng"]) for p in route_points]

print("✅ Loaded route points:", len(route_coords))

# -----------------------------
# LOAD STATIONS WITH CANDIDATES
# -----------------------------
with open("stations_with_candidates.json") as f:
    stations = json.load(f)

print("✅ Loaded stations:", len(stations))

# -----------------------------
# PICK ONE STATION TO VISUALIZE
# -----------------------------
station = stations[0]   # change index if needed

station_lat = float(station["latitude"])
station_lon = float(station["longitude"])

candidates = station["candidate_detours"]

print("\n📍 Visualizing station:", station["name"])
print("Candidate points:", len(candidates))

# -----------------------------
# CREATE MAP CENTERED ON STATION
# -----------------------------
m = folium.Map(location=[station_lat, station_lon], zoom_start=11)

# -----------------------------
# DRAW ROUTE LINE
# -----------------------------
folium.PolyLine(
    route_coords,
    weight=4,
    opacity=0.6,
).add_to(m)

# -----------------------------
# STATION MARKER (RED)
# -----------------------------
folium.Marker(
    location=[station_lat, station_lon],
    popup=f"⚡ Station: {station['name']}",
    icon=folium.Icon(color="red", icon="flash"),
).add_to(m)

# -----------------------------
# CANDIDATE ROUTE POINTS (BLUE)
# -----------------------------
for c in candidates:
    idx = c["route_idx"]
    dist = c["distance_km"]

    lat, lon = route_coords[idx]

    folium.CircleMarker(
        location=[lat, lon],
        radius=6,
        popup=f"Candidate idx={idx} ({dist} km)",
        color="blue",
        fill=True,
        fill_opacity=0.8,
    ).add_to(m)

# -----------------------------
# SAVE MAP OUTPUT
# -----------------------------
m.save("visual_step7.html")

print("\n✅ DONE: Open visual_step7.html in browser")
