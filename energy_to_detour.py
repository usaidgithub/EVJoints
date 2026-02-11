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
regen_eff = 0.40  # capped

# Flat road base Wh/km
base_Wh_per_km = 30200 / 280  # ≈108 Wh/km


# -----------------------------
# LOAD PREFIX ARRAYS
# -----------------------------
with open("prefix_arrays.json") as f:
    prefix = json.load(f)

cum_distance = prefix["cum_distance_m"]
cum_ascent = prefix["cum_ascent_m"]
cum_descent = prefix["cum_descent_m"]


# -----------------------------
# LOAD STATIONS WITH CANDIDATES
# -----------------------------
with open("stations_with_candidates.json") as f:
    stations = json.load(f)


# -----------------------------
# ENERGY FUNCTION
# -----------------------------
def energy_to_index(i):
    """Energy from source → route index i"""

    distance_km = cum_distance[i] / 1000
    ascent_m = cum_ascent[i]
    descent_m = cum_descent[i]

    # Flat energy
    E_flat = distance_km * base_Wh_per_km / 1000

    # Climb energy
    E_climb = (mass * g * ascent_m) / 3.6e6

    # Regen energy (capped)
    E_regen = (mass * g * descent_m) / 3.6e6 * regen_eff

    # Total energy
    E_route = E_flat + E_climb - E_regen

    return round(E_route, 4)


# -----------------------------
# STEP 8: ENERGY + DISTANCE FOR EACH DETOUR POINT
# -----------------------------
for station in stations:

    for cand in station["candidate_detours"]:
        idx = cand["route_idx"]

        # -----------------------------
        # DISTANCE FROM PREFIX ARRAY
        # -----------------------------
        source_to_detour_km = cum_distance[idx] / 1000

        # Add it explicitly
        cand["source_to_detour_km"] = round(source_to_detour_km, 3)

        # Detour → station distance already exists
        detour_to_station_km = cand.get("detour_to_station_km", cand.get("distance_km", 0))
        cand["detour_to_station_km"] = round(detour_to_station_km, 3)

        # Total travel distance
        cand["total_distance_km"] = round(
            source_to_detour_km + detour_to_station_km, 3
        )

        # -----------------------------
        # ENERGY COMPUTATION
        # -----------------------------
        cand["energy_from_source_kwh"] = energy_to_index(idx)

        # Battery used %
        used_pct = (cand["energy_from_source_kwh"] / BATTERY_KWH) * 100
        cand["battery_used_pct"] = round(used_pct, 2)

        # Remaining SOC
        cand["soc_remaining_pct"] = round(100 - used_pct, 2)


# -----------------------------
# SAVE OUTPUT
# -----------------------------
with open("stations_with_energy.json", "w", encoding="utf-8") as f:
    json.dump(stations, f, indent=2)

print("✅ STEP 8 COMPLETE (Distance + Energy Included)")
print("Saved → stations_with_energy.json")


# -----------------------------
# VERIFICATION PRINT
# -----------------------------
print("\n🔍 Sample Verification (First Station):")
s = stations[0]

print("Station:", s["name"])
for c in s["candidate_detours"]:
    print(
        "Idx:", c["route_idx"],
        "| Dist Source→Detour:", c["source_to_detour_km"], "km",
        "| Detour→Station:", c["detour_to_station_km"], "km",
        "| Total:", c["total_distance_km"], "km",
        "| Energy:", c["energy_from_source_kwh"], "kWh",
        "| SOC Remaining:", c["soc_remaining_pct"], "%"
    )
