import geopandas as gpd
import matplotlib.pyplot as plt

# Load the GeoJSON file
geojson_file = 'illinois-with-county-boundaries_1097.geojson'
geo_df = gpd.read_file(geojson_file)

# Plot the GeoJSON data
geo_df.plot(figsize=(20, 20), edgecolor="black", color="lightblue")
plt.title("Illinois County Boundaries")
plt.show()
import json
import plotly.express as px

# Load the GeoJSON file
geojson_file = 'illinois-with-county-boundaries_1097.geojson'
with open(geojson_file) as f:
    geojson_data = json.load(f)

# Plot the GeoJSON data
fig = px.choropleth_mapbox(
    geojson=geojson_data,
    locations=[],
    featureidkey="properties.name",  # Adjust this key based on the GeoJSON properties
    mapbox_style="carto-positron",
    center={"lat": 40.0, "lon": -89.0},  # Centering around Illinois
    zoom=6,
    opacity=0.2,
)
fig.update_layout(title_text="Illinois County Boundaries")
fig.show()
import geopandas as gpd

# Load the GeoJSON file
geojson_file = 'illinois-with-county-boundaries_1097.geojson'
geo_df = gpd.read_file(geojson_file)

# Calculate the centroids of each county
geo_df['centroid'] = geo_df.geometry.centroid

# Extract centroid coordinates
geo_df['centroid_lat'] = geo_df.centroid.y
geo_df['centroid_lon'] = geo_df.centroid.x

# Display the centroids with county names
centroids_df = geo_df[['name', 'centroid_lat', 'centroid_lon']]  # Replace 'name' with the appropriate column for county names
print(centroids_df)

# Save the centroid data to a CSV file if needed
centroids_df.to_csv("illinois_county_centroids.csv", index=False)
import matplotlib.pyplot as plt

# Plot counties and centroids
fig, ax = plt.subplots(figsize=(10, 10))
geo_df.plot(ax=ax, color='lightblue', edgecolor='black', alpha=0.5)
geo_df.centroid.plot(ax=ax, color='red', markersize=10, label="Centroids")
plt.legend()
plt.title("Illinois Counties and Centroids")
plt.show()
