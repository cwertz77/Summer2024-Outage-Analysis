#Import necessary library
import geopandas as gpd
import pandas as pd
from shapely.geometry import Point
import os
import glob

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

#print(stations_in_counties)

# Clean up the results (optional)
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

# Print a sample of the results
print(stations_in_counties.head())
print(grouped.head())
target = 'Cook'
target_county_data = grouped[grouped['County'] == target]
print(target_county_data['station_names'])
station_names_in_target_county = target_county_data['station_names'].iloc[0]

# Load the data from the weather stations
#Specify the root datasets folder
root_folder = 'Hourly_WeatherData_IL'
#Initialize empty data file to store meta files and files
matching_files = []

#Iterate over each year folder inside root folder
for year_folder in os.listdir(root_folder):
    year_folder_path = os.path.join(root_folder,year_folder)
    if os.path.isdir(year_folder_path):
        csv_files = glob.glob(os.path.join(year_folder_path, "*.csv"))
        
        # Filter the files based on station names
        for file in csv_files:
            # Extract the station ID from the file name (assuming the station name is part of the file name)
            file_name = os.path.basename(file).replace('.csv', '')
            
            # Check if the file corresponds to one of the stations in the target county
            if file_name in station_names_in_target_county:
                matching_files.append(file)

# Print the list of matching files
print("Matching files for the target county (Cook):")
for file in matching_files:
    print(file)

# Example: Loading the first matching file
if matching_files:
    example_file = matching_files[0]
    df_example = pd.read_csv(example_file)
    print(f"Loaded data from: {example_file}")
    print(df_example.head())
else:
    print("No matching files found for the target county.")

    
    # Save the cleaned data to the current working directory
    output_filepath = os.path.join(os.getcwd(), output_filename)
    df_cleaned.to_csv(output_filepath, index=False)
    
   
    print(f"Saved cleaned data to {output_filename}")
    print(df_cleaned)








