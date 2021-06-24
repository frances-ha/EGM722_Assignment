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
print(gdf.columns)
gdf.set_crs("EPSG:29902", inplace=True)




