import geopandas as gpd


# ---------------------------------------------------------------------------------------------------------------
# Define functions

def get_lgd_outcome():
    """This function uses the spatial join dataset to create a new column which processes existing appeal outcome
    data & returns new variable based on whether the appeal outcome is considered a successful or unsuccessful
    result for the local council. """

    lgd_outcome = []  # Initialise an empty list to be appended to the join gdf

    for value in join['PAC_Decisi']:
        if value == "Allowed":  # If appeal outcome ('PAC_Decisi') is allowed, this is a "fail" for the LGD.
            lgd_outcome.append("Fail")
        else:
            lgd_outcome.append("Success")  # If appeal outcome is dismissed / withdrawn / varied / invalid (i.e. all
        # other values), this is a "success" for the LGD.

    join["LGD_Success_Fail"] = lgd_outcome  # Add new column to gdf


def total_appeals():
    return join['PAC_Decisi'].count()


def num_appeals():
    return len(join.PAC_Decisi.unique())


def get_unique_appeals(decisions):
    """This function returns a list of all possible enforcement appeal outcomes from the input dataset by looping
        through a selected GeoDataFrame column.

        Parameters: decisions(gdf): GeoDataFrame column label.

        Returns: list of unique values. """

    unique = []  # Initialise empty list

    for outcome in decisions:  # Look at all elements of selected gdf series
        if outcome not in unique:  # Find any values that haven't been added to the unique list
            unique.append(outcome)  # Add these values to the list
    return unique


def appeal_totals():
    """This function is based on the key gdf column used in this analysis, 'PAC_Decisi', and uses the pandas value_count
    function to return a GeoSeries containing counts of unique values from this column in
    descending order.  This is used as a baseline to establish total numbers of enforcement appeal outcome
    across NI.  For consistency purposes the join gdf is used but the results do not relate to the spatially joined
    Local Government District boundaries."""

    return join['PAC_Decisi'].value_counts()


def lgd_appeals():
    """This function uses the value count function to extend the analysis by returning a GeoSeries containing counts of
    unique values from the 'LGDNAME' column attached to the spatially joined gdf.  This produces a list of enforcement
    appeals handled per LGD in descending order, with the most prolific local council at the top of the list."""

    return join['LGDNAME'].value_counts()


# -------------------------------------------------------------------------------------------------------------------
# Prepare test data for GIS analysis

# Load enforcement appeal data & LGD boundary data then check column names & CRS info

appeal_outcomes = gpd.read_file('DataFiles/appeal_points.shp')
print(appeal_outcomes.columns.values)
print(appeal_outcomes.crs)  # answer - epsg:4326

lgd = gpd.read_file('DataFiles/NI_LocalGovernmentDistricts.shp')
print(lgd.columns.values)
print(lgd.crs)  # answer - epsg:29902
lgd_wgs84 = lgd.to_crs(epsg=4326)  # Transform Irish Grid geometries to WGS84 lat-long coordinate reference system.

# Apply spatial join then inspect column names

join = gpd.sjoin(appeal_outcomes, lgd_wgs84, how='inner', lsuffix='left', rsuffix='right')
print(join.columns.values)

# Amend gdf to only display columns of interest to the GIS analysis, then check output column names

cols_of_interest = ['Appeal_Ref', 'LGDNAME', 'PAC_Decisi']
join = join[cols_of_interest]
print(join.columns.values)

# Call function to create new column that summarises enforcement appeal outcomes into two categories: "Success" or
# "Failure" for LGD.

print(get_lgd_outcome())

join.reset_index(inplace=True)  # Reset gdf index by setting a list of integers from 0 to length of data
join.sort_values(by=['index'], ascending=True, inplace=True)  # Sort index values in ascending order
print(join.head(10))  # Test if object has returned correct data

# -------------------------------------------------------------------------
# Spatial Analysis

# How many enforcement appeals have been determined in Northern Ireland since 2013?

print('{} total enforcement appeals'.format(total_appeals()))

# How many unique values of appeal outcome are there, and what are these outcomes?

print('{} unique classes of appeal outcome'.format(num_appeals()))
print('List of appeal outcomes: {}'.format(get_unique_appeals(join.PAC_Decisi)))

# What are the overall results of planning enforcement appeal outcomes in Northern Ireland?

print('Total numbers of each possible appeal outcome: {}'.format(appeal_totals()))

# Generate a list in descending order of total appeal cases dealt with per LGD

print('Enforcement appeals handled per LGD in descending order: {}'.format(lgd_appeals()))

# For each LGD, what is % of allowed ("Failure") vs dismissed/varied/withdrawn ("Success") enforcement appeals?
# N.B. due to low test data numbers, use most prolific LGD (Newry, Mourne and Down aka NMD) as example.

# Firstly, get total number of LGD cases by subsetting LGDNAME series
NMD = join.loc[join['LGDNAME'] == 'Newry, Mourne and Down']
print('total number of appeals is', len(NMD))
NMD_int = len(NMD)  # Convert outcome to numeric data by changing gdf to integer value

# Secondly, subset data to find the number of appeals that were successfully defended by the LGD
NMD_success = NMD.loc[NMD['LGD_Success_Fail'] == 'Success']
print('number of upheld appeal decisions is', len(NMD_success))
NMD_success_int = len(NMD_success)

# Thirdly, subset the same gdf to find the number of appeals lost by the LGD
NMD_fail = NMD.loc[NMD['LGD_Success_Fail'] == 'Fail']
print('number of appeals lost is', len(NMD_fail))
NMD_fail_int = len(NMD_fail)

# Finally, calculate percentages and print to screen.  Format specification is used to clean up the final outputs by
# reducing the numbers of decimal places printed to screen.

success_rate = (NMD_success_int / NMD_int) * 100
print('{:.2f} % success rate'.format(success_rate))

failure_rate = (NMD_fail_int / NMD_int) * 100
print('{:.2f} % failure rate'.format(failure_rate))
