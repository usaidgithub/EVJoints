import json
import math

# -------------------------------
# Haversine Distance (meters)
# -------------------------------
def haversine(p1, p2):
    lat1, lon1 = p1
    lat2, lon2 = p2

    R = 6371000  # Earth radius in meters

    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)

    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)

    a = (
        math.sin(dphi / 2) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    )

    return 2 * R * math.atan2(math.sqrt(a), math.sqrt(1 - a))


# -------------------------------
# Build Prefix Arrays
# -------------------------------
def build_prefix_arrays(points):
    n = len(points)

    cum_distance = [0.0] * n
    cum_ascent = [0.0] * n
    cum_descent = [0.0] * n

    for i in range(1, n):
        p1 = points[i - 1]
        p2 = points[i]

        # Distance between route points
        d = haversine((p1["lat"], p1["lng"]), (p2["lat"], p2["lng"]))

        # Elevation difference
        delta_h = p2["elevation"] - p1["elevation"]

        # Prefix distance
        cum_distance[i] = cum_distance[i - 1] + d

        # Prefix ascent/descent
        if delta_h > 0:
            cum_ascent[i] = cum_ascent[i - 1] + delta_h
            cum_descent[i] = cum_descent[i - 1]
        else:
            cum_ascent[i] = cum_ascent[i - 1]
            cum_descent[i] = cum_descent[i - 1] + abs(delta_h)

    return cum_distance, cum_ascent, cum_descent


# -------------------------------
# MAIN
# -------------------------------
if __name__ == "__main__":

    # Load sampled route points with elevation
    with open("sampled_with_elevation_50m.json") as f:
        points = json.load(f)

    # Build arrays
    cum_distance, cum_ascent, cum_descent = build_prefix_arrays(points)

    # Save prefix arrays to file
    prefix_data = {
        "cum_distance_m": cum_distance,
        "cum_ascent_m": cum_ascent,
        "cum_descent_m": cum_descent
    }

    with open("prefix_arrays.json", "w") as f:
        json.dump(prefix_data, f, indent=2)

    # -------------------------------
    # Verification Output
    # -------------------------------
    print("\n✅ PREFIX ARRAYS GENERATED SUCCESSFULLY\n")

    print("Total Route Distance (km):", cum_distance[-1] / 1000)
    print("Total Ascent (m):", cum_ascent[-1])
    print("Total Descent (m):", cum_descent[-1])

    print("\nSample Checkpoints:")
    for i in [100, 500, 1000, 2000]:
        if i < len(points):
            print(
                f"Index {i}:",
                f"Dist={cum_distance[i]/1000:.2f} km,",
                f"Ascent={cum_ascent[i]:.1f} m,",
                f"Descent={cum_descent[i]:.1f} m"
            )
