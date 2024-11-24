import pandas as pd
import geopandas as gpd
from shapely.geometry import Point

# Load county GeoJSON file
geojson_file = 'illinois-with-county-boundaries_1097.geojson'
counties = gpd.read_file(geojson_file)

# Reproject counties to a projected CRS for accurate distance calculation
counties = counties.to_crs(epsg=26971)  # NAD83 / Illinois East
counties['centroid'] = counties.geometry.centroid

# Create a 20 km buffer around each county centroid
counties['buffer_25km'] = counties.centroid.buffer(25000)  # 25 km buffer in meters

# Load weather station data
stations = pd.read_csv('Location_of_weatherstation.csv')  # Replace with the actual file name
stations_gdf = gpd.GeoDataFrame(
    stations,
    geometry=gpd.points_from_xy(stations.Longtitude, stations.Lalitude),
    crs='EPSG:4326'  # Assume stations are in geographic CRS (lat/lon)
)

# Reproject weather stations to the same CRS as counties
stations_gdf = stations_gdf.to_crs(epsg=26971)

# Check which stations fall within the 20 km buffer
results = []

for _, county in counties.iterrows():
    for _, station in stations_gdf.iterrows():
        if station.geometry.within(county['buffer_25km']):
            results.append({
                'county_name': county['name'],  # Replace 'name' with the column for county names
                'station_name': station['Station_name'],
                'station_lat': station['Lalitude'],
                'station_lon': station['Longtitude']
            })

# Create a DataFrame of the results
results_df = pd.DataFrame(results)

# Save results to a CSV
results_df.to_csv('stations_mapped_to_counties.csv', index=False)

# Print a sample of the results
print(results_df.head())
grouped = results_df.groupby('county_name').agg({
    'station_name': list,  # Group station names into a list
    'station_name': 'count',  # Count number of stations per county
}).rename(columns={'station_name': 'station_count'})

# Merge the grouped DataFrame back with the original list of station names
grouped_with_stations = (
    results_df.groupby('county_name')
    .agg({'station_name': lambda x: list(x)})
    .merge(grouped, left_index=True, right_index=True)
    .reset_index()
)
grouped_with_stations.to_csv('stations_grouped_by_county.csv', index=False)

# Print a sample of the grouped results
print(grouped_with_stations.head())
target_county = 'Winnebago'
target_county_data = grouped_with_stations[grouped_with_stations['county_name'] == target_county]

# Print the results for the target county
print(target_county_data)
for _, row in grouped_with_stations.iterrows():
    if row['station_count'] == 0:
        print(f"There is no weather station for {row['county_name']}.")
counties_without_stations = grouped_with_stations[grouped_with_stations['station_count'] == 0]

if not counties_without_stations.empty:
    print("Counties with no weather stations:")
    print(counties_without_stations['county_name'].tolist())
else:
    print("All counties have at least one weather station.")

