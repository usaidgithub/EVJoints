import requests
import polyline
import folium
import math
from config import GOOGLE_MAPS_API_KEY
import json

# -----------------------------
# STEP 1: INPUTS (Given)
# -----------------------------
SOURCE = (19.110394346916838, 72.9255527657633)
DESTINATION = (18.579607394136257, 73.90884169273019)
#Harversine formula
def haversine(p1, p2):
    lat1, lon1 = p1
    lat2, lon2 = p2

    R = 6371000  # meters
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)

    a = math.sin(dphi / 2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2)**2
    return 2 * R * math.atan2(math.sqrt(a), math.sqrt(1 - a))
#Linear interpolation
def interpolate(p1, p2, fraction):
    lat = p1[0] + (p2[0] - p1[0]) * fraction
    lon = p1[1] + (p2[1] - p1[1]) * fraction
    return (lat, lon)
#sampling points between source and destination
def sample_route(route_points, step_m=50):
    sampled = [route_points[0]]
    carry = 0.0

    for i in range(1, len(route_points)):
        p_start = route_points[i - 1]
        p_end = route_points[i]

        seg_len = haversine(p_start, p_end)
        if seg_len == 0:
            continue

        dist_covered = 0.0

        while carry + (seg_len - dist_covered) >= step_m:
            remaining = step_m - carry
            fraction = (dist_covered + remaining) / seg_len

            new_point = interpolate(p_start, p_end, fraction)
            sampled.append(new_point)

            dist_covered += remaining
            carry = 0.0

        carry += seg_len - dist_covered

    # Append destination ONCE
    if haversine(sampled[-1], route_points[-1]) > 1:
        sampled.append(route_points[-1])

    return sampled

#Save points in json file
def save_sampled_route(points, filename="sampled_route_50m.json"):
    with open(filename, "w") as f:
        json.dump(points, f, indent=2)

# -----------------------------
# STEP 1A: Fetch route
# -----------------------------
def fetch_route_polyline(source, destination):
    url = "https://maps.googleapis.com/maps/api/directions/json"
    params = {
        "origin": f"{source[0]},{source[1]}",
        "destination": f"{destination[0]},{destination[1]}",
        "mode": "driving",
        "key": GOOGLE_MAPS_API_KEY
    }

    response = requests.get(url, params=params)
    data = response.json()

    if data["status"] != "OK":
        raise Exception(f"Directions API error: {data['status']}")

    polyline_str = data["routes"][0]["overview_polyline"]["points"]
    return polyline_str
def plot_sampling_comparison(original, sampled, source, destination):
    center_lat = (source[0] + destination[0]) / 2
    center_lon = (source[1] + destination[1]) / 2

    m = folium.Map(location=[center_lat, center_lon], zoom_start=7)

    # Original route (thin, red)
    folium.PolyLine(
        original,
        color="red",
        weight=2,
        opacity=0.5,
        tooltip="Original Polyline"
    ).add_to(m)

    # Sampled route (thick, blue)
    folium.PolyLine(
        sampled,
        color="blue",
        weight=4,
        opacity=0.8,
        tooltip="Sampled @50m"
    ).add_to(m)

    folium.Marker(source, tooltip="Source", icon=folium.Icon(color="green")).add_to(m)
    folium.Marker(destination, tooltip="Destination", icon=folium.Icon(color="red")).add_to(m)

    m.save("route_sampling_50m.html")


# -----------------------------
# STEP 1B: Decode polyline
# -----------------------------
def decode_route(polyline_str):
    return polyline.decode(polyline_str)


# -----------------------------
# STEP 1C: Visualize on map
# -----------------------------
def plot_route_on_map(route_points, source, destination):
    # Center map roughly between source & destination
    center_lat = (source[0] + destination[0]) / 2
    center_lon = (source[1] + destination[1]) / 2

    m = folium.Map(location=[center_lat, center_lon], zoom_start=7)

    # Plot route
    folium.PolyLine(
        route_points,
        color="blue",
        weight=5,
        opacity=0.8
    ).add_to(m)

    # Markers
    folium.Marker(source, tooltip="Source", icon=folium.Icon(color="green")).add_to(m)
    folium.Marker(destination, tooltip="Destination", icon=folium.Icon(color="red")).add_to(m)

    # Save map
    m.save("route_step1.html")



# -----------------------------
# MAIN
# -----------------------------
if __name__ == "__main__":
    print("Fetching route from Google Directions API...")
    polyline_str = fetch_route_polyline(SOURCE, DESTINATION)

    print("Decoding polyline...")
    route_points = decode_route(polyline_str)

    print(f"Decoded {len(route_points)} route points")

    print("Generating map...")
    plot_route_on_map(route_points, SOURCE, DESTINATION)

    print("DONE ✅ Open route_step1.html in browser")
    print("Sampling route at 50m resolution...")
    sampled_route = sample_route(route_points, step_m=50)

    print(f"Sampled points count: {len(sampled_route)}")

    save_sampled_route(sampled_route)

    plot_sampling_comparison(route_points, sampled_route, SOURCE, DESTINATION)

    print("DONE ✅ Open route_sampling_50m.html")
    dists = [haversine(sampled_route[i-1], sampled_route[i]) for i in range(1, len(sampled_route))]
    print(min(dists), max(dists))

