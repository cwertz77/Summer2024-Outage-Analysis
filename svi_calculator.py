import pandas as pd
import statistics as stats
from metric_calculations import county_metric_data, get_percentile_sorted_data, plot_metric

def updated_svi(svi_data_path, get_stats=False):
    svi_csv = pd.DataFrame()
    year = int(svi_data_path.split("_")[-1].replace(".csv", ""))
    with open(svi_data_path, 'r') as f:
        svi_csv = pd.read_csv(f)
    
    # extract percentile ranked rpl_themes for each county and put into map {county: {rpl_theme_1: 0.2, ..., rpl_theme_4: 0.41}}
    svi_themes = {}
    for i in range(len(svi_csv)):
        row = svi_csv.iloc[i]
        county = row["COUNTY"].replace("County", "").strip()
        svi_themes[county] = {k: v for k, v in [(f"theme_{i}", row[f"RPL_THEME{i}"]) for i in range(1, 5)]}

    # percentile rank caidi county data
    raw_caidi = county_metric_data(year, "caidi", normalize=False)
    caidi_data = get_percentile_sorted_data(county_metric_data(year, "caidi"))

    # add caidi percentile ranks as a key-value pair in map for each county and sum percentile ranked themes
    new_svi, caidi_svi_percentile = {}, {}
    for county in svi_themes.keys():
        if county in caidi_data.keys():
            county_name = county.replace("County", "").strip()
            svi_themes[county]["theme_5"] = caidi_data[county_name]
            theme_sum = sum([svi_themes[county][f"theme_{i}"] for i in range(1, 5)])
            new_svi[county.replace("County", "").strip()] = theme_sum
            caidi_svi_percentile[raw_caidi[county_name]] = theme_sum

    if get_stats:
        caidi_to_svi = get_percentile_sorted_data(caidi_svi_percentile)

        percentile_av_caidi = {}
        for i in range(1, 5):
            all_caidis = []
            for caidi, norm_svi in caidi_to_svi.items():
                if norm_svi < 0.25*i and norm_svi > 0.25*(i-1):
                    all_caidis.append(caidi)
            if all_caidis:
                percentile_av_caidi[i] = all_caidis

        df_format = {"YEAR": [year]}
        for key, vals in percentile_av_caidi.items():
            mean, std_dev, threshold = stats.mean(vals), stats.stdev(vals), 1
            norm_vals = [val for val in vals if (mean - std_dev * threshold) <= val <= (mean + std_dev * threshold)]
            mean, std_dev = stats.mean(norm_vals), stats.stdev(norm_vals)
            df_format[f"AV_CAIDI_Q{key}"] = [round(mean, 2)]
            df_format[f"STD_DEV_CAIDI_Q{key}"] = [round(std_dev, 2)]
            print(f"{key} quartile with av caidi {mean:.2f} and std dev {std_dev:.2f} (min: {min(norm_vals)}, max: {max(norm_vals)})")

        df = pd.DataFrame(df_format)
        cur_df = pd.read_csv("./caidi_stats.csv")
        df = pd.concat([df, cur_df], ignore_index=True)
        df.to_csv("./caidi_stats.csv", index=False)

    new_svi = get_percentile_sorted_data(new_svi)
    return new_svi


