import json
from best_station_soc import step10_build_best_dataframe

# Load Step 9 output
with open("stations_with_total_energy.json", "r") as f:
    stations_data = json.load(f)

# Run Step 10
df = step10_build_best_dataframe(stations_data)

print("\n✅ STEP 10 COMPLETE: Best Candidate Per Station\n")
print(df.head(10))

# Save result
df.to_csv("step10_best_stations.csv", index=False)

print("\nSaved → step10_best_stations.csv")
