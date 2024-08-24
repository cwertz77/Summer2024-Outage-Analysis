from pandas import *
import json

days = {}
year = "2022"
eagle = read_csv(f'processed_illinois{year}.csv')
major = read_csv(f"{year}_illinois.csv")

dates = eagle["run_start_time"].tolist()
counties = eagle["county"].tolist()
disturbances = major["Event date and time"].tolist()

for disturbance in disturbances:
    affected = []
    for i in range(len(dates)):
        if disturbance[0:2] == dates[i][5:7] and disturbance[3:5] == dates[i][8:10] and counties[i] not in affected:
            affected.append(counties[i])

    print(affected)
    days[disturbance] = affected


json_object = json.dumps(days, indent=2)
with open(f"{year}_overlap.json", "w") as outfile:
    outfile.write(json_object)