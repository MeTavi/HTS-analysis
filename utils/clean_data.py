import pandas as pd
import numpy as np
import os
import geopandas as gpd

def persiIDAdj(table):
    table['PERSID'] = table['PERSID'].str.replace('/','')
    return table

def CleanHousehold(HOUSEHOLDS, ASGS, zones, HH):
    Household = HOUSEHOLDS.copy()
    Household = Household.astype({'HHID':'int64'})
    Household = pd.merge(Household, ASGS, left_on = 'HOME_SA1_2016', right_on = 'SA1_7DIGITCODE_2016')

    """Spatial Join to Model Sectors"""
    Household_map = gpd.GeoDataFrame(Household, geometry=gpd.points_from_xy(Household['HOMELONG'], Household['HOMELAT']), crs='EPSG:4283')

    # Atousa Modification:
    Household_map = gpd.sjoin(Household_map, zones[['geometry','LvL4_ID', 'LvL3_ID', 'LvL2_ID', 'LvL1_ID', 'Dist_ID','BSTM','SEQSTM']],
     how = 'left', op = 'within').drop(columns ='index_right')#.astype({'LvL4_ID':int, 'LvL3_ID':int, 'LvL2_ID':int, 'LvL1_ID': int, 'Dist_ID':int})

    # Household_map = gpd.sjoin(Household_map, zones[['geometry','LvL4_ID', 'LvL3_ID', 'LvL2_ID', 'LvL1_ID', 'Dist_ID']],
    # how = 'left', op = 'within').drop(columns ='index_right')#.astype({'LvL4_ID':int, 'LvL3_ID':int, 'LvL2_ID':int, 'LvL1_ID': int, 'Dist_ID':int})


    Household = pd.DataFrame(Household_map).drop(columns = 'geometry')
    Household.rename(columns = {'LvL4_ID':'Home_LvL4', 'LvL3_ID':'Home_LvL3', 'LvL2_ID':'Home_LvL2', 'LvL1_ID':'Home_LvL1', 
    'Dist_ID':'Home_Dist', 'SA2_NAME_2016':'HH_SA2', 'SA3_NAME_2016': 'HH_SA3', 'SA4_NAME_2016': "HH_SA4", 'LGA_NAME_2016': "HH_LGA"}, inplace = True)

    Household.drop(columns=['SA1_7DIGITCODE_2016', 'SA2_5DIGITCODE_2016', 'SA3_CODE_2016', 'SA4_CODE_2016'], inplace=True)

    #district_plot = district.plot(figsize=(40,20))
    #zone_plot = zones.plot(column = 'BSTM', figsize=(40,20),cmap= 'Pastel2')
    #hh_map = Household_map.plot(column = 'LGA_NAME_2016', ax = zone_plot, marker = ",", markersize=2,cmap='OrRd', legend = True)#coolwarm
    #hh_map.savefig('HH_map.pdf')
    #del Household_map, zone_plot, hh_map

    print('Number of Household Records in Original: {}'.format(len(HOUSEHOLDS.axes[0])))
    print('Number of Household Records: {}'.format(len(Household.axes[0])))

    """Update Household Weights"""
    Household['old_HHWGT_19'] = Household['HHWGT_19']
    Household = Household.set_index("HHID")
    Household.update(HH.set_index('HHID'))
    Household.reset_index(inplace=True)

    print("LGA Weighting Population: {}".format(Household.old_HHWGT_19.sum().round(0)))
    print("Sector Weighting Population: {}".format(Household.HHWGT_19.sum().round(0)))

    del Household_map
    Household[['HH_LGA','old_HHWGT_19','HHWGT_19']].groupby(by='HH_LGA').agg(['count', 'sum']).round(0)
    return Household


def CleanPerson(PERSONS, Household, ANZSCO_filter, Pers):
    Person = PERSONS.copy()

    Person = Person.astype({'HHID':'int64', "PERSID": 'int64', 'ANZSCO_1-digit': int, 'ANZSCO_3-digit': 'int64'}).sort_values('HHID')

    # Atousa Modification:
    Person = pd.merge(Person, Household[['HHID', 'HH_SA2', 'HH_SA3', 'HH_SA4', 'HH_LGA',
    'Home_LvL4', 'Home_LvL3', 'Home_LvL2', 'Home_LvL1', 'Home_Dist', 'BSTM']], left_on = 'HHID', right_on = 'HHID', how = 'left')

    # Person = pd.merge(Person, Household[['HHID', 'HH_SA2', 'HH_SA3', 'HH_SA4', 'HH_LGA',
    # 'Home_LvL4', 'Home_LvL3', 'Home_LvL2', 'Home_LvL1', 'Home_Dist']], left_on = 'HHID', right_on = 'HHID', how = 'left')

    """Fix Random Errors Here."""
    Person.loc[Person.PERSID == 613521001,'ANZSCO_1-digit'] = 2
    Person.loc[Person.PERSID == 613521001,'ANZSCO_3-digit'] = 200
    #twb
    Person.loc[Person.PERSID == 766731002, 'ANZSCO_3-digit'] = 800
    Person.loc[Person.PERSID == 766731001, 'ANZSCO_3-digit'] = 141
    Person.loc[Person.PERSID == 782701000, 'ANZSCO_3-digit'] = 500

    Person.replace(['primary','secondary'],['Primary','Secondary'], inplace=True)
    """Fix Random Errors Here."""

    """Add Collar Tag."""
    Person = pd.merge(Person, ANZSCO_filter[['ANZSCO_3','Collar', 'Collar2']], left_on = 'ANZSCO_3-digit', right_on = 'ANZSCO_3', how = 'left').drop(columns= 'ANZSCO_3').sort_values('HHID').drop_duplicates().dropna(axis = 0, thresh = 5)

    Person = Person.reset_index().drop(columns = 'index')
    Person = Person.astype({'HHID':'int64', "PERSID": 'int64', 'ANZSCO_1-digit': int, 'ANZSCO_3-digit': 'int64'}).sort_values('HHID')

    """Update New Person Weights."""
    Person['old_PERSWGT19'] = Person['PERSWGT19']
    Person = Person.set_index("PERSID")
    Person.update(Pers.set_index('PERSID'))
    Person.reset_index(inplace=True)

    print('Number of Person Records in Original: {}'.format(len(PERSONS.axes[0])))
    print('Number of Person Records: {}'.format(len(Person.axes[0])))

    return Person