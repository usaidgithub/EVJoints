import json
import requests
import time
from config import GOOGLE_MAPS_API_KEY

# ==============================
# CONFIG
# ==============================

ELEVATION_URL = "https://maps.googleapis.com/maps/api/elevation/json"

INPUT_FILE = "sampled_route_50m.json"
OUTPUT_FILE = "sampled_with_elevation_50m.json"

BATCH_SIZE = 400   # Google allows max 512 locations per request
SLEEP_TIME = 0.25  # Rate-limit safety


# ==============================
# STEP 1: Load Sampled Route
# ==============================

def load_sampled_points(filename):
    with open(filename, "r") as f:
        points = json.load(f)

    print(f"✅ Loaded {len(points)} sampled points from {filename}")
    return points


# ==============================
# STEP 2: Fetch Elevation Batch
# ==============================

def fetch_elevation_batch(batch_points):
    """
    Calls Google Elevation API for one batch of points.
    """

    locations = "|".join(
        f"{lat},{lng}" for lat, lng in batch_points
    )

    params = {
        "locations": locations,
        "key": GOOGLE_MAPS_API_KEY
    }

    response = requests.get(ELEVATION_URL, params=params)
    data = response.json()

    if data["status"] != "OK":
        raise Exception(f"❌ Elevation API Error: {data}")

    return data["results"]


# ==============================
# STEP 3: Elevation Pipeline
# ==============================

def enrich_with_elevation(points):
    enriched = []

    total_batches = (len(points) // BATCH_SIZE) + 1
    batch_num = 1

    for i in range(0, len(points), BATCH_SIZE):

        batch = points[i:i + BATCH_SIZE]

        print(f"\n🌍 Fetching batch {batch_num}/{total_batches}...")
        results = fetch_elevation_batch(batch)

        for pt, res in zip(batch, results):
            enriched.append({
                "lat": pt[0],
                "lng": pt[1],
                "elevation": res["elevation"]
            })

        print(f"✅ Batch {batch_num} done ({len(batch)} points)")

        batch_num += 1
        time.sleep(SLEEP_TIME)

    print("\n🎉 Elevation fetched for all points!")
    return enriched


# ==============================
# STEP 4: Save Output JSON
# ==============================

def save_output(data, filename):
    with open(filename, "w") as f:
        json.dump(data, f, indent=2)

    print(f"\n✅ Saved elevation-enriched route → {filename}")


# ==============================
# MAIN
# ==============================

if __name__ == "__main__":

    print("\n🚀 STEP 1: Loading sampled route points...")
    sampled_points = load_sampled_points(INPUT_FILE)

    print("\n🚀 STEP 2: Fetching elevations from Google API...")
    enriched_points = enrich_with_elevation(sampled_points)

    print("\n🚀 STEP 3: Saving final JSON...")
    save_output(enriched_points, OUTPUT_FILE)

    print("\n✅ DONE! Now you have:")
    print("   sampled_with_elevation_50m.json")
