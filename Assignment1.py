import sys
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point

df = pd.read_csv('DataFiles/PlanningEnforcement_AppealDecisions.csv')
df['Geometry'] = list(zip(df['Y'], df['X']))
df['Geometry'] = df['Geometry'].apply(Point)
df.head()

