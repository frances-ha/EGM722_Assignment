# Add imports

import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from matplotlib import font_manager, rcParams
from pyproj import Proj, transform
from shapely.geometry import Point
from cartopy.feature import ShapelyFeature
import cartopy.crs as ccrs
import matplotlib.patches as mpatches
import matplotlib.lines as mlines

plt.ion()  # turn on interactive mode

# Define functions at top of script to prevent interpreter from throwing errors when attempting to evaluate commands
# that haven't yet been written.

# Prepare for map legend by generating matplotlib handles to create legend of features to go in final map output

def generate_handles(labels, colors, edge='k', alpha=1):
    lc = len(colors)  # get length of colours list
    handles = []
    for i in range(len(labels)):
        handles.append(mpatches.Rectangle((0, 0), 1, 1, facecolor=colors[i % lc], edgecolor=edge, alpha=alpha))
    return handles


# Create scale bar function definition to be displayed in bottom left corner of map output

def scale_bar(ax, location=(0.15, 0.1)):  # ax is axes to draw scalebar on
    llx0, llx1, lly0, lly1 = ax.get_extent(ccrs.PlateCarree())  # get limits of axis in lat-long.
    # ccrs (Cartopy Coordinate Reference System) is Cartopy's crs module (see import list).
    # ccrs.PlateCarree class makes PlateCarree projection available from Cartopy projection list.
    # There are different options for global projections (e.g. ccrs.Mercator)
    # PlateCarree projection is Cartopy default, a grid of equal rectangles, less distorted than Mercator.

    # make Transverse Mercator (tmc) horizontally centred in the middle of the map, vertically at scale bar location.
    sbllx = (llx1 + llx0) / 2
    sblly = lly0 + (lly1 - lly0) * location[1]
    tmc = ccrs.TransverseMercator(sbllx, sblly)  # Irish Grid is based on a Transverse Mercator projection

    x0, x1, y0, y1 = ax.get_extent(tmc)  # get extent of plotted area in coordinates in metres

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

df = pd.read_csv('DataFiles/PlanningEnforcement_AppealDecisions.csv')
inProj, outProj = Proj("epsg:29902"), Proj("epsg:4326")
df['Y1'], df['X1'] = transform(inProj, outProj, df['X'].tolist(), df['Y'].tolist())
df.reset_index(inplace=True)
print(df.columns) # show current order of dataframe columns
df = df.reindex(columns=['level_0', 'index', 'Appeal_Reference', 'Departmental_Reference',
       'Development_Description', 'House_Number', 'Street_Name', 'Postcode',
       'Decision_Date', 'PAC_Decision_Outcome', 'X', 'Y', 'X1', 'Y1',
       'geometry'])

print(df.head())
df['geometry'] = list(zip(df['X1'], df['Y1']))
df['geometry'] = df['geometry'].apply(Point)
# del df['X'], df['Y']
print(df.head())


appeals = gpd.GeoDataFrame(df)  # converting AppealDecisions.csv spatial data frame into a GeoDataFrame.
appeals.set_crs("EPSG:4326", inplace=True)  # csv XYs are in Irish Grid, these need to be reprojected to WGS84 lat-long
print(appeals.head())
appeals.to_file('DataFiles/appeal_points.shp')

# Load shapefile data

outline = gpd.read_file('DataFiles/NI_outline.shp')
lgd = gpd.read_file('DataFiles/NI_LocalGovernmentDistricts.shp')
water = gpd.read_file('DataFiles/NI_Water_Bodies.shp')
appeals = gpd.read_file('DataFiles/appeal_points.shp')

# Export Lough Neagh polygon from NI_Water_Bodies.shp to new shapefile to display in a simplified map display

neagh = water.head(1)
neagh.to_file('DataFiles/lough_neagh.shp')
neagh = gpd.read_file('DataFiles/lough_neagh.shp')

# transform all shapefile geometries to appropriate projected crs for display in mapping output plot.
# WGS84 UTM (Zone 29) is good for large-scale mapping especially when a small region such as NI fits within one
# of the 60 zones in a UTM projection.

appeals = appeals.to_crs(epsg=32629)
outline = outline.to_crs(epsg=32629)
lgd = lgd.to_crs(epsg=32629)
neagh = neagh.to_crs(epsg=32629)

# creating a new GeoAxes pyplot figure

myFig = plt.figure(figsize=(10, 10))

myCRS = ccrs.UTM(29)  # telling plot to expect data in WGS84 UTM29.

# create an object of class Axes using UTM projection to tell pyplot where to plot data.
ax = plt.axes(projection=ccrs.UTM(29))

# use Cartopy ShapelyFeature class to draw polygons from shapefile geometries.
lgd_features = ShapelyFeature(lgd['geometry'], myCRS, edgecolor='k', facecolor='w', linewidth=0.75)
outline_feature = ShapelyFeature(outline['geometry'], myCRS, edgecolor='k', facecolor='none', linewidth=1)
neagh_feature = ShapelyFeature(neagh['geometry'], myCRS, edgecolor='k', facecolor='c', linewidth=0.75)

# use ax.plot() to draw point data for planning enforcement appeal decisions
appeal_handle = ax.plot(appeals.geometry.x, appeals.geometry.y, 's', color='red', ms=4, transform=myCRS)

ax.add_feature(outline_feature)  # add NI outline feature to map
ax.add_feature(lgd_features)  # add Local Government District boundaries to map
ax.add_feature(neagh_feature)  # add Lough Neagh water body to map

# Create new column for lgd geopandas dataframe

lgd['coords'] = lgd['geometry'].apply(lambda x: x.representative_point().coords[:])
lgd['coords'] = [coords[0] for coords in lgd['coords']]

ax.plot()
for idx, row in lgd.iterrows():
    plt.annotate(text=row['LGDNAME'], fontfamily='Arial Narrow', fontsize='x-small', xy=row['coords'],
                 horizontalalignment='center')

xmin, ymin, xmax, ymax = outline.total_bounds

# ax.set_extent([xmin, xmax, ymin, ymax], crs=myCRS)  # use shapefile feature boundary to zoom map to area of interest,
# with re-ordered coordinates due to  differing orders in total_bounds and set_extent.

# add legend

num_appeals = len(appeals.PAC_Decisi.unique())
print('Number of unique features: {}'.format(num_appeals))

appeal_colours = ['lime', 'red', 'grey', 'orangered', 'tomato']

appeal_outcomes = list(appeals.PAC_Decisi.unique())
appeal_outcomes.sort()

appeal_handles = generate_handles(appeals.PAC_Decisi.unique(), appeal_colours)

nice_appeals = []
for name in appeal_outcomes:
    nice_appeals.append(name.title())

handles = appeal_handles
labels = nice_appeals

leg = ax.legend(handles, labels, title='Enforcement Appeal Decisions', title_fontsize=10, fontsize=8, loc='upper left',
                frameon=True, framealpha=1)

gridlines = ax.gridlines(draw_labels=True, linestyle='--',
                         xlocs=[-8, -7, -6],
                         ylocs=[54.5, 55])
gridlines.right_labels = False # turn off the left-side labels
gridlines.top_labels = False  # turn off the bottom labels
ax.set_extent([xmin, xmax, ymin, ymax], crs=myCRS)

scale_bar(ax)

