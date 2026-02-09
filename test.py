import json

with open("stations_with_total_energy.json") as f:
    data = json.load(f)

count = 0
for s in data:
    for c in s["candidate_detours"]:
        if c["route_idx"] == 0:
            count += 1

print("Stations containing route_idx=0:", count)
