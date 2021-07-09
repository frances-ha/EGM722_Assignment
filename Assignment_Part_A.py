# Add imports

import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from matplotlib import font_manager, rcParams
import numpy as np
from pyproj import Proj, transform
from shapely.geometry import Point
from cartopy.feature import ShapelyFeature
import cartopy.crs as ccrs

plt.ion()  # turn on interactive mode


# Define functions at top of script to prevent interpreter from throwing errors when attempting to evaluate commands
# that haven't yet been written.

# Establish range of possible enforcement appeal outcomes

def get_unique_appeals(decisions):
    unique = []

    for outcome in decisions:
        if outcome not in unique:
            unique.append(outcome)
    return unique


# Establish total numbers of each appeal outcome across Northern Ireland
def appeal_totals():
    return join['PAC_Decisi'].value_counts()


# Establish most and least prolific local government district for pursuing contested enforcement cases
def lgd_appeals():
    return join['LGDNAME'].value_counts()

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
print(df.columns)  # show current order of dataframe columns
df = df.reindex(columns=['level_0', 'index', 'Appeal_Reference', 'Departmental_Reference',
                         'Development_Description', 'House_Number', 'Street_Name', 'Postcode',
                         'Decision_Date', 'PAC_Decision_Outcome', 'X', 'Y', 'X1', 'Y1',
                         'geometry'])

print(df.head())
df['geometry'] = list(zip(df['X1'], df['Y1']))
df['geometry'] = df['geometry'].apply(Point)
# del df['X'], df['Y']
print(df.head())

appeals = gpd.GeoDataFrame(df)  # converting AppealDecisions.csv pandas data frame into a GeoDataFrame.
appeals.set_crs("EPSG:4326", inplace=True)  # csv XYs are in Irish Grid, these need to be reprojected to WGS84 lat-long
print(appeals.head())
appeals.to_file('DataFiles/appeal_points.shp')

# Load shapefile data

outline = gpd.read_file('DataFiles/NI_outline.shp')
lgd = gpd.read_file('DataFiles/NI_LocalGovernmentDistricts.shp')
water = gpd.read_file('DataFiles/NI_Water_Bodies.shp')
appeals = gpd.read_file('DataFiles/appeal_points.shp')

# Export only Lough Neagh polygon from NI_Water_Bodies.shp to a new shapefile for display in a simplified map

neagh = water.head(1)
neagh.to_file('DataFiles/lough_neagh.shp')
neagh = gpd.read_file('DataFiles/lough_neagh.shp')

# transform all shapefile geometries to appropriate projected crs for display in mapping output plot.
# WGS84 UTM (Zone 29) is good for large-scale mapping especially when a small region such as NI fits within one
# of the 60 zones in the UTM projection.

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

# use ax.plot() to draw point data for planning enforcement appeal decisions based on PAC Decision column

dismissed_handle = ax.plot(appeals[appeals['PAC_Decisi'] == 'Dismissed'].geometry.x,
                           appeals[appeals['PAC_Decisi'] == 'Dismissed'].geometry.y, 's', color='red', ms=4,
                           transform=myCRS)

withdrawn_handle = ax.plot(appeals[appeals['PAC_Decisi'] == 'Withdrawn'].geometry.x,
                           appeals[appeals['PAC_Decisi'] == 'Withdrawn'].geometry.y, 's', color='firebrick', ms=4,
                           transform=myCRS)

varied_handle = ax.plot(appeals[appeals['PAC_Decisi'] == 'Varied'].geometry.x,
                        appeals[appeals['PAC_Decisi'] == 'Varied'].geometry.y, 's', color='indianred', ms=4,
                        transform=myCRS)

notvalid_handle = ax.plot(appeals[appeals['PAC_Decisi'] == 'NotValid'].geometry.x,
                          appeals[appeals['PAC_Decisi'] == 'NotValid'].geometry.y, 's', color='rosybrown', ms=4,
                          transform=myCRS)

