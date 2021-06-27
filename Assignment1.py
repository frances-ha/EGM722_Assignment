import pandas as pd
import geopandas as gpd
from shapely.geometry import Point

df = pd.read_csv('DataFiles/PlanningEnforcement_AppealDecisions.csv')
df['geometry'] = list(zip(df['X'], df['Y']))
df['geometry'] = df['geometry'].apply(Point)
del df['X'], df['Y']
print(df.head())
print(df.columns)

gdf = gpd.GeoDataFrame(df)
# data is in Irish Grid, needs to be converted to unprojected lat/lon coordinates, use global standard WGS84 datum.
gdf.set_crs("EPSG:4326", inplace=True)
print(gdf.head)

gdf.to_file('DataFiles/appeal_points.shp')



