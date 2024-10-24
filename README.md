# Summer2024-Outage-Analysis
The documentation for all files and folders in this repository is as follows

## Code Files 


### csv_utils.py

#### xlsx_to_csv
Converts an Excel file to a CSV.
#### concatenate_csvs
Combines a list of CSVs with the same column names into one CSV.
#### normalize_columns
During Excel to CSV conversion, some of the column names from the **energy_information_administration** folder (EIA general data)
are spread out across the first few rows, so this function condenses all column names into the first row of the CSV to adhere to proper CSV format.

### data_filterer.py

#### filter_csv_EIA_dataset
Filter the general US datasets in the  **energy_information_administration** folder for state-specific row entries.
#### reformat
Remove duplicate column name rows from the Major Disturbances and Unusual Occurrences dataset (XLSX had columns written again for each new sheet in its PDF form) and recombine entries that were spread out over multiple rows during XLSX to CSV conversion.
#### filter_disturbances
Filter datasets general US from the **EIA_disturbances_data** folder to include state-specific data.
#### filter_weather_events
Filter datasets from the **illinois_weather_data** folder to create a new CSV with only the specified event types (e.g., Hurricane, Tornado).
#### filter_repeats
Filter datasets from the **outage_records** folder (EAGLE-I data) to combine the same event which was split up into 15 minute recording intervals into the same event. The new CSV also includes a column representing event end time.

### metric_calculations.py

#### make_style_function
Define styling for geojson of state counties (fill color, border weight, opacity).
#### desaturate_color
Determines county color on geojson based on scale factor between 0 and 1, which scales the amount of green and blue in the fill color of the county.
#### get_time_diff
Get the time difference between the start and end times of an event from the filtered EAGLE-I dataset in the **outage_records** folder.
#### get_quantitative_vulnerability
Parse the filtered EAGLE-I dataset for all of the distinct events per county. Return a map of counties to events (date, number of people affected, duration in minutes). Each county has a value corresponding to a map of distinct dates. Each date has a value corresponding to an array of tuples of the number of people affected by the event and the duration of the event in minutes.
#### search_for_equals
Check the number of values equal to the value at a certain index in a sorted list (used when calculating percentile ranks).
#### get_percentile_sorted_data
Percentile rank the values of a map by sorting the values of the map in ascending order and determining the number of values less than, equal to, and greater than a given value. The percentile rank is the number of elements less than the given element plus 1/2 times the number of elements equal to the given element, over the total number of elements.
#### get_num_customers_affected
Gets the total number of customers in the power network of a given county by retrieving the county's FIPS code (**county_to_fips.csv**) and mapping it to the number of customers (**mcc.csv**).
#### get_svi
Get the 4-theme SVI value for a given county on a given year.
#### normalize_quantitative_vulnerabilities
Returns a per-county vulnerability metric based on the total number of customers affected and the cumulative outage duration, using the data from **get_quantitative_vulnerability**. The data is normalized to so it can be plotted via a geojson. If the calculate_metrics parameter is set to True (default is False), SAIFI, SAIDI, CAIDI, and SVI will be calculated for the given input data and written to a CSV.
#### county_metric_data
Returns a county to metric map of one of the metrics from **outage_records/metrics.csv** (SAIDI, SAIFI, CAIDI, or SVI). 
#### get_normalized_nri_data
Normalize NRI data from **/plots_and_metric_data/NRI_Table_Counties_Illinois.csv**
#### svi_nri_quantitative_map
Plot a weighted sum of SVI, NRI, and EAGLE-I data for each county on a geojson (map is generated with the Folium library).
#### plot_metric
Plot SAIDI, SAIFI, CAIDI, or SVI on a geojson.
#### eagleI_EIA_overlap_map
Plot the normalized number of overlap between the **EIA_disturbances_data** and **outage_records** datasets on a geojson.

### metric_mapper.py

#### convert_to_json_serializable
Convert common datatypes to JSON serializable datatypes.
#### combine_weather_and_eagle_I_data
Combine the data in **illinois_weather_data** and **outage_records** datasets into a JSON with root keys being every date in a given year. The JSON is populated with the weather events and the number of major events from the EAGLE-I dataset for each date.
#### find_wind_mph
Finds the wind speed in MPH for an event with a given date and county in the filtered weather data files (**illinois_weather_data**).
#### combine_weather_data
Create a CSV with the date and county of an event, as well as the number of people affected and the wind speed of the event. Combines yearly data from the **illinois_weather_data** and **outage_records** datasets.

### svi_calculator.py

#### updated_svi
Add CAIDI as a 5th theme to SVI by summing percentile ranked themes and percentile ranking the result. The **get_stats** option also calculates the average CAIDI and its standard deviation for each SVI quartile.

## Data Folders


### EIA_disturbances_data
US and Illinois disturbances data. Includes year-by-year data and concatenated data for 2014-2023.

### energy_information_administration
Various power metrics (the Reliability CSV has SAIDI,SAIFI,CAIDI,CAIFI) for Illinois and the US for 2014-2022.

### illinois_weather_data
General weather data and wind event data for Illinois for 2015-2024.

### outage_records
Raw Eagle-I data, filtered Eagle-I data (no event repeats), and county metrics data (SAIDI, SAIFI, CAIDI, SVI) for 2014-2023.

### plots_and_metric_data
SVI and NRI data, colorbar HTML file for Folium map. Geojson maps for: 
- SVI
- CAIDI 
- SVI and CAIDI
- SVI and NRI
- EAGLE-I data
- SVI, NRI, and EAGLE-I data

### weather_data_with_eagle_I
JSONs of weather events and EAGLE-I major event frequencies for each day in a given year for 2015-2023. 

### wind_and_eagle_I_csvs
CSVs of events including their date, county, number of people affected, and the wind speed of the event.

## EAGLE-I EIA Overlap
#### The data contained in this folder are JSON files, each with a key of a date and a time and the value associated with the times is a list of counties. The date is significant of a major outage disturbance noticed by the EIA, and the list of couties is representative of counties with customers that experienced a disturbance on that date, based on the EAGLE-I data.

## Sorted EAGLE-I
#### The data contained in this folder is EAGLE-I data for each year sorted in a CSV file. The original EAGLE-I data is the recorded amount of customers who experienced an outage every 15 minutes. The data available for each year is the county, zip code, time, date, and customers impacted. The original data is out of order in terms of dates and times. The python file, "county_data.py" utilizes a selection sort algorithm to sort the EAGLE-I data by date and time. 

## illinois_weather_data
#### The data in the illinois_weather data are CSV files of the major weather disturbances(hail, winter storm, thunder, etc.) in Illinois for each year. The files with "filtered" only contain rows that have measurements for the magnitude of a major disturbance. For example, the strong wind events given the measurement for the knots. The other files are the untouched CSV files of the weather data pulled from NOAA.

## Weather + EAGLE-I
#### The single CSV in the folder is a combination of the weather data and the EAGLE-I data. It is in the form of a timeline and puts a specific weather disturbance in the EAGLE-I data in order to see the aftermath of certain weather events. Due to the unnecessary amount of data points and length, this data doesn't fully serve our purpose, so it has been excluded from our final results.
