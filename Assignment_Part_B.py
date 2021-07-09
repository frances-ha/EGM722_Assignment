# Add imports

import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from pyproj import Proj, transform
from shapely.geometry import Point
from cartopy.feature import ShapelyFeature
import cartopy.crs as ccrs

# plt.ion()  # Turn on interactive mode

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

# Create new column to process existing data and return new variable

def get_lgd_outcome():
    lgd_outcome = []

    for value in join['PAC_Decisi']:
        if value == "Allowed":  # if appeal outcome ('PAC_Decisi') is allowed, this is a "fail" for the LGD.
            lgd_outcome.append("Fail")
        else:
            lgd_outcome.append("Success")  # if appeal outcome is dismissed / withdrawn / varied / invalid (i.e. all
        # other values), this is a "success" for the LGD.

    join["LGD_Success_Fail"] = lgd_outcome
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

# Apply spatial join then inspect column names

join = gpd.sjoin(appeal_outcomes, lgd_wgs84, how='inner', lsuffix='left', rsuffix='right')
print(join.columns.values)

# Amend gdf to only display columns of interest to GIS analysis, then check output column names

cols_of_interest = ['Appeal_Ref', 'LGDNAME', 'PAC_Decisi']
join = join[cols_of_interest]
print(join.columns.values)

# Call function to create new column to summarise enforcement appeal outcomes into "Success" or "Failure" for LGD.

print(get_lgd_outcome())
print(join.head(10)) # quickly test if object has returned correct data

# -------------------------------------------------------------------------
# GIS ANALYSIS

# How many enforcement appeals have been determined in Northern Ireland since 2013?

total_appeals = new_join['PAC_Decisi'].count()
print('{} total enforcement appeals'.format(total_appeals)) # answer - 129

# How many unique values of appeal outcome are there, and what are these outcomes?

num_appeals = len(new_join.PAC_Decisi.unique())
print('{} unique classes of appeal outcome'.format(num_appeals)) # answer - 5

outcomes_list = get_unique_appeals(new_join.PAC_Decisi)
print('List of appeal outcomes: {}'.format(outcomes_list))

# What are the overall results of planning enforcement appeal outcomes in Northern Ireland?

print('Total numbers of each appeal outcome: {}'.format(appeal_totals()))

# Generate a list in descending order of total appeal cases dealt with per LGD

print('Enforcement appeals handled per LGD in descending order: {}'.format(lgd_appeals()))

# For each lgd, what is the percentage of allowed ("Failure") vs dismissed/varied/withdrawn ("Success")
# enforcement appeals?  Due to low test data numbers, use most prolific LGD (Newry, Mourne and Down aka NMD) as example


