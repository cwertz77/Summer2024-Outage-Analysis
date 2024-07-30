import folium
import json
import pandas as pd


def make_style_function(county_colors_map):
    def style_function(feature):
        county_name = feature['properties']['name']
        print(county_name)
        return {
            'fillColor': county_colors_map.get(county_name, '#000000'), 
            'color': '#000000',
            'weight': 5,  
            'dashArray': '5, 5',
            'fillOpacity': 0.7
        }
    return style_function

def desaturate_color(hex_code, percent):
    #hex to rgb
    r = int(hex_code[1:3], 16)
    g = int(hex_code[3:5], 16)
    b = int(hex_code[5:7], 16)

    #grayscale
    gray = int(r * 0.299 + g * 0.587 + b * 0.114)

    #desaturate
    r = int(r * percent + gray * (1 - percent))
    g = int(g * percent + gray * (1 - percent))
    b = int(b * percent + gray * (1 - percent))

    return f"#{r:02x}{g:02x}{b:02x}"

def get_normalized_nri_data(nri_path):
    with open(nri_path, 'r') as f:
        csv = pd.read_csv(f)

    max = 0
    for i in range(len(csv)):
        risk_val = csv.iloc[i]['RISK_SCORE']
        if risk_val > max:
            max = risk_val
        
    county_scores = {}
    for i in range(len(csv)):
        county_scores[csv.iloc[i]['COUNTY']] = csv.iloc[i]['RISK_SCORE'] / max

    return county_scores

def generate_svi_and_nri_map(svi_path, nri_path):
    geojson_data = {}
    with open('./illinois-with-county-boundaries_1097.geojson', 'r') as f:
        geojson_data = json.load(f)

    county_saturation = {}
    with open(svi_path, 'r') as f:
        csv = pd.read_csv(f)

    nri_data = get_normalized_nri_data(nri_path)
    for i in range(len(csv)):
        row = csv.iloc[i]
        county_saturation[row['COUNTY']] = row['RPL_THEMES']
        try:
            county_saturation[row['COUNTY']] = (row['RPL_THEMES'] + nri_data[row['COUNTY'].replace('County', '').strip()])/2
        except:
            print(f'does not exist {row['COUNTY']}')


    county_hex = {}
    for key in county_saturation.keys():
        county_hex[key.replace('County', '').strip()] = desaturate_color('#0000FF', county_saturation[key])
            
    for key in county_hex.keys():
        print(f'key is {key} and value is {county_hex[key]}')

    style_function = make_style_function(county_colors_map=county_hex)

    m = folium.Map(location=[40.754, -88.931], zoom_start=6)

    folium.GeoJson(
        geojson_data,
        style_function=style_function
    ).add_to(m)

    year = svi_path.split("_")[-1].replace('.csv', '')
    m.save(f"cdc_svi/svi_and_nri_map_{year}.html")

