# Add imports

import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from pyproj import Proj, transform
from shapely.geometry import Point
from cartopy.feature import ShapelyFeature
import cartopy.crs as ccrs

plt.ion()  # Turn on interactive mode

# Write functions

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

# Establish most and least prolific LGD for pursuing contested enforcement cases

def lgd_appeals():
    return join['LGDNAME'].value_counts()
# -----------------------------------------------------------
# PREPARE TEST DATA FOR GIS ANALYSIS

# Load enforcement appeal data & LGD boundary data then check column names & CRS info

appeal_outcomes = gpd.read_file('DataFiles/appeal_points.shp')
print(appeal_outcomes.columns.values)
print(appeal_outcomes.crs) # answer - epsg:4326

lgd = gpd.read_file('DataFiles/NI_LocalGovernmentDistricts.shp')
print(lgd.columns.values)
print(lgd.crs) # answer - epsg:29902
lgd_wgs84 = lgd.to_crs(epsg=4326)

# Apply spatial join then examine column names

join = gpd.sjoin(appeal_outcomes, lgd_wgs84, how='inner', lsuffix='left', rsuffix='right')
print(join.columns.values)

# Amend gdf to only display columns of interest, then check output column names

cols_of_interest = ['Appeal_Ref', 'LGDNAME', 'PAC_Decisi']
join = join[cols_of_interest]
print(join.columns.values)

# Create a new column

# -------------------------------------------------------------------------
# GIS ANALYSIS

# How many enforcement appeals have been determined in Northern Ireland since 2013?

total_appeals = join['PAC_Decisi'].count()
print('{} total enforcement appeals'.format(total_appeals)) # answer - 129

# How many unique values of appeal outcome are there, and what are these outcomes?

num_appeals = len(join.PAC_Decisi.unique())
print('{} unique classes of appeal outcome'.format(num_appeals)) # answer - 5

outcomes_list = get_unique_appeals(join.PAC_Decisi)
print('list of appeal outcomes: {}'.format(outcomes_list))

# What are the overall results of planning enforcement appeal outcomes in Northern Ireland?

print('total numbers of each appeal outcome: {}'.format(appeal_totals()))

# Generate a list in descending order of total appeal cases dealt with per LGD

print('Enforcement appeals handled per LGD in descending order: {}'.format(lgd_appeals()))
