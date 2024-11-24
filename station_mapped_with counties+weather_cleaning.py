# Import necessary libraries
import geopandas as gpd
import pandas as pd
from shapely.geometry import Point
import os
import glob
import matplotlib.pyplot as plt

# Load County GeoJSON file
counties = gpd.read_file('illinois-with-county-boundaries_1097.geojson')

# Load Weather Station CSV and create a GeoDataFrame
stations = pd.read_csv('Location_of_weatherstation.csv')
stations_gdf = gpd.GeoDataFrame(
    stations,
    geometry=gpd.points_from_xy(stations.Longtitude, stations.Lalitude),
    crs='EPSG:4326'  # Assuming WGS84 (latitude/longitude)
)

# Ensure both datasets are in the same CRS
counties = counties.to_crs(stations_gdf.crs)

# Perform a spatial join to match stations to counties
stations_in_counties = gpd.sjoin(stations_gdf, counties, how="inner", predicate="within")

# Clean up the results
stations_in_counties = stations_in_counties[['Station_name', 'Lalitude', 'Longtitude', 'name']].rename(
    columns={'name': 'County'}
)

# Save the results to a CSV file
stations_in_counties.to_csv('stations_mapped_to_counties.csv', index=False)

# Group by County to see how many stations each county has
grouped = stations_in_counties.groupby('County').agg(
    station_count=('Station_name', 'count'),
    station_names=('Station_name', list)
).reset_index()

# Save the grouped data
grouped.to_csv('stations_grouped_by_county.csv', index=False)

# Select target county (e.g., Cook County)
target_county = 'Cook'
target_county_data = grouped[grouped['County'] == target_county]
station_names_in_target_county = target_county_data['station_names'].iloc[0]

# Specify the root folder containing weather data
root_folder = 'Hourly_WeatherData_IL'

# Initialize an empty DataFrame to store all processed data across years
df_combined_all_years = pd.DataFrame()

# Loop through each year folder
for year_folder in os.listdir(root_folder):
    year_folder_path = os.path.join(root_folder, year_folder)
    
    # Check if the folder is a valid directory and represents a year
    if os.path.isdir(year_folder_path):
        print(f"Processing year: {year_folder}")
        
        # Initialize a DataFrame for this year's data
        df_combined_year = pd.DataFrame()
        
        # Get all CSV files for this year
        csv_files = glob.glob(os.path.join(year_folder_path, "*.csv"))
        
        for file in csv_files:
            file_name = os.path.basename(file).replace('.csv', '')
            
            # Check if the file corresponds to one of the stations in the target county
            if file_name in station_names_in_target_county:
                print(f"Processing file: {file_name}")
                df = pd.read_csv(file)
                
                # Extract windspeed from 'WND' column
                df['ws'] = df['WND'].apply(lambda x: x.split(',')[3] if isinstance(x, str) and len(x.split(',')) > 3 else 0)
                df['ws'] = df['ws'].astype(int).apply(lambda x: 0 if x == 9999 else x)
                
                # Convert DATE column to datetime and round to the nearest hour
                df['DATE'] = pd.to_datetime(df['DATE'], errors='coerce').dt.round('h')
                
                # Keep only the maximum windspeed for each timestamp
                df_cleaned = df[df.groupby('DATE')['ws'].transform('max') == df['ws']]
                
                # Append to this year's combined DataFrame
                df_combined_year = pd.concat([df_combined_year, df_cleaned], ignore_index=True)
        
        # Append this year's data to the overall combined DataFrame
        df_combined_all_years = pd.concat([df_combined_all_years, df_combined_year], ignore_index=True)
print(df_combined_all_years.columns)

# Ensure the combined data has the full hourly range across all years
start_time = '2018-01-01 00:00:00'
end_time = '2023-12-31 23:00:00'
full_range = pd.date_range(start=start_time, end=end_time, freq='1h')

df_full_range = pd.DataFrame({'DATE': full_range})
df_full_range.set_index('DATE', inplace=True)

# Merge with the combined dataset
df_combined_all_years['DATE'] = pd.to_datetime(df_combined_all_years['DATE'])
df_combined_all_years.set_index('DATE', inplace=True)
df_result_all_years = df_full_range.merge(df_combined_all_years[['ws']], how='left', left_index=True, right_index=True)


df_result_all_years['ws'] = (df_result_all_years['ws']*3.6)/10 # 10 is scalling factor and 3.6 to convert  m/s in km/hour
# Save the processed dataset for all years
output_filename = f'weather_data_{target_county}_cleaned_all_years.xlsx'
df_result_all_years.to_excel(output_filename, index=False)
print(f"File saved successfully as {output_filename}")
print(df_result_all_years.head())

# Visualize the data
plt.figure(figsize=(12, 6))
plt.plot( df_result_all_years['ws'], marker='o', linestyle='-', color='r', label='Hourly Data')
#plt.plot(df_15min_all_years['DATE'], df_15min_all_years['ws'], marker='*', linestyle='-', color='b', label='15-Minute Interpolated Data')
plt.xlabel('Date')
plt.ylabel('Wind Speed(km/hour)')
plt.title(f'Wind Speed for Weather Stations in {target_county} County (All Years)')
plt.legend()
plt.xticks(rotation=45)
plt.grid(True)
plt.tight_layout()
plt.show()