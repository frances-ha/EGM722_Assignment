import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from pyproj import Proj, transform
from shapely.geometry import Point
from cartopy.feature import ShapelyFeature
import cartopy.crs as ccrs

plt.ion()  # Turn on MatPlotLib interactive mode


# ---------------------------------------------------------------------------------------------------------------------
# Define functions

def get_unique_appeals(decisions):
    """This function returns a list of all possible enforcement appeal outcomes from the input dataset by looping
    through a selected GeoDataFrame column.

    Parameters: decisions(gdf): GeoDataFrame column label.

    Returns: list of unique values. """

    unique = []  # Initialise an empty list

    for outcome in decisions:  # Look at all elements of selected gdf column
        if outcome not in unique:  # Find any values that haven't been added to the unique list
            unique.append(outcome)  # Add these values to the list
    return unique


def scale_bar(ax, location=(0.15, 0.1)):
    """"This function creates a scale bar to be displayed at a specified location on the map output.

    Parameters: ax: axes to draw scale bar on;
                location: centre of scale bar in axis coordinates - in this case we want the scale bar to be located
                at the bottom left of the map. """

    llx0, llx1, lly0, lly1 = ax.get_extent(ccrs.PlateCarree())  # Get limits of axis in lat-long
    # Different options exist for selecting a coordinate reference system in Cartopy. In this case we choose the
    # default option, PlateCarree, which is a grid of equal rectangles with less distortion than e.g. Mercator.

    sbllx = (llx1 + llx0) / 2
    sblly = lly0 + (lly1 - lly0) * location[1]
    tmc = ccrs.TransverseMercator(sbllx, sblly)  # Use Transverse Mercator Projection (tmc) to position scale bar on
    # map using horizontal and vertical scale bar locations

    x0, x1, y0, y1 = ax.get_extent(tmc)  # Get extent of plotted area in coordinates in metres

    # Turn specified scale bar location into coordinates in metres
    sbx = x0 + (x1 - x0) * location[0]
    sby = y0 + (y1 - y0) * location[1]

    plt.plot([sbx, sbx - 20000], [sby, sby], color='k', linewidth=9, transform=tmc)
    plt.plot([sbx, sbx - 10000], [sby, sby], color='k', linewidth=6, transform=tmc)
    plt.plot([sbx - 10000, sbx - 20000], [sby, sby], color='w', linewidth=6, transform=tmc)

    plt.text(sbx, sby - 4500, '20 km', transform=tmc, fontsize=8)
    plt.text(sbx - 12500, sby - 4500, '10 km', transform=tmc, fontsize=8)
    plt.text(sbx - 24500, sby - 4500, '0 km', transform=tmc, fontsize=8)


# --------------------------------------------------------------------------------------------------------------------
# Prepare data

# Create new shapefile of test data from csv file.

df = pd.read_csv('DataFiles/PlanningEnforcement_AppealDecisions.csv')
inProj, outProj = Proj("epsg:29902"), Proj("epsg:4326")
df['Y1'], df['X1'] = transform(inProj, outProj, df['X'].tolist(), df['Y'].tolist())  # Transform TM65 Irish Grid coords
# (EPSG:29902) into WGS84 (EPSG: 4326) lat-long coordinates and create columns in df containing new XY lists.

# df.reset_index(inplace=True)  # Reset the index of the original dataframe by generating a new index label with default
# name "level_0" which is added to dataframe.
print(df.columns)  # Show current order of dataframe columns.
df = df.reindex(columns=['Appeal_Reference', 'Departmental_Reference', 'Development_Description', 'House_Number',
                         'Street_Name', 'Postcode', 'Decision_Date', 'PAC_Decision_Outcome', 'X', 'Y', 'X1', 'Y1',
                         'geometry'])  # Re-order dataframe so that new transformed X1 & Y1 lists read concurrently.
# delete excessive columns? del df['X'], df['Y'] ?

df['geometry'] = list(zip(df['X1'], df['Y1']))
df['geometry'] = df['geometry'].apply(Point)

appeals = gpd.GeoDataFrame(df)  # Convert test data to GeoDataFrame.
appeals.set_crs("EPSG:4326", inplace=True)  # Set gdf coordinate reference system to WGS84 lat-long.
appeals.to_file('DataFiles/appeal_points.shp')  # Save new gdf as shapefile.

# Load shapefile data

outline = gpd.read_file('DataFiles/NI_outline.shp')
lgd = gpd.read_file('DataFiles/NI_LocalGovernmentDistricts.shp')
water = gpd.read_file('DataFiles/NI_Water_Bodies.shp')
appeals = gpd.read_file('DataFiles/appeal_points.shp')

# Export only Lough Neagh polygon from NI_Water_Bodies.shp to a new shapefile for display in simplified map

neagh = water.head(1)
neagh.to_file('DataFiles/lough_neagh.shp')
neagh = gpd.read_file('DataFiles/lough_neagh.shp')

# Transform all shapefile geometries to appropriate projected crs for display in mapping output plot.  WGS84 UTM Zone 29
# is appropriate for large scale mapping, esp because NI fits completely inside Zone 29 of the 60 projected zones.

appeals = appeals.to_crs(epsg=32629)
outline = outline.to_crs(epsg=32629)
lgd = lgd.to_crs(epsg=32629)
neagh = neagh.to_crs(epsg=32629)

# --------------------------------------------------------------------------------------------------------------------
# Prepare map

myFig = plt.figure(figsize=(10, 10))  # Create a new GeoAxes PyPlot figure

myCRS = ccrs.UTM(29)  # Tell plot to expect data in WGS84 UTM29.

# Create an object of class Axes using UTM projection to tell PyPlot where to plot data.
ax = plt.axes(projection=ccrs.UTM(29))

# Use Cartopy ShapelyFeature class to draw polygons from shapefile geometries.
lgd_features = ShapelyFeature(lgd['geometry'], myCRS, edgecolor='k', facecolor='w', linewidth=0.75)
outline_feature = ShapelyFeature(outline['geometry'], myCRS, edgecolor='k', facecolor='none', linewidth=1)
neagh_feature = ShapelyFeature(neagh['geometry'], myCRS, edgecolor='k', facecolor='c', linewidth=0.75)

# Use ax.plot() to draw point data for planning enforcement appeal decisions based on the 'Planning Appeals Commission
# (PAC) Decision' column, n.b. this has been shortened by Geopandas to 'PAC_Decisi'.

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

ax.add_feature(outline_feature)  # Add NI outline feature to map
ax.add_feature(lgd_features)  # Add Local Government District boundaries to map
ax.add_feature(neagh_feature)  # Add Lough Neagh water feature to map

# Set up labelling so that each local government district (lgd) polygon will have a label on the map.  This section of
# code is based on the following Stack Overflow page:
# https://stackoverflow.com/questions/38899190/geopandas-label-polygons

lgd['coords'] = lgd['geometry'].apply(lambda x: x.representative_point().coords[:])  # Create new 'coords' column
# using Shapely representative point method which returns a column (GeoSeries) of points guaranteed to be within
# the geometry of each polygon object.
lgd['coords'] = [coords[0] for coords in lgd['coords']]

# List unique appeal outcomes

outcomes = get_unique_appeals(appeals.PAC_Decisi)
order = [0, 2, 4, 3, 1]
appeals_list = [outcomes[i] for i in order]

ax.plot()
for idx, row in lgd.iterrows():
    plt.annotate(text=row['LGDNAME'], fontsize='x-small', xy=row['coords'], horizontalalignment='center')

xmin, ymin, xmax, ymax = outline.total_bounds

# Add legend

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
