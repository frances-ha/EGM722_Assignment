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

# Functions are defined first as each line of the script is run in sequence & we don't want interpreter to throw errors
# when evaluating commands that haven't yet been written.

# Prepare for map legend by generating matplotlib handles to create legend of features to go in map output

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

# Create new shapefile of Planning Appeals Commission data from csv text file

sdf = pd.read_csv('DataFiles/PlanningEnforcement_AppealDecisions.csv')
sdf['geometry'] = list(zip(sdf['X'], sdf['Y']))
sdf['geometry'] = sdf['geometry'].apply(Point)
del sdf['X'], sdf['Y']
print(sdf.head())

appeals = gpd.GeoDataFrame(sdf) # converting AppealDecisions.csv spatial data frame into a GeoDataFrame.
appeals.set_crs("EPSG:4326", inplace=True) # csv XYs were in Irish Grid, these need to be converted to unprojected
# lat-long coordinates using global internet standard WGS84 datum.
print(appeals.head())
appeals.to_file('DataFiles/appeal_points.shp')

# Load open source Northern Ireland (NI) data from shapefiles

outline = gpd.read_file('DataFiles/NI_outline.shp')
lgds = gpd.read_file('DataFiles/NI_LocalGovernmentDistricts.shp')

# re-project all shapefile geometries to correct crs for display in mapping output (in this case UTM29)

appeals = appeals.to_crs(epsg=32629)
outline = outline.to_crs(epsg=32629)
lgds = lgds.to_crs(epsg=32629)

# myCRS = ccrs.UTM(29)

# create a new GeoAxis pyplot figure
# myFig = plt.figure(figsize=(10, 10)) #this is just a normal matplotlib Axes object with no projection info.
# this line should prob be deleted.


# n.b. plot is expecting one CRS (WGS84 UTM Zone 29N) but data is currently in WGS84 lat-long.
# UTM is bad for small-scale world maps, good for mapping narrow regions e.g. NI.
#For projected layer crs, add UTM coordinate system at 29. WGS 84 / UTM zone 29N EPSG code is 32629

# create a new GeoAxes pyplot figure.  subplot kwarg is crucial; tells matplotlib how to transform gridlines and put
# them in right place.  NI shapefile data is currently in WGS 84 lat-long.  Need to transform NI data into same CRS as
# plot.
# fig, ax = plt.subplots(1,1, figsize=(10,10), subplot_kw=dict(projection=myCRS)) #plt.subplots allows adding of
# multiple Axes objects.  Keyword argument tells matplotlib how to transform gridlines and put them in right place.

# outline_feature = ShapelyFeature(outline['geometry'], myCRS, edgecolor='k', facecolor='w')
# xmin, ymin, xmax, ymax = outline.total_bounds
# ax.add_feature(outline_feature)

# ax.set_extent([xmin, xmax, ymin, ymax], crs=myCRS)

# myFig.show()
