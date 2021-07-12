#%%
import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.lines as mlines
from cartopy.feature import ShapelyFeature
import cartopy.crs as ccrs

# LOAD DATA
# load the datasets
towns = gpd.read_file('c:\\Users\\grego\\OneDrive\\01_GIS\\02_711_Principles\\Practical 1\\EGM711_Practical_1_data\\NI_towns.shp')
outline = gpd.read_file(r'c:\Users\grego\OneDrive\01_GIS\02_711_Principles\Practical 1\EGM711_Practical_1_data\NI_outline.shp') # add r before file path if not using '\\'
roads = gpd.read_file(r'c:\Users\grego\OneDrive\01_GIS\02_711_Principles\Practical 1\EGM711_Practical_1_data\NI_roads.shp') # add r before file path if not using '\\'

# CREATE A FIGURE
myFig = plt.figure(figsize=(10, 10))

# create a Universal Transverse Mercator reference system to transform our data.
myCRS = ccrs.UTM(29)

# createa an object of class Axes using a Mercator projection where to plot data
ax = plt.axes(projection=ccrs.UTM(29))

# DEFINE EXTENT

# using the boundary of the shapefile features, zoom the map to our area of interest
xmin, ymin, xmax, ymax = outline.total_bounds # assign the bounding box coords for outline to these variables
ax.set_extent([xmin, xmax, ymin, ymax], crs=myCRS)

# ADD NI OUTLINE

outline_feature = ShapelyFeature(outline['geometry'], myCRS, edgecolor='k', facecolor='w')
ax.add_feature(outline_feature)

# ADD ROADS (MOTORWAYS WILL BE OVERPLOTTED)

# pick 7 road colors
road_colors = ['firebrick', 'seagreen', 'royalblue', 'coral', 'violet', 'cornsilk','black']

# get a list of unique road classes
road_classes = list(roads.Road_class.unique())
road_classes.sort()
road_classes = road_classes[:-1] # removes the last road class when sorted, i.e. Motorways

# assign each road feature a color from the color list
for i, road_class in enumerate(road_classes):
    feat = ShapelyFeature(roads['geometry'][roads['Road_class'] == road_class], myCRS, edgecolor=road_colors[i], linewidth=1, alpha=1)
    ax.add_feature(feat)

# ADD MOTORWAYS

motorway = roads[roads['Road_class'] == 'MOTORWAY']
motorway_feat = ShapelyFeature(motorway['geometry'], myCRS, edgecolor='k', linewidth=4, alpha=1)
ax.add_feature(motorway_feat)

# ADD TOWNS

# add town markers
town_handle = ax.plot(towns.geometry.x, towns.geometry.y, 'bo', color='b', ms=6, transform=myCRS)

# add the text labels for the towns
for i, row in towns.iterrows():
    x, y = row.geometry.x, row.geometry.y
    plt.text(x, y, row['TOWN_NAME'].title(), backgroundcolor='w',  bbox=dict(boxstyle='square', fc='w', ec='none'), fontsize=8, transform=myCRS) # use plt.text to place a label at x,y'''

# LEGEND PREP

# generate matplotlib handles to create a legend of features

def generate_handles(labels, colors, alpha=1):
    lc = len(colors) # get length of colors list
    handles = []
    for i in range(len(labels)):
        handles.append(mlines.Line2D([0, 1], [0, 1], linestyle='-', color=colors[i % lc], alpha=alpha))
    return handles

# Define handles and labels for all features

road_handles = generate_handles(road_classes, road_colors, alpha=1)

road_labels = [name.title() for name in road_classes]

motorway_handle = [mlines.Line2D([],[],linewidth=4, linestyle='-', color='k')]

# ADD LEGEND 

# ax.legend() takes a list of handles and a list of labels corresponding to the objects you want to add to the legend
# order of features in the handles list and labels list must be the same

handles = town_handle + road_handles + motorway_handle
labels = ['Towns'] + road_labels + ['Motorway']

leg = ax.legend(handles, labels, title='Legend', title_fontsize=14, fontsize=12, loc='upper left', frameon=True, framealpha=1)

# ADD SCALEBAR

# create a scalebar in the bottom left corner of the map

def scale_bar(ax, location=(0.15, 0.05)):
    llx0, llx1, lly0, lly1 = ax.get_extent(ccrs.PlateCarree())
    sbllx = (llx1 + llx0) / 2
    sblly = lly0 + (lly1 - lly0) * location[1]

    tmc = ccrs.TransverseMercator(sbllx, sblly)
    x0, x1, y0, y1 = ax.get_extent(tmc)
    sbx = x0 + (x1 - x0) * location[0]
    sby = y0 + (y1 - y0) * location[1]

    plt.plot([sbx, sbx - 20000], [sby, sby], color='k', linewidth=9, transform=tmc)
    plt.plot([sbx, sbx - 10000], [sby, sby], color='k', linewidth=6, transform=tmc)
    plt.plot([sbx-10000, sbx - 20000], [sby, sby], color='w', linewidth=6, transform=tmc)

    plt.text(sbx, sby-4500, '20 km', transform=tmc, fontsize=8)
    plt.text(sbx-12500, sby-4500, '10 km', transform=tmc, fontsize=8)
    plt.text(sbx-24500, sby-4500, '0 km', transform=tmc, fontsize=8)

scale_bar(ax)

plt.show()

# %%
