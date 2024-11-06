import folium
import json
import pandas as pd
import json
from datetime import datetime


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


def desaturate_color(percent):
    percent = max(0, min(percent, 1))
    g = int(255 * (1 - percent))
    b = int(255 * percent)

    g_hex = f"{g:02x}"
    b_hex = f"{b:02x}"

    return f"#00{g_hex}{b_hex}"


def get_time_diff(row):
    start_time = datetime.strptime(row['run_start_time'], '%Y-%m-%d %H:%M:%S')
    end_time = datetime.strptime(row['run_end_time'], '%Y-%m-%d %H:%M:%S')
    time_diff = abs(end_time - start_time).total_seconds() / 60
    return time_diff


def get_quantitative_vulnerability(data_path):
    # entry is county_name : {date: [ (num people out, duration in minutes) ]}
    counties_outages = {}
    with open(data_path, 'r') as f:
        csv = pd.read_csv(f)
        for i in range(len(csv)):
            row = csv.iloc[i]
            duration = get_time_diff(row)
            start_date = str(row['run_start_time']).split(' ')[0]
            if row['county'] not in counties_outages.keys():
                counties_outages[row['county']] = {start_date: [(row['customers_out'], duration)]}
            else:
                county_dates = counties_outages[row['county']]
                if start_date not in county_dates.keys():
                    county_dates[start_date] = [(row['customers_out'], duration)]
                else:
                    county_events = county_dates[start_date]
                    customers_out = row['customers_out']
                    # check if row['customers_out'] is not in the first element of any tuple in county_events
                    found = False
                    for index, (out, dur) in enumerate(county_events):
                        if out == customers_out:
                            county_events[index] = (customers_out, dur + duration)
                            found = True
                            break
                    if not found:
                        county_events.append((customers_out, duration))

    return counties_outages


def search_for_equals(sorted_list, index):
    if index < 0 or index >= len(sorted_list):
        return 0, 0
    value = sorted_list[index]
    left_count, right_count = 0, 0

    left_index = index - 1
    while left_index >= 0 and sorted_list[left_index] == value:
        left_count += 1
        left_index -= 1

    right_index = index + 1
    while right_index < len(sorted_list) and sorted_list[right_index] == value:
        right_count += 1
        right_index += 1

    return left_count, right_count


def get_percentile_sorted_data(data_map):
    sorted_data = [(key, value) for key, value in data_map.items()]
    sorted_data = sorted(sorted_data, key=lambda x: x[1])

    total = len(sorted_data)
    percentile_ranks = {}
    values = [val[1] for val in sorted_data]

    for i in range(total):
        left_equal, right_equal = search_for_equals(values, i)  # returns a tuple that's unpacked
        num_equal = left_equal + right_equal + 1
        percentile_rank = ((i - left_equal) + 0.5 * num_equal) / total
        county = sorted_data[i][0]
        percentile_ranks[county] = percentile_rank

    return percentile_ranks


def get_num_customers_affected(county_name):
    data = pd.read_csv("./county_to_fips.csv")
    for row in range(len(data)):
        if data.iloc[row]["county"] == county_name:
            fips_code = data.iloc[row]["fips_code"]
            break
    cust_out_data = pd.read_csv("./mcc.csv")
    for row in range(len(cust_out_data)):
        if int(cust_out_data.iloc[row]["County_FIPS"]) == fips_code:
            return cust_out_data.iloc[row]["Customers"]


def get_svi(county_name, year):
    svi_csv = pd.read_csv(f"./plots_and_metric_data/svi_interactive_map_{year}.csv")
    for row in range(len(svi_csv)):
        if svi_csv.iloc[row]["COUNTY"].replace("County", "").strip() == county_name:
            return svi_csv.iloc[row]["RPL_THEMES"]