allowed_handle = ax.plot(appeals[appeals['PAC_Decisi'] == 'Allowed'].geometry.x,
                         appeals[appeals['PAC_Decisi'] == 'Allowed'].geometry.y, 's', color='limegreen', ms=4,
                         transform=myCRS)

ax.add_feature(outline_feature)  # add NI outline feature to map
ax.add_feature(lgd_features)  # add Local Government District boundaries to map
ax.add_feature(neagh_feature)  # add Lough Neagh water body to map

# Create new column for lgd geopandas dataframe to prepare for lgd labels

lgd['coords'] = lgd['geometry'].apply(lambda x: x.representative_point().coords[:])
lgd['coords'] = [coords[0] for coords in lgd['coords']]

# GIS ANALYSIS

# apply spatial join to appeal decisions and lgd boundary shapefiles

join = gpd.sjoin(appeals, lgd, how='inner', lsuffix='left', rsuffix='right')

# find out the total number of enforcement appeals in NI

total_appeals = join['PAC_Decisi'].count()
print('{} total enforcement appeals'.format(total_appeals))

# get total number of unique decision outcomes

num_appeals = len(join.PAC_Decisi.unique())
print('{} unique classes of appeal outcome'.format(num_appeals))

# list unique appeal outcomes

outcomes = get_unique_appeals(join.PAC_Decisi)
order = [0, 3, 2, 4, 1]
appeals_list = [outcomes[i] for i in order]
print(appeals_list)

# What are the overall results of planning enforcement appeals in Northern Ireland?

print(appeal_totals())

# generate a list in descending order of planning authorities and corresponding numbers of enforcement appeal cases

print(lgd_appeals())

# for each lgd, what is the percentage of allowed vs dismissed/varied/withdrawn enforcement appeals?

# firstly, create a new gdf with reduced information

cols_of_interest = ['Appeal_Ref', 'LGDNAME', 'PAC_Decisi']
gis_analysis = join[cols_of_interest]
print(gis_analysis.head())

gis_analysis = gis_analysis.assign(LGD_Success_Fail = gis_analysis['PAC_Decisi'])
gis_analysis.loc[gis_analysis['PAC_Decisi'] == 'Dismissed', 'LGD_Success_Fail'] = 'Success'
gis_analysis.loc[gis_analysis['PAC_Decisi'] == 'Withdrawn', 'LGD_Success_Fail'] = 'Success'
gis_analysis.loc[gis_analysis['PAC_Decisi'] == 'Varied', 'LGD_Success_Fail'] = 'Success'
gis_analysis.loc[gis_analysis['PAC_Decisi'] == 'Notvalid', 'LGD_Success_Fail'] = 'Success'
gis_analysis.loc[gis_analysis['PAC_Decisi'] == 'Allowed', 'LGD_Success_Fail'] = 'Fail'

gis_analysis = gis_analysis.drop(columns="PAC_Decisi")

# use most prolific LGD (Newry, Mourne and Down aka NMD) as example


# could i plot pie charts of these percentages on the map?


ax.plot()
for idx, row in lgd.iterrows():
    plt.annotate(text=row['LGDNAME'], fontfamily='Arial Narrow', fontsize='x-small', xy=row['coords'],
                 horizontalalignment='center')

xmin, ymin, xmax, ymax = outline.total_bounds

# add legend

appeal_handles = dismissed_handle + withdrawn_handle + varied_handle + notvalid_handle + allowed_handle

handles = appeal_handles
labels = appeals_list

leg = ax.legend(handles, labels, title='Enforcement Appeal Decisions', title_fontsize=10, fontsize=8, loc='upper left',
                frameon=True, framealpha=1)

gridlines = ax.gridlines(draw_labels=True, linestyle='--',
                         xlocs=[-8, -7, -6],
                         ylocs=[54.5, 55])
gridlines.right_labels = False  # turn off the left-side labels
gridlines.top_labels = False  # turn off the bottom labels
ax.set_extent([xmin, xmax, ymin, ymax], crs=myCRS)

scale_bar(ax)
