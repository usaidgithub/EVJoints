import requests
import polyline
import json
from geopy.distance import geodesic
from config import GOOGLE_MAPS_API_KEY
# ==============================
# ✅ CONFIG
# ==============================


SOURCE = (19.110353796653445, 72.9256064096532)
DESTINATION = (8.09123062909898, 77.54926521450045)

STEP_DISTANCE_METERS = 50

OUTPUT_FILE = "sampled_route_50m.json"


# ==============================
# ✅ Fetch FULL Route Geometry
# ==============================

def fetch_full_route_points(source, destination):
    """
    Fetches the complete road-following route geometry
    using step-by-step polyline decoding.
    """

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
        raise Exception("Directions API Error:", data)

    steps = data["routes"][0]["legs"][0]["steps"]

    full_route_points = []

    print("✅ Extracting road geometry from steps...")

    for step in steps:
        step_polyline = step["polyline"]["points"]

        # Decode step polyline into full coordinates
        decoded_points = polyline.decode(step_polyline)

        # Append to full route
        full_route_points.extend(decoded_points)

    print("✅ Total full route points:", len(full_route_points))

    return full_route_points


# ==============================
# ✅ Accurate Sampling Every 50m
# ==============================

def sample_route_exact(route_points, step_m=50):
    """
    Samples points every `step_m` meters
    along the real curved road geometry.
    """

    sampled = [route_points[0]]
    accumulated_distance = 0

    for i in range(1, len(route_points)):
        prev_point = route_points[i - 1]
        curr_point = route_points[i]

        segment_distance = geodesic(prev_point, curr_point).meters

        accumulated_distance += segment_distance

        if accumulated_distance >= step_m:
            sampled.append(curr_point)
            accumulated_distance = 0

    # Ensure destination included
    if sampled[-1] != route_points[-1]:
        sampled.append(route_points[-1])

    print("✅ Sampled points generated:", len(sampled))

    return sampled


# ==============================
# ✅ Save JSON
# ==============================

def save_sampled_route(sampled_points, filename):
    """
    Saves sampled route into JSON file.
    """

    with open(filename, "w") as f:
        json.dump(sampled_points, f, indent=2)

    print(f"✅ Sampled route saved as: {filename}")


# ==============================
# ✅ MAIN
# ==============================

if __name__ == "__main__":
    print("\n🚀 Fetching full road-following route...\n")

    full_route = fetch_full_route_points(SOURCE, DESTINATION)

    print("\n🚀 Sampling route every 50 meters...\n")

    sampled_route = sample_route_exact(full_route, STEP_DISTANCE_METERS)

    print("\n🚀 Saving sampled route JSON...\n")

    save_sampled_route(sampled_route, OUTPUT_FILE)

    print("\n🎉 Done! Now this sampled route will follow roads perfectly.\n")
