import json
import math

# Reuse haversine
def haversine(p1, p2):
    lat1, lon1 = p1
    lat2, lon2 = p2

    R = 6371000
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)

    a = math.sin(dphi / 2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2)**2
    return 2 * R * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def build_prefix_arrays(points):
    n = len(points)

    cum_distance = [0.0] * n
    cum_ascent = [0.0] * n
    cum_descent = [0.0] * n

    for i in range(1, n):
        p1 = points[i - 1]
        p2 = points[i]

        d = haversine((p1["lat"], p1["lng"]), (p2["lat"], p2["lng"]))
        delta_h = p2["elevation"] - p1["elevation"]

        cum_distance[i] = cum_distance[i - 1] + d

        if delta_h > 0:
            cum_ascent[i] = cum_ascent[i - 1] + delta_h
            cum_descent[i] = cum_descent[i - 1]
        else:
            cum_ascent[i] = cum_ascent[i - 1]
            cum_descent[i] = cum_descent[i - 1] + abs(delta_h)

    return cum_distance, cum_ascent, cum_descent

with open("sampled_with_elevation_50m.json") as f:
    points = json.load(f)

cum_distance, cum_ascent, cum_descent = build_prefix_arrays(points)
print("Total distance (km):", cum_distance[-1] / 1000)
print("Total ascent (m):", cum_ascent[-1])
print("Total descent (m):", cum_descent[-1])
for i in [100, 500, 1000, 2000]:
    print(
        i,
        cum_distance[i] / 1000,
        cum_ascent[i],
        cum_descent[i]
    )
