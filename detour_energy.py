import json
import math

# -----------------------------
# VEHICLE CONSTANTS (Same as Step 8)
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
    R = 6371  # Earth radius km

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
# STEP 9 CORE FUNCTION
# -----------------------------
def estimate_detour_energy(route_point, station):

    twist_factor = 1.3

    # Route point
    P_lat = route_point["lat"]
    P_lon = route_point["lng"]
    P_elev = route_point["elevation"]

    # Station lat/lon
    S_lat = float(station["latitude"])
    S_lon = float(station["longitude"])

    # ✅ FIX: Safe station elevation
    raw_elev = station.get("elevation", 0)

    if raw_elev in ["", None]:
        S_elev = P_elev   # best assumption
    else:
        S_elev = float(raw_elev)

    # -----------------------------
    # Distance Approximation
    # -----------------------------
    straight_km = haversine(P_lat, P_lon, S_lat, S_lon)
    detour_km = straight_km * twist_factor

    # -----------------------------
    # Elevation Delta
    # -----------------------------
    delta_elev = S_elev - P_elev

    ascent_m = 0
    descent_m = 0

    if delta_elev > 0:
        ascent_m = delta_elev * 1.15
    elif delta_elev < 0:
        descent_m = abs(delta_elev) * 0.85

    # -----------------------------
    # Energy Computation
    # -----------------------------
    E_flat = (detour_km * base_Wh_per_km) / 1000
    E_climb = (mass * g * ascent_m) / 3.6e6
    E_regen = (mass * g * descent_m) / 3.6e6 * regen_eff

    E_detour = E_flat + E_climb - E_regen

    return round(E_detour, 5)



# -----------------------------
# LOAD ROUTE POINTS WITH ELEVATION
# -----------------------------
with open("sampled_with_elevation_50m.json") as f:
    route_points = json.load(f)

# Each route point should look like:
# { "lat": ..., "lon": ..., "elev": ... }

# -----------------------------
# LOAD STATIONS WITH ENERGY (Step 8 Output)
# -----------------------------
with open("stations_with_energy.json") as f:
    stations = json.load(f)


# -----------------------------
# STEP 9: APPLY DETOUR ENERGY TO EACH CANDIDATE
# -----------------------------
for station in stations:

    for cand in station["candidate_detours"]:

        idx = cand["route_idx"]

        # Route point object
        route_point = route_points[idx]

        # Estimate detour energy
        detour_energy = estimate_detour_energy(route_point, station)

        # Save correction
        cand["detour_energy_kwh"] = detour_energy

        # Total energy to reach station
        total_energy = cand["energy_from_source_kwh"] + detour_energy
        cand["total_energy_to_station_kwh"] = round(total_energy, 4)

        # SOC remaining at station
        used_pct = (total_energy / BATTERY_KWH) * 100
        cand["soc_remaining_at_station_pct"] = round(100 - used_pct, 2)


# -----------------------------
# SAVE OUTPUT
# -----------------------------
with open("stations_with_total_energy.json", "w", encoding="utf-8") as f:
    json.dump(stations, f, indent=2)

print("✅ STEP 9 COMPLETE")
print("Saved → stations_with_total_energy.json")


# -----------------------------
# VERIFICATION PRINT
# -----------------------------
print("\n🔍 Sample Check (First Station):")
s = stations[0]

for c in s["candidate_detours"][:3]:
    print(
        "Idx:", c["route_idx"],
        "| Detour Energy:", c["detour_energy_kwh"], "kWh",
        "| Total:", c["total_energy_to_station_kwh"], "kWh",
        "| SOC at Station:", c["soc_remaining_at_station_pct"], "%"
    )
