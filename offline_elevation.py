import json
import elevation
import rasterio


# -----------------------------
# STEP 1: Download DEM
# -----------------------------
def download_dem(route_points, output_file="dem.tif"):

    lats = [p[0] for p in route_points]
    lngs = [p[1] for p in route_points]

    min_lat, max_lat = min(lats), max(lats)
    min_lon, max_lon = min(lngs), max(lngs)

    print("📦 Downloading DEM...")

    elevation.clip(
        bounds=(min_lon, min_lat, max_lon, max_lat),
        output=output_file
    )

    print("✅ DEM downloaded:", output_file)


# -----------------------------
# STEP 2: Query Elevation
# -----------------------------
def get_elevation(lat, lon, dataset):

    row, col = dataset.index(lon, lat)
    value = dataset.read(1)[row, col]

    return float(value)


# -----------------------------
# STEP 3: Add Elevation
# -----------------------------
def add_elevation_offline(route_points, dem_file="dem.tif"):

    print("🌍 Loading DEM...")

    enriched = []

    with rasterio.open(dem_file) as dataset:

        for i, point in enumerate(route_points):

            lat = point[0]
            lon = point[1]

            elev = get_elevation(lat, lon, dataset)

            enriched.append({
                "lat": lat,
                "lng": lon,
                "elevation": elev
            })

            if i % 200 == 0:
                print(f"✅ {i}/{len(route_points)} done")

    return enriched


# -----------------------------
# RUN PIPELINE
# -----------------------------
if __name__ == "__main__":

    with open("sampled_route_50m.json") as f:
        route_points = json.load(f)

    download_dem(route_points)

    final_points = add_elevation_offline(route_points)

    with open("sampled_with_elevation_offline.json", "w") as f:
        json.dump(final_points, f, indent=2)

    print("✅ Saved: sampled_with_elevation_offline.json")
