import json
import random
from scipy.spatial import KDTree

# -----------------------------
# LOAD ROUTE POINTS
# -----------------------------
with open("sampled_with_elevation_50m.json") as f:
    points = json.load(f)

# Extract lat/lon only
coords = [(p["lat"], p["lng"]) for p in points]

# -----------------------------
# BUILD KD-TREE
# -----------------------------
route_kdtree = KDTree(coords)

print("KD-Tree built successfully ✅")
print("Total route points:", len(coords))
# Test with slightly offset points
print("\n🔍 Offset-point test:")
lat, lon = coords[1000]
offset_point = (lat + 0.0003, lon + 0.0003)

dist, idx = route_kdtree.query(offset_point)

print("Offset query → nearest index:", idx)
print("Matched route point:", coords[idx])


# -----------------------------
# VERIFICATION TESTS
# -----------------------------
def test_random_queries(k=5):
    print("\n🔍 KD-Tree sanity check:")
    for _ in range(k):
        idx = random.randint(0, len(coords) - 1)
        query_point = coords[idx]

        dist, nearest_idx = route_kdtree.query(query_point)

        print(
            f"Query idx={idx} → "
            f"Nearest idx={nearest_idx}, "
            f"Distance={dist:.8f}"
        )

test_random_queries()
