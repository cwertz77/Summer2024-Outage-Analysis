import folium
import json
import pandas as pd


def make_style_function(county_colors_map):
    def style_function(feature):
        county_name = feature['properties']['name']
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

               
def get_quantitative_vulnerability(data_path):
    # entry is county_name : {date: [num people out]}
    counties_outages = {}
    with open(data_path, 'r') as f:
        csv = pd.read_csv(f)
        for i in range(len(csv)):
            row = csv.iloc[i]
            start_date = str(row['run_start_time']).split(' ')[0]
            if row['county'] not in counties_outages.keys():
                counties_outages[row['county']] = {start_date: [row['customers_out']]}
            else:
                county_dates = counties_outages[row['county']]
                if start_date not in county_dates.keys():
                    county_dates[start_date] = [row['customers_out']]
                else:
                    county_events = county_dates[start_date]
                    if row['customers_out'] not in county_events:
                        county_events.append(row['customers_out'])
                        counties_outages[row['county']][start_date] = county_events
    return counties_outages

def normalize_quantitative_vulnerabilities(data_path):
    outages = get_quantitative_vulnerability(data_path)
    county_totals = {}
    norm_county_totals = {}

    for county, dates in outages.items():
        print(f"County: {county}")
        county_totals[county] = 0
        for date, events in dates.items():
            print(f"  Date: {date}")
            for event in events:
                county_totals[county] += event
                print(f"    Customers out: {event}")         
    
    min_val = min(county_totals.values())
    max_val = max(county_totals.values())
    for key in county_totals.keys():
        norm_county_totals[key] = (county_totals[key] - min_val)/(max_val - min_val)
    return norm_county_totals


def get_normalized_nri_data(nri_path):
    # Read the CSV file into a DataFrame
    csv = pd.read_csv(nri_path)
    
    # Get the risk scores and their min and max values
    scores = csv['RISK_SCORE'].tolist()
    min_val = min(scores)
    max_val = max(scores)
    
    # Normalize the risk scores and add them to the dictionary
    county_scores = {}
    for i in range(len(csv)):
        county = csv.iloc[i]['COUNTY']
        risk_score = csv.iloc[i]['RISK_SCORE']
        normalized_score = (risk_score - min_val) / (max_val - min_val)
        county_scores[county] = normalized_score

    return county_scores


def svi_nri_quantitative_map(svi_path, nri_path, quantitative_data_path):
    geojson_data = {}
    with open('./illinois-with-county-boundaries_1097.geojson', 'r') as f:
        geojson_data = json.load(f)

    county_saturation = {}
    with open(svi_path, 'r') as f:
        csv = pd.read_csv(f)

    nri_data = get_normalized_nri_data(nri_path)
    quantitative_data = normalize_quantitative_vulnerabilities(quantitative_data_path)

    for i in range(len(csv)):
        row = csv.iloc[i]
        county_saturation[row['COUNTY']] = row['RPL_THEMES']
        county_name = row['COUNTY'].replace('County', '').strip()
        try:
            county_saturation[row['COUNTY']] = (row['RPL_THEMES'] + nri_data[county_name] + quantitative_data[county_name])/3
        except:
            print(f'does not exist {row['COUNTY']}')


    county_hex = {}
    for key in county_saturation.keys():
        county_hex[key.replace('County', '').strip()] = desaturate_color('#0000FF', county_saturation[key])
            
    '''for key in county_hex.keys():
        print(f'key is {key} and value is {county_hex[key]}')'''

    style_function = make_style_function(county_colors_map=county_hex)

    m = folium.Map(location=[40.754, -88.931], zoom_start=6)

    folium.GeoJson(
        geojson_data,
        style_function=style_function
    ).add_to(m)

    year = svi_path.split("_")[-1].replace('.csv', '')
    m.save(f"cdc_svi/svi_nri_quantitative_map_{year}.html")

def filter_svi_map(path):
    with open(path, 'r') as f:
        csv = pd.read_csv(f)
        df_filtered = csv[csv['ST_ABBR'] == 'IL']
        df_filtered.to_csv(path, index=False)
        
svi_nri_quantitative_map('./cdc_svi/svi_interactive_map_2022.csv',
                          './cdc_svi/NRI_Table_Counties_Illinois.csv', 
                          './outage_records/filtered_2022.csv')