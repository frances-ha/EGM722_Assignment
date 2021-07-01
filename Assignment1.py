# Add imports

import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from shapely.geometry import Point
from cartopy.feature import ShapelyFeature
import cartopy.crs as ccrs
import matplotlib.patches as mpatches
import matplotlib.lines as mlines

plt.ion() # turn on interactive mode

# Define functions at top of script to prevent interpreter from throwing errors when attempting to evaluate commands
# that haven't yet been written.

# Prepare for map legend by generating matplotlib handles to create legend of features to go in final map output

def generate_handles(labels, colors, edge='k', alpha=1):
    lc = len(colors) # get length of colours list
    handles = []
    for i in range(len(labels)):
        handles.append(mpatches.Rectangle((0, 0), 1, 1, facecolor=colors[i % lc], edgecolor=edge, alpha=alpha))
    return handles

# Create scale bar function definition to be displayed in bottom left corner of map output

def scale_bar(ax, location=(0.15, 0.05)): # ax is axes to draw scalebar on
    llx0, llx1, lly0, lly1 = ax.get_extent(ccrs.PlateCarree()) # get limits of axis in lat-long.
    # ccrs (Cartopy Coordinate Reference System) is Cartopy's crs module (see import list).
    # ccrs.PlateCarree class makes PlateCarree projection available from Cartopy projection list.
    # There are different options for global projections (e.g. ccrs.Mercator)
    # PlateCarree projection is Cartopy default, a grid of equal rectangles, less distorted than Mercator.

    # make Transverse Mercator (tmc) horizontally centred in the middle of the map, vertically at scale bar location.
    sbllx = (llx1 + llx0) / 2
    sblly = lly0 + (lly1 - lly0) * location[1]
    tmc = ccrs.TransverseMercator(sbllx, sblly) # Irish Grid is based on a Transverse Mercator projection

    x0, x1, y0, y1 = ax.get_extent(tmc) # get extent of plotted area in coordinates in metres

    # turn specified scale bar location into coordinates in metres.
    sbx = x0 + (x1 - x0) * location[0]
    sby = y0 + (y1 - y0) * location[1]

    plt.plot([sbx, sbx - 20000], [sby, sby], color='k', linewidth=9, transform=tmc)
    plt.plot([sbx, sbx - 10000], [sby, sby], color='k', linewidth=6, transform=tmc)
    plt.plot([sbx - 10000, sbx - 20000], [sby, sby], color='w', linewidth=6, transform=tmc)

    plt.text(sbx, sby - 4500, '20 km', transform=tmc, fontsize=8)
    plt.text(sbx - 12500, sby - 4500, '10 km', transform=tmc, fontsize=8)
    plt.text(sbx - 24500, sby - 4500, '0 km', transform=tmc, fontsize=8)

# Create new shapefile of PAC enforcement appeal data from csv text file

sdf = pd.read_csv('DataFiles/PlanningEnforcement_AppealDecisions.csv')
sdf['geometry'] = list(zip(sdf['X'], sdf['Y']))
sdf['geometry'] = sdf['geometry'].apply(Point)
del sdf['X'], sdf['Y']
print(sdf.head())

appeals = gpd.GeoDataFrame(sdf) # converting AppealDecisions.csv spatial data frame into a GeoDataFrame.
appeals.set_crs("EPSG:4326", inplace=True) # csv XYs were in Irish Grid, these need to be converted to unprojected
# lat-long coordinates using global mapping standard WGS84 datum.
print(appeals.head())
appeals.to_file('DataFiles/appeal_points.shp')

# Load open source Northern Ireland (NI) shapefile data

outline = gpd.read_file('DataFiles/NI_outline.shp')
lgds = gpd.read_file('DataFiles/NI_LocalGovernmentDistricts.shp')

# transform all shapefile geometries to appropriate projected crs for display in mapping output plot.
# WGS84 UTM (Zone 29) is good for large-scale mapping especially when a small region such as NI fits within one
# of the 60 zones in a UTM projection.

appeals = appeals.to_crs(epsg=32629)
outline = outline.to_crs(epsg=32629)
lgds = lgds.to_crs(epsg=32629)

# creating a new GeoAxes pyplot figure

myFig = plt.figure(figsize=(10, 10))

myCRS = ccrs.UTM(29) # telling plot to expect data in WGS84 UTM29.

# create an object of class Axes using UTM projection to tell pyplot where to plot data.
ax = plt.axes(projection=ccrs.UTM(29))

# use Cartopy ShapelyFeature class to draw NI's outline from the shapefile polygon geometry and add it to the map.
outline_feature = ShapelyFeature(outline['geometry'], myCRS, edgecolor='k', facecolor='w')

xmin, ymin, xmax, ymax = outline.total_bounds

ax.add_feature(outline_feature)

ax.set_extent([xmin, xmax, ymin, ymax], crs=myCRS)

