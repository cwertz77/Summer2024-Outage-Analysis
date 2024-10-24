import pandas as pd
year = "2023"

weather = pd.read_csv(f"filtered_weather{year}.csv")
weather_data = [list(row) for row in weather.values]
eagle = pd.read_csv(f"sortedEAGLE{year}.csv")
eagle = [list(row) for row in eagle.values]
final_json = {}

for event in weather_data:
    out = []
    if "kts." in str(event[6]):
        for time in eagle:
            if "CO." in event[1]:
                if event[1][0:-4].lower() == time[2].lower():
                    if float(event[3][0:2]) == float(time[5][5:7]):

                        if float(event[3][3:5]) <= float(time[5][8:10]) <= float(event[30][3:5]):

                            out.append(time)
                            continue
                        elif float(event[3][0:2]) < float(time[5][8:10]) and float(time[5][5:7]) > float(event[30][3:5]):
                            break


            elif "(ZONE)" in event[1]:
                if event[1][0:-7].lower() == time[2].lower():
                    if float(event[3][0:2]) == float(time[5][5:7]):

                        if float(event[3][3:5]) < float(time[5][8:10]) < float(event[30][3:5]):

                            out.append(time)
                            continue
                        elif float(event[3][0:2]) < float(time[5][8:10]) and float(time[5][5:7]) > float(event[30][3:5]):
                            break


    final_json[event[3] + " " + str(event[5]) + " " + str(event[6]) + " " + str(event[1])] = out

import json

with open(f"weather_to_outage{year}.json", "w") as outfile:
    json.dump(final_json, outfile)