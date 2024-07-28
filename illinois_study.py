import pandas as pd
import numpy as np
import json
import geopandas as gpd
import plotly.express as px
import os


def generate_geojson(outage_data = './outage_records/processed_illinois2023.csv'):
    with open('illinois-with-county-boundaries_1097.geojson') as resp:
        state_outline = json.load(resp)
    csv = pd.read_csv(outage_data, index_col=0)
    # customers out per county total
    columns = ['County', 'Customers Lost']
    list_of_counties = list((csv['fips_code'].drop_duplicates()))
    list_of_counties=[str(int(i)) for i in list_of_counties]
    total_num_customers_out = list(csv.groupby(['county']).sum()['sum'])
    # electricity customers per county
    customers_per_county=pd.read_csv('MCC.csv')
    for k in range(len(customers_per_county)):
        if customers_per_county.loc[k,'County_FIPS'] not in list_of_counties:
            customers_per_county.drop(k,inplace=True)
    customers_per_county=list(customers_per_county['Customers'])
    normalized_outage=[int(b)/int(m) for b,m in zip(total_num_customers_out,customers_per_county)]

    # plot
    fig = px.choropleth(normalized_outage, geojson=state_outline,
                        locations=list_of_counties, color=normalized_outage,
                        labels={'color': 'average number of outages per customer (2023)'})
    fig.update_geos(lonaxis=dict(range=[-100, -85]), lataxis=dict(range=[30, 45])),
    fig.show()
    breakpoint()


def filter_repeats(outage_data, save_path):
    csv = pd.read_csv(outage_data, index_col=0)
    no_repeats_df = pd.DataFrame()
    start_time = ""
    for index in range(1, len(csv)):
        percent_done = index/len(csv)*100
        print(f'on iteration {index}; percent done: {percent_done}%')
        cols = ["county", "state", "customers_out"]
        if all(csv.iloc[index][col] == csv.iloc[index-1][col] for col in cols):
            if start_time == "":
                start_time = csv.iloc[index]["run_start_time"]
        else:
            last = str(csv.iloc[index-1]["run_start_time"]).split(":")
            minutes = int(last[1]) + 15
            end_time = f"{last[0]}:{minutes}:{last[2]}"

            cur_col = csv.iloc[index-1].copy()
            cur_col["run_start_time"] = start_time if start_time else cur_col["run_start_time"]
            cur_col["run_end_time"] = end_time
            no_repeats_df = pd.concat([no_repeats_df, cur_col.to_frame().T], ignore_index=True)

            start_time = ""
    
    with open(save_path, 'w+') as f:
        f.write(no_repeats_df.to_csv())
