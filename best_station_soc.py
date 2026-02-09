import json

BATTERY_CAPACITY_KWH = 45.0

def choose_best_candidate(station):
    candidates = station["candidate_detours"]
    best = min(candidates, key=lambda c: c["total_energy_to_station_kwh"])
    return best


def compute_arrival_soc(total_energy_kwh):
    return round(100 - (total_energy_kwh / BATTERY_CAPACITY_KWH) * 100, 2)


def build_map_ready_output(stations, route_points):

    output = []

    for station in stations:

        best = choose_best_candidate(station)

        idx = best["route_idx"]
        detour_point = route_points[idx]

        total_energy = best["total_energy_to_station_kwh"]
        soc = compute_arrival_soc(total_energy)

        output.append({
            "station_id": station["id"],
            "name": station["name"],
            "station_lat": float(station["latitude"]),
            "station_lon": float(station["longitude"]),
            "best_route_idx": idx,
            "detour_lat": detour_point["lat"],
            "detour_lon": detour_point["lng"],
            "arrival_soc": soc,
            "energy_used_kwh": round(total_energy, 3)
        })

    return output


# -----------------------------
# RUN
# -----------------------------
with open("stations_with_total_energy.json") as f:
    stations = json.load(f)

with open("sampled_with_elevation_50m.json") as f:
    route_points = json.load(f)

map_data = build_map_ready_output(stations, route_points)

with open("map_visualization.json", "w") as f:
    json.dump(map_data, f, indent=2)

print("✅ Saved map_visualization.json")
