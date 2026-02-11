import json
import math

# -----------------------------
# VEHICLE CONSTANTS
# -----------------------------
BATTERY_KWH = 45

vehicle_mass = 2000
passenger_mass = 120
luggage_mass = 70

mass = vehicle_mass + passenger_mass + luggage_mass

g = 9.81
regen_eff = 0.40

base_Wh_per_km = 30200 / 280  # ≈108 Wh/km


# -----------------------------
# HAVERSINE DISTANCE FUNCTION
# -----------------------------
def haversine(lat1, lon1, lat2, lon2):
    """
    Great-circle distance between two GPS points (km)
    """
    R = 6371

    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)

    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(dlon / 2) ** 2
    )

    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c


# -----------------------------
# STEP 1: BUILD CUMULATIVE ROUTE DISTANCE
# -----------------------------
def compute_cumulative_distances(route_points):
    """
    Returns array where cumulative[i] = distance from source → route point i
    """
    cumulative = [0.0]

    for i in range(1, len(route_points)):
        prev = route_points[i - 1]
        curr = route_points[i]

        seg_km = haversine(
            prev["lat"], prev["lng"],
            curr["lat"], curr["lng"]
        )

        cumulative.append(cumulative[-1] + seg_km)

    return cumulative


# -----------------------------
# STEP 2: DETOUR ENERGY FUNCTION
# -----------------------------
def estimate_detour_energy(route_point, station):

    twist_factor = 1.3

    P_lat = route_point["lat"]
    P_lon = route_point["lng"]
    P_elev = route_point["elevation"]

    S_lat = float(station["latitude"])
    S_lon = float(station["longitude"])

    raw_elev = station.get("elevation", 0)

    if raw_elev in ["", None]:
        S_elev = P_elev
    else:
        S_elev = float(raw_elev)

    # Straight line distance
    straight_km = haversine(P_lat, P_lon, S_lat, S_lon)

    # Approximate detour road twist
    detour_km = straight_km * twist_factor

    # Elevation delta
    delta_elev = S_elev - P_elev

    ascent_m = 0
    descent_m = 0

    if delta_elev > 0:
        ascent_m = delta_elev * 1.15
    elif delta_elev < 0:
        descent_m = abs(delta_elev) * 0.85

    # Energy calculation
    E_flat = (detour_km * base_Wh_per_km) / 1000
    E_climb = (mass * g * ascent_m) / 3.6e6
    E_regen = (mass * g * descent_m) / 3.6e6 * regen_eff

    E_detour = E_flat + E_climb - E_regen
    return round(max(E_detour, 0), 5)


# -----------------------------
# LOAD ROUTE + STATIONS
# -----------------------------
with open("sampled_with_elevation_50m.json") as f:
    route_points = json.load(f)

with open("stations_with_energy.json") as f:
    stations = json.load(f)


# -----------------------------
# BUILD SOURCE → ROUTE DISTANCES
# -----------------------------
print("⏳ Computing cumulative route distances...")
cumulative_km = compute_cumulative_distances(route_points)
print("✅ Done.")


# -----------------------------
# APPLY TO EACH DETOUR CANDIDATE
# -----------------------------
for station in stations:

    for cand in station["candidate_detours"]:

        idx = cand["route_idx"]
        route_point = route_points[idx]

        # ✅ Accurate distance from source → detour point
        source_to_detour = cumulative_km[idx]
        cand["source_to_detour_km"] = round(source_to_detour, 3)

        # Total distance = route travel + detour travel
        cand["total_distance_km"] = round(
            cand["source_to_detour_km"] + cand["detour_to_station_km"], 3
        )

        # Detour energy
        detour_energy = estimate_detour_energy(route_point, station)
        cand["detour_energy_kwh"] = detour_energy

        # Total energy
        total_energy = cand["energy_from_source_kwh"] + detour_energy
        cand["total_energy_to_station_kwh"] = round(total_energy, 4)

        # SOC remaining
        used_pct = (total_energy / BATTERY_KWH) * 100
        cand["soc_remaining_at_station_pct"] = round(100 - used_pct, 2)


# -----------------------------
# SAVE FINAL OUTPUT
# -----------------------------
with open("stations_with_total_energy.json", "w", encoding="utf-8") as f:
    json.dump(stations, f, indent=2)

print("\n✅ COMPLETE")
print("Saved → stations_with_total_energy.json")


# -----------------------------
# SAMPLE CHECK
# -----------------------------
print("\n🔍 Sample Check (First Station):")

for c in stations[0]["candidate_detours"][:3]:
    print(
        "Idx:", c["route_idx"],
        "| Source→Detour:", c["source_to_detour_km"], "km",
        "| Detour:", c["detour_to_station_km"], "km",
        "| Total:", c["total_distance_km"], "km",
        "| SOC:", c["soc_remaining_at_station_pct"], "%"
    )
