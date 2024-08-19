import pandas as pd
from metric_calculations import county_metric_data, get_percentile_sorted_data, plot_metric

def updated_svi(svi_data_path):
    svi_csv = pd.DataFrame()
    year = int(svi_data_path.split("_")[-1].replace(".csv", ""))
    print(year)
    with open(svi_data_path, 'r') as f:
        svi_csv = pd.read_csv(f)
    
    # extract percentile ranked rpl_themes for each county and put into map {county: {rpl_theme_1: 0.2, ..., rpl_theme_4: 0.41}}
    svi_themes = {}
    for i in range(len(svi_csv)):
        row = svi_csv.iloc[i]
        svi_themes[row["COUNTY"]] = {k: v for k, v in [(f"theme_{i}", row[f"RPL_THEME{i}"]) for i in range(1, 5)]}

    # percentile rank caidi county data
    caidi_data = get_percentile_sorted_data(county_metric_data(year, "caidi"))

    # add caidi percentile ranks as a key-value pair in map for each county and sum percentile ranked themes
    new_svi = {}
    for county in svi_themes.keys():
        if county in caidi_data.keys():
            svi_themes[county]["theme_5"] = caidi_data[county.replace("County", "").strip()]
            theme_sum = sum([svi_themes[county][f"theme_{i}"] for i in range(1, 5)])
            new_svi[county.replace("County", "").strip()] = theme_sum

    new_svi = get_percentile_sorted_data(new_svi)
    return new_svi

all = updated_svi('./plots_and_metric_data/svi_interactive_map_2014.csv')
for key, val in all.items():
    print(f"{key}: {val}")

plot_metric(2014, "svi_with_caidi", is_svi=True, svi_data=all)