def normalize_quantitative_vulnerabilities(data_path, year,calculate_metrics=True):
    outages = get_quantitative_vulnerability(data_path)
    county_totals = {}
    metric_df = pd.DataFrame()

    for county, dates in outages.items():
        print(f"County: {county}")
        county_totals[county] = 0
        # to generate SAIFI, SAIDI, and CAIDI (SAIFI/SAIDI)
        num_interruptions, cum_duration, customer_interruptions, customer_minute_interruptions = 0, 0, 0, 0
        for date, events in dates.items():
            # print(f"  Date: {date}")
            for event in events:
                num_interruptions += 1
                customer_interruptions += event[0]
                num_people_out, total_duration = event[0], event[1]
                cum_duration += total_duration
                customer_minute_interruptions+=num_people_out*total_duration
                county_totals[county] += num_people_out * total_duration  # scale importance by duration
                # print(f"    Customers out: {num_people_out} for a duration of {total_duration} minutes")

        if calculate_metrics:
            num_customers = get_num_customers_affected(county)
            saifi = customer_interruptions / num_customers
            saidi = customer_minute_interruptions / num_customers
            caidi = saidi / saifi
            year = int(data_path.split("_")[-1].replace(".csv", ""))
            if year % 2 == 1:
                svi = get_svi(county, year - 1)
            else:
                svi = get_svi(county, year)
            metrics_map = {"year": year, "county": county, "saifi": "%.5f" % saifi, "saidi": "%.5f" % saidi,
                           "caidi": "%.5f" % caidi, "svi": "%.5f" % svi}
            metric_df = pd.concat([metric_df, pd.DataFrame([metrics_map])], ignore_index=True)

    if calculate_metrics:
        metric_df.to_csv(f'./outage_records/metrics_{year}.csv', index=False)

    percentile_ranks = get_percentile_sorted_data(county_totals)

    return percentile_ranks


normalize_quantitative_vulnerabilities('outage_records/filtered_2015.csv',2015, calculate_metrics=True)


def county_metric_data(year, metric_name, normalize=True):
    csv = pd.read_csv('/Users/irislitiu/work/WSU_Outage_Analysis/outage_records/metrics.csv')
    county_metric_data = {}
    found_year = False

    all_scores = [csv.iloc[i][metric_name] for i in range(len(csv)) if csv.iloc[i]['year'] == year]

    min_val = min(all_scores)
    max_val = max(all_scores)

    for i in range(len(csv)):
        row = csv.iloc[i]
        if row['year'] == year:
            found_year = True
            if normalize:
                county_metric_data[row['county']] = (row[metric_name] - min_val) / (max_val - min_val)
            else:
                county_metric_data[row['county']] = row[metric_name]
        else:
            if found_year:
                break
    return county_metric_data


def get_normalized_nri_data(nri_path):
    csv = pd.read_csv(nri_path)

    scores = csv['RISK_SCORE'].tolist()
    min_val = min(scores)
    max_val = max(scores)

    county_scores = {}
    for i in range(len(csv)):
        county = csv.iloc[i]['COUNTY']
        risk_score = csv.iloc[i]['RISK_SCORE']
        normalized_score = (risk_score - min_val) / (max_val - min_val)
        county_scores[county] = normalized_score

    return county_scores


