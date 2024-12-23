import pandas as pd
import json
from metric_calculations import get_quantitative_vulnerability
from dateutil import rrule
from datetime import datetime
import numpy as np


def convert_to_json_serializable(value):
    if pd.isna(value):
        return None
    elif isinstance(value, pd.Timestamp):
        return value.strftime('%Y-%m-%d %H:%M:%S')
    elif isinstance(value, (np.integer, np.int64, int)):
        return int(value)
    elif isinstance(value, (np.floating, np.float64, float)):
        return float(value)
    elif isinstance(value, (datetime, pd.Timestamp)):
        return value.isoformat()
    else:
        return str(value)


def combine_weather_and_eagle_I_data(weather_path, eagle_I_path, save_path, year):
    weather_csv = pd.read_csv(weather_path)
    eagle_I_data = get_quantitative_vulnerability(eagle_I_path)
    start_date, end_date = f"{year}0101", f"{year}1231"

    root_keys = {}
    for dt in rrule.rrule(rrule.DAILY,
                          dtstart=datetime.strptime(start_date, '%Y%m%d'),
                          until=datetime.strptime(end_date, '%Y%m%d')):
        date = dt.strftime('%m/%d/%Y')
        root_keys[date] = {}

    for row in range(len(weather_csv)):
        date = weather_csv.iloc[row]["BEGIN_DATE"]
        write_out = {}
        for col in weather_csv.columns:
            write_out[col] = convert_to_json_serializable(weather_csv.iloc[row][col])

        if "weather_data" not in root_keys[date]:
            root_keys[date]["weather_data"] = [write_out]
        else:
            root_keys[date]["weather_data"].append(write_out)

    for dates in eagle_I_data.values():
        num_events = 0
        for cur_date, events in dates.items():
            parts = cur_date.split("-")
            cur_date = f"{parts[1]}/{parts[2]}/{parts[0]}"
            for event in events:
                total_duration = event[1]
                if total_duration > 7200:
                    num_events += 1
            root_keys[cur_date]["num_major_eagle_I_events"] = num_events

    print(f"finished processing {year} data")

    with open(save_path, "w") as out_file:
        json.dump(root_keys, out_file, indent=3)


'''for i in range(2015, 2024):
    combine_weather_and_eagle_I_data(
        f"./illinois_weather_data/weather_{i}.csv", 
        f"./outage_records/filtered_{i}.csv", 
        f"./weather_data_with_eagle_I/{i}.json",
        i)'''


def find_wind_mph(weather_path, date, county):
    weather_csv = pd.read_csv(weather_path)
    for i in range(len(weather_csv)):
        row = weather_csv.iloc[i]
        if row["BEGIN_DATE"] == date and row["CZ_NAME_STR"].replace("(ZONE)", "").replace("CO.",
                                                                                          "").strip().lower() == county.lower():
            return row["MAGNITUDE"]


#outputs file with counties and number of people out and event magnitude (mph for wind storms)
def combine_weather_data(weather_path, outage_record_path, save_path, year):
    county_metrics = pd.DataFrame(
        columns=["date", "county", "max_num_people_out", "duration", "customer_mins", "wind_speed_mph"])
    eagle_I_data = get_quantitative_vulnerability(outage_record_path)

    for county, dates in eagle_I_data.items():
        for cur_date, events in dates.items():
            parts = cur_date.split("-")
            if int(parts[0]) != year:
                break
            cur_date = f"{parts[1]}/{parts[2]}/{parts[0]}"
            max_people_out = max([event[0] for event in events])
            duration = sum(event[1] for event in events)
            customer_mins = sum(event[1] * event[0] for event in events)
            wind_speed = find_wind_mph(weather_path, cur_date, county)
            print(f"wind speed {wind_speed}")
            if wind_speed:
                row_df = pd.DataFrame([[cur_date, county, max_people_out, duration, customer_mins, wind_speed]],
                                      columns=["date", "county", "max_num_people_out", "duration", "customer_mins",
                                               "wind_speed_mph"])
                county_metrics = pd.concat([county_metrics, row_df], ignore_index=True)

    with open(save_path, "w") as f:
        f.write(county_metrics.to_csv())


for i in range(2020, 2024):
    combine_weather_data(f"./illinois_weather_data/wind_events_{i}.csv", f"./outage_records/filtered_{i}.csv",
                         f"./wind_and_eagle_I_csvs/{i}.csv", i)


def combine_EIA_with_wind(weather_path, outage_record_path, save_path, year):
    county_metrics = pd.DataFrame(
        columns=["date", "county", "max_num_people_out", "duration", "customer_mins", "wind_speed_mph"])

    breakpoint()
