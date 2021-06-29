# add imports
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from shapely.geometry import Point
from cartopy.feature import ShapelyFeature
import cartopy.crs as ccrs
import matplotlib.patches as mpatches
import matplotlib.lines as mlines

plt.ion() # turn on interactive mode

# define all functions first as interpreter runs each line of script in sequence and
# we don't want it to try to evaluate commands that haven't yet been defined.

# map legend prep

# generate matplotlib handles to create a legend of features to put in the map output.
def generate_handles(labels, colors, edge='k', alpha=1):
    lc = len(colors) # get length of colours list
    handles = []
    for i in range(len(labels)):
        handles.append(mpatches.Rectangle((0, 0), 1, 1, facecolor=colors[i % lc], edgecolor=edge, alpha=alpha))
    return handles

# create scale bar function definition to be displayed in bottom left corner of map output
def scale_bar_left(ax, location=(0.15, 0.05)):
    llx0, llx1, lly0, lly1 = ax.get_extent(ccrs.PlateCarree())
    sbllx = (llx1 + llx0) / 2
    sblly = lly0 + (lly1 - lly0) * location[1]

    tmc = ccrs.TransverseMercator(sbllx, sblly)
    x0, x1, y0, y1 = ax.get_extent(tmc)
    sbx = x0 + (x1 - x0) * location[0]
    sby = y0 + (y1 - y0) * location[1]

    plt.plot([sbx, sbx - 20000], [sby, sby], color='k', linewidth=9, transform=tmc)
    plt.plot([sbx, sbx - 10000], [sby, sby], color='k', linewidth=6, transform=tmc)
    plt.plot([sbx - 10000, sbx - 20000], [sby, sby], color='w', linewidth=6, transform=tmc)

    plt.text(sbx, sby - 4500, '20 km', transform=tmc, fontsize=8)
    plt.text(sbx - 12500, sby - 4500, '10 km', transform=tmc, fontsize=8)
    plt.text(sbx - 24500, sby - 4500, '0 km', transform=tmc, fontsize=8)

# load NI data from shapefiles
outline = gpd.read_file('DataFiles/NI_outline.shp')
lgds = gpd.read_file('DataFiles/LocalGovernmentDistricts.shp')

# create new shapefile from csv text file
sdf = pd.read_csv('DataFiles/PlanningEnforcement_AppealDecisions.csv')
sdf['geometry'] = list(zip(sdf['X'], sdf['Y']))
sdf['geometry'] = sdf['geometry'].apply(Point)
del sdf['X'], sdf['Y']
print(sdf.head())
print(sdf.columns)

gdf = gpd.GeoDataFrame(sdf)
# data is in Irish Grid, needs to be converted to unprojected lat/lon coordinates, use global standard WGS84 datum.
gdf.set_crs("EPSG:4326", inplace=True)
print(gdf.head)

gdf.to_file('DataFiles/appeal_points.shp')

# create a new GeoAxis pyplot figure
myFig = plt.figure(figsize=(10, 10))

myCRS = ccrs.UTM(29) # plot is expecting one CRS (WGS84 UTM Zone 29N) but data is currently in WGS84 Lat/Lon

ax = plt.axes(projection=ccrs.Mercator())

outline_feature = ShapelyFeature(outline['geometry'], myCRS, edgecolor='k', facecolor='w')
xmin, ymin, xmax, ymax = outline.total_bounds
ax.add_feature(outline_feature)

ax.set_extent([xmin, xmax, ymin, ymax], crs=myCRS)

myFig.show()
