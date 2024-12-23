import pandas as pd
import numpy as np
import json
import geopandas as gpd
import plotly.express as px
import os


def generate_geojson(outage_data = './outage_records/processed_illinois2023.csv', geojson='illinois-with-county-boundaries_1097.geojson'):
    with open(geojson) as resp:
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