def svi_nri_quantitative_map(svi_path, nri_path, quantitative_data_path,
                             geojson='./illinois-with-county-boundaries_1097.geojson'):
    geojson_data = {}
    with open(geojson, 'r') as f:
        geojson_data = json.load(f)

    county_saturation = {}
    with open(svi_path, 'r') as f:
        csv = pd.read_csv(f)

    nri_data = get_normalized_nri_data(nri_path)
    quantitative_data = normalize_quantitative_vulnerabilities(quantitative_data_path)

    for i in range(len(csv)):
        row = csv.iloc[i]
        county_name = row['COUNTY'].replace('County', '').strip()
        sum, found_count, county_saturation[row['COUNTY']] = 0, 0, 0

        if row['RPL_THEMES']:
            sum += row['RPL_THEMES']
            found_count += 1
        if nri_data.keys().__contains__(county_name):
            sum += nri_data[county_name]
            found_count += 1
        if quantitative_data.keys().__contains__(county_name):
            sum += quantitative_data[county_name]
            found_count += 1
        else:
            print(f"county {county_name} not found in quantitative data")

        county_saturation[row['COUNTY']] = sum / found_count

        if county_name == "LaSalle":
            county_saturation["La Salle"] = sum / found_count
        if county_name == "St. Clair":
            county_saturation["Saint Clair"] = sum / found_count

    county_hex = {}
    for key in county_saturation.keys():
        county_hex[key.replace('County', '').strip()] = desaturate_color(county_saturation[key])

    style_function = make_style_function(county_colors_map=county_hex)

    m = folium.Map(location=[40.754, -88.931], zoom_start=6)

    color_bar_html = open('./plots_and_metric_data/colorbar.html', 'r').read()
    icon = folium.DivIcon(html=color_bar_html)
    folium.Marker(location=[40.4, -86.7], icon=icon).add_to(m)

    folium.GeoJson(
        geojson_data,
        style_function=style_function
    ).add_to(m)

    year = svi_path.split("_")[-1].replace('.csv', '')
    m.save(f"plots_and_metric_data/svi_nri_quantitative_map_{year}.html")


'''svi_nri_quantitative_map('./plots_and_metric_data/svi_interactive_map_2022.csv',
                          './plots_and_metric_data/NRI_Table_Counties_Illinois.csv', 
                          './outage_records/filtered_2022.csv')'''


def plot_metric(year, metric_name, is_svi=False, svi_data={}, geojson='./illinois-with-county-boundaries_1097.geojson'):
    geojson_data = {}
    with open(geojson, 'r') as f:
        geojson_data = json.load(f)

    county_saturation = {}
    if is_svi:
        data = svi_data
    else:
        data = county_metric_data(year, metric_name)

    # special case county names for Illinois
    for county, metric in data.items():
        if county == "LaSalle":
            county = "La Salle"
        if county == "St. Clair":
            county = "Saint Clair"
        county_saturation[county] = metric

    county_hex = {}
    for key in county_saturation.keys():
        county_hex[key] = desaturate_color(county_saturation[key])

    style_function = make_style_function(county_colors_map=county_hex)

    m = folium.Map(location=[40.754, -88.931], zoom_start=6)

    color_bar_html = open('./plots_and_metric_data/colorbar.html', 'r').read()
    icon = folium.DivIcon(html=color_bar_html)
    folium.Marker(location=[40.4, -86.7], icon=icon).add_to(m)

    folium.GeoJson(
        geojson_data,
        style_function=style_function
    ).add_to(m)

    m.save(f"plots_and_metric_data/{metric_name}_{year}.html")


def eagleI_EIA_overlap_map(data_path, save_path, geojson='./illinois-with-county-boundaries_1097.geojson'):
    with open(data_path, 'r') as f:
        data = json.load(f)
        keys = data.keys()
        num = {}
        for key in keys:
            county_list = data[key]
            for county in county_list:
                if county not in num.keys():
                    num[county] = 1
                else:
                    num[county] += 1

        max_val = max(num.values())
        min_val = min(num.values())
        norm_num = {}

        for key in num:
            norm_num[key] = (num[key] - min_val) / (max_val - min_val)

        county_hex = {}
        for key in norm_num.keys():
            county_hex[key] = desaturate_color(norm_num[key])

        style_function = make_style_function(county_colors_map=county_hex)

        m = folium.Map(location=[40.754, -88.931], zoom_start=6)

        with open(geojson, 'r') as f:
            geojson_data = json.load(f)

        folium.GeoJson(
            geojson_data,
            style_function=style_function
        ).add_to(m)

        m.save(save_path)
