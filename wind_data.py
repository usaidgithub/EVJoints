import json
import requests
from config import OPENWEATHER_API_KEY

INPUT_FILE = "sampled_with_elevation_50m.json"
OUTPUT_FILE = "sampled_with_elevation_wind.json"

WEATHER_URL = "https://api.openweathermap.org/data/2.5/weather"


# -----------------------------
# Load elevation data
# -----------------------------
def load_data(filename):
    with open(filename, "r") as f:
        return json.load(f)


# -----------------------------
# Fetch wind at midpoint
# -----------------------------
def fetch_wind(lat, lon):
    params = {
        "lat": lat,
        "lon": lon,
        "appid": OPENWEATHER_API_KEY,
        "units": "metric"
    }

    res = requests.get(WEATHER_URL, params=params)
    data = res.json()

    wind_speed = data["wind"]["speed"]   # m/s
    wind_deg = data["wind"]["deg"]       # direction

    print(f"🌬 Wind speed: {wind_speed} m/s")
    print(f"🌬 Wind direction: {wind_deg}°")

    return wind_speed, wind_deg


# -----------------------------
# Attach wind to all points
# -----------------------------
def attach_wind(points, wind_speed, wind_deg):

    enriched = []

    for pt in points:
        pt_copy = pt.copy()
        pt_copy["wind_speed"] = wind_speed
        pt_copy["wind_direction"] = wind_deg
        enriched.append(pt_copy)

    return enriched


# -----------------------------
# Save
# -----------------------------
def save_output(data, filename):
    with open(filename, "w") as f:
        json.dump(data, f, indent=2)

    print(f"✅ Wind-enriched data saved → {filename}")


# -----------------------------
# MAIN
# -----------------------------
if __name__ == "__main__":

    print("Loading elevation route...")
    points = load_data(INPUT_FILE)

    midpoint = points[len(points)//2]
    mid_lat = midpoint["lat"]
    mid_lon = midpoint["lng"]

    print("Fetching wind at route midpoint...")
    wind_speed, wind_deg = fetch_wind(mid_lat, mid_lon)

    enriched = attach_wind(points, wind_speed, wind_deg)

    save_output(enriched, OUTPUT_FILE)

    print("DONE ✅")