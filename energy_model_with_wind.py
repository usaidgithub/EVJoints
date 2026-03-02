import json
import math

INPUT_FILE = "sampled_with_elevation_wind.json"
OUTPUT_FILE = "battery_profile.json"

# -----------------------------
# Vehicle Parameters
# -----------------------------
MASS = 1800               # kg
G = 9.81
Crr = 0.01
Cd = 0.29
A = 2.2
RHO = 1.225

CAR_SPEED = 25           # m/s (~90 km/h)
BATTERY_CAPACITY_WH = 60000  # 60 kWh
BATTERY_CAPACITY_J = BATTERY_CAPACITY_WH * 3600

INITIAL_SOC = 1.0
MIN_SOC = 0.20

SEGMENT_DISTANCE = 50  # meters


# -----------------------------
# Bearing
# -----------------------------
def calculate_bearing(p1, p2):
    lat1, lon1 = map(math.radians, p1)
    lat2, lon2 = map(math.radians, p2)

    dlon = lon2 - lon1

    x = math.sin(dlon) * math.cos(lat2)
    y = math.cos(lat1) * math.sin(lat2) - \
        math.sin(lat1) * math.cos(lat2) * math.cos(dlon)

    bearing = math.degrees(math.atan2(x, y))
    return (bearing + 360) % 360


# -----------------------------
# Wind-adjusted drag
# -----------------------------
def drag_energy(wind_speed, wind_dir, bearing):
    theta = math.radians(bearing - wind_dir)
    wind_along = wind_speed * math.cos(theta)

    v_air = CAR_SPEED + wind_along
    if v_air < 0:
        v_air = 0

    Fd = 0.5 * RHO * Cd * A * v_air**2
    return Fd * SEGMENT_DISTANCE


# -----------------------------
# Main energy loop
# -----------------------------
def simulate_energy(points):

    soc = INITIAL_SOC
    battery_profile = []

    total_distance = 0

    for i in range(1, len(points)):

        p1 = points[i-1]
        p2 = points[i]

        bearing = calculate_bearing(
            (p1["lat"], p1["lng"]),
            (p2["lat"], p2["lng"])
        )

        # Slope energy
        elevation_gain = p2["elevation"] - p1["elevation"]
        slope_energy = MASS * G * elevation_gain

        # Rolling resistance
        rolling_force = MASS * G * Crr
        rolling_energy = rolling_force * SEGMENT_DISTANCE

        # Drag
        drag = drag_energy(
            p1["wind_speed"],
            p1["wind_direction"],
            bearing
        )

        total_energy = slope_energy + rolling_energy + drag

        # Reduce SOC
        soc -= total_energy / BATTERY_CAPACITY_J
        total_distance += SEGMENT_DISTANCE

        battery_profile.append({
            "distance_m": total_distance,
            "soc": soc
        })

        if soc <= MIN_SOC:
            print("⚡ Charging needed at",
                  round(total_distance/1000, 2), "km")
            break

    return battery_profile


# -----------------------------
# Run
# -----------------------------
if __name__ == "__main__":

    with open(INPUT_FILE, "r") as f:
        points = json.load(f)

    profile = simulate_energy(points)

    with open(OUTPUT_FILE, "w") as f:
        json.dump(profile, f, indent=2)

    print("✅ Battery profile saved →", OUTPUT_FILE)