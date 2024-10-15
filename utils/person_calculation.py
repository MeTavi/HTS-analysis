import pandas as pd
import numpy as np
import os
import geopandas as gpd

def cal_cc_kid(TRIPS, Person):
    trip_rev = TRIPS.copy()
    kindy_pers = Person.copy()

    """Age Bands."""
    # under5 = kindy_pers.AGE < 5
    under5 = kindy_pers.AGE_cat == 1

    """Processing."""
    duration = trip_rev.DURATION > 90
    DEST_CC_kindy = trip_rev.DESTPLACE == 'Childcare or kindergarten'
    DEST_prim_sec = trip_rev.DESTPLACE == 'Primary or secondary school'

    # CC_person = trip_rev[['PERSID',"HHID", "DESTPLACE", "DURATION"]].loc[duration & DEST_CC_kindy,['PERSID']].drop_duplicates().astype({'PERSID': 'int64'})
    CC_person = trip_rev[['PERSID',"HHID", "DESTPLACE", "DURATION"]].loc[duration & (DEST_CC_kindy | DEST_prim_sec),['PERSID']].drop_duplicates().astype({'PERSID': 'int64'})

    CC_person['CC/Kindy'] = 1

    kindy_pers = pd.merge(kindy_pers, CC_person, on='PERSID', how='left')
    CC_person = kindy_pers["CC/Kindy"] == 1
    not_CC_kid = kindy_pers.STUDYING != 'CC/Kindy'

    kindy_pers.loc[CC_person & under5 & not_CC_kid,'STUDYING'] = 'CC/Kindy'
    # kindy_pers.loc[CC_person & under5 & not_CC_kid,'Student_Prim'] = 0
    # kindy_pers.loc[CC_person & under5 & not_CC_kid,'Student_CC'] = 1
    print("Number of Added Kindy Kids:{}".format(len(kindy_pers.loc[CC_person & under5 & not_CC_kid])))
    kindy_pers.drop(columns=['CC/Kindy'], inplace = True)

    PrimSchl = kindy_pers.STUDYING == 'Primary'
    SecSchl = kindy_pers.STUDYING == 'Secondary'
    UniFT = kindy_pers.STUDYING == 'tertiaryFullTime'
    UniPT = kindy_pers.STUDYING == 'tertiaryPartTime'
    kindy_pers.loc[(PrimSchl | SecSchl | UniFT | UniPT) & under5,'STUDYING'] = "CC/Kindy"

    #Assign Kindy
    kindy = kindy_pers.STUDYING == 'CC/Kindy'
    # kindy_pers.loc[kindy, 'Student_CC'] = 1
    kindy_pers.loc[kindy, 'Student_type'] = 1


    Person = kindy_pers
    del trip_rev, kindy_pers, kindy, not_CC_kid, under5, duration, DEST_CC_kindy, CC_person
    return Person



def cal_prim(TRIPS, Person):
    trip_rev = TRIPS.copy()
    school_pers = Person.copy()
    school_pers['STUDYING'].replace({'other': 0}, inplace = True)

    """Age Bands."""
    under6 = school_pers.AGE < 5
    over5 = school_pers.AGE >= 5
    under13 = school_pers.AGE < 13
    """Processing."""
    duration = trip_rev.DURATION > 90
    # zero_study = school_pers.STUDYING == 0
    DEST_prim= trip_rev.DESTPLACE == 'Primary or secondary school'

    prim_person = trip_rev.loc[DEST_prim & duration,['PERSID']].drop_duplicates().astype({'PERSID': 'int64'})
    prim_person['Prim_person'] = 1
    school_pers = pd.merge(school_pers, prim_person, on='PERSID', how='left')
    missing = school_pers.STUDYING == 0

    prim_missing = school_pers.Prim_person == 1

    school_pers.loc[missing & prim_missing & over5 & under13, 'STUDYING'] = 'Primary'
    # school_pers.loc[missing & prim_missing & under6, 'STUDYING'] = 'CC/Kindy'
    print("Number of Added Kindy Kids:{}".format(len(school_pers.loc[missing & prim_missing & under6])))
    print("Number of Added Primary Kids:{}".format(len(school_pers.loc[missing & prim_missing & over5 & under13])))

    school_pers.drop(columns = 'Prim_person', inplace = True)

    Person = school_pers

    del school_pers, prim_person, prim_missing, DEST_prim, under6, over5, under13, trip_rev, missing
    return Person


def cal_study_tag(Person):
    pers_filt = Person.copy()

    """Age Bands."""
    over5 = pers_filt.AGE > 4
    under5 = pers_filt.AGE < 5
    under18 = pers_filt.AGE < 18
    over15 = pers_filt.AGE > 14
    sub75 = pers_filt.AGE < 75
    over75 = pers_filt.AGE > 74
    under15 = pers_filt.AGE < 15
    over20 = pers_filt.AGE > 20
    o13 = pers_filt.AGE > 12
    u13 = pers_filt.AGE < 13

    """Clean Studying Var."""
    PrimSchl = pers_filt.STUDYING == 'Primary'
    SecSchl = pers_filt.STUDYING == 'Secondary'
    UniFT = pers_filt.STUDYING == 'tertiaryFullTime'
    UniPT = pers_filt.STUDYING == 'tertiaryPartTime'
    # CC_kindy = pers_filt.MAINACT == 'Childcare/Kindergarten'

    # # print('CC/Kindy')
    # # print(pers_filt.loc[CC_kindy,['STUDYING','AGE']].value_counts())
    # pers_filt.loc[CC_kindy,'STUDYING'] = "CC/Kindy"
    # # print("Primary to Kindy")
    # # print(pers_filt.loc[PrimSchl & under5, ['STUDYING','AGE']].value_counts())
    # pers_filt.loc[(PrimSchl | SecSchl | UniFT | UniPT) & under5,'STUDYING'] = "CC/Kindy"
    # # print("Primary to Secondary")
    # # print(pers_filt.loc[PrimSchl & o13, ['STUDYING','AGE']].value_counts())
    pers_filt.loc[PrimSchl & o13,'STUDYING'] = 'Secondary'
    # print("Adult Secondary")
    # print(pers_filt.loc[SecSchl & over20, ['STUDYING','AGE']].value_counts())
    pers_filt.loc[SecSchl & over20,'STUDYING'] = 0
    # print("Secondary to Primary")
    # print(pers_filt.loc[SecSchl & u13, ['STUDYING','AGE']].value_counts())
    pers_filt.loc[(SecSchl| UniFT | UniPT) & u13,'STUDYING'] = 'Primary'
    # print('Uni errors')
    # print(pers_filt.loc[UniFT & u13, ['STUDYING','AGE']].value_counts())
    pers_filt.loc[UniFT & u13,'STUDYING'] = 0
    # print(pers_filt.loc[UniPT & u13, ['STUDYING','AGE']].value_counts())
    pers_filt.loc[UniPT & u13,'STUDYING'] = 0

    #fig = px.histogram(pers_filt[['STUDYING',"MAINACT",'AGE']], x="AGE", color="STUDYING", marginal = "rug", hover_data=['MAINACT']);fig.show()
    """Assign Study Vars."""
    PrimSchl = pers_filt.STUDYING == 'Primary'
    SecSchl = pers_filt.STUDYING == 'Secondary'
    TertPT = pers_filt.STUDYING == 'tertiaryFullTime'
    TertFT = pers_filt.STUDYING == 'tertiaryPartTime'

    # pers_filt.loc[PrimSchl, 'Student_Prim'] = 1
    # pers_filt.loc[SecSchl, 'Student_Sec'] = 1
    # pers_filt.loc[TertPT | TertFT, 'Student_Tert'] = 1
    # pers_filt.loc[PrimSchl | SecSchl | TertPT | TertFT, 'Student'] = 1
    pers_filt.loc[PrimSchl, 'Student_type'] = 2
    pers_filt.loc[SecSchl, 'Student_type'] = 3
    pers_filt.loc[TertPT | TertFT, 'Student_type'] = 4
    pers_filt.loc[PrimSchl | SecSchl | TertPT | TertFT, 'Student_type'] = 5

    return pers_filt

def cal_work_tag(pers_filt):

    """Age Bands."""
    # over5 = pers_filt.AGE > 4
    # under5 = pers_filt.AGE < 5
    # under18 = pers_filt.AGE < 18
    over15 = pers_filt.AGE > 14
    # sub75 = pers_filt.AGE < 75
    # over75 = pers_filt.AGE > 74
    under15 = pers_filt.AGE < 15
    # over20 = pers_filt.AGE > 20
    # o13 = pers_filt.AGE > 12
    # u13 = pers_filt.AGE < 13

    """Clean Worker Variable."""
    retired = pers_filt.WORKSTATUS == 'retired'
    PrimSchl = pers_filt.STUDYING == 'Primary'
    Not_PrimSchl = pers_filt.STUDYING != 'Primary'

    #display(pers_filt.loc[PrimSchl| retired | under15, ['Collar','AGE']].plot.hist(bins=20))
    # pers_filt.loc[PrimSchl| retired | under15,'Collar'] = np.NaN
    pers_filt.loc[retired,'Collar'] = np.NaN

    white = pers_filt.Collar == 'White'
    blue = pers_filt.Collar == 'Blue'

    """Assign Worker vs Dependents."""
    workFT = pers_filt.WORKSTATUS == 'workFullTime'
    workPT = pers_filt.WORKSTATUS == 'workPartTime'
    non_workFT = pers_filt.WORKSTATUS != 'workFullTime'
    non_workPT = pers_filt.WORKSTATUS != 'workPartTime'

    pers_filt.loc[(non_workFT & non_workPT) | PrimSchl | under15, 'Dependent'] = 1
    pers_filt.loc[(workFT | workPT) & Not_PrimSchl & over15, 'Worker'] = 1
    worker = pers_filt.Worker == 1

    # pers_filt.loc[worker & white, 'Worker_White'] = 1
    # pers_filt.loc[worker & blue, 'Worker_Blue'] = 1

    pers_filt.loc[worker & white, 'Worker_wb'] = 2
    pers_filt.loc[worker & blue, 'Worker_wb'] = 1

    return pers_filt

def cal_ageCat(pers_filt):
    """Apply Age Categories."""
    u15 = pers_filt.AGE < 15
    o15 = pers_filt.AGE > 14

    u30 = pers_filt.AGE < 30
    o30 = pers_filt.AGE > 29

    u50 = pers_filt.AGE < 50
    o50 = pers_filt.AGE > 49

    u75 = pers_filt.AGE < 75
    o75 = pers_filt.AGE > 74

    pers_filt.loc[u15, '0-14'] = 1
    pers_filt.loc[o15 & u30, '15-29'] = 1
    pers_filt.loc[o30 & u50, '30-49'] = 1
    pers_filt.loc[o50 & u75, '50-74'] = 1
    pers_filt.loc[o75, '75+'] = 1

    pers_filt.loc[u15,'Age_cat'] = '0-14'
    pers_filt.loc[o15 & u30,'Age_cat'] =  '15-29'
    pers_filt.loc[o30 & u50,'Age_cat'] =  '30-49'
    pers_filt.loc[o50 & u75,'Age_cat'] =  '50-74'
    pers_filt.loc[o75,'Age_cat'] =  '75+'


    #Missing Record Check
    pers_filt.fillna(0, inplace = True)
    pers_filt['check'] = pers_filt['Worker'] + pers_filt['Dependent']
    print('ERRORS PRESENT:{} Person Records without Variable attached'.format(pers_filt[pers_filt.check!=1].PERSID.count()))
    print('REVIEW PERSID:{} '.format(pers_filt[pers_filt.check!=1].PERSID.to_list()))
    pers_filt.drop(columns = ['check'], inplace = True)

    Person = pers_filt
    return Person



def cal_worker(TRIPS, Person):
    trip_rev = TRIPS.copy()
    work_pers = Person.copy()

    """Age Bands."""
    over15 = work_pers.AGE > 14

    """Processing."""
    duration = trip_rev.DURATION > 60 #--------was 60-----------------------------------------------------------------------------------
    DEST_WP = trip_rev.DESTPLACE == 'My workplace'
    Not_PrimSchl = work_pers.STUDYING != 'Primary'

    work_person = trip_rev[['PERSID',"HHID", "DESTPLACE", "DURATION"]].loc[duration & DEST_WP,['PERSID']].drop_duplicates().astype({'PERSID': 'int64'})

    work_person['does_work'] = 1

    work_pers = pd.merge(work_pers, work_person, on='PERSID', how='left')
    work_person_type = work_pers['does_work'] == 1
    not_worker = work_pers.Worker != 1
    blue_col = work_pers.Collar == 'Blue'
    white_col = work_pers.Collar == 'White'
    no_col = work_pers.Collar == 0
    work_pers.loc[work_person_type & over15 & Not_PrimSchl & not_worker,'Worker'] = 1
    # work_pers.loc[work_person_type & over15 & Not_PrimSchl & not_worker & blue_col,'Worker_Blue'] = 1
    # work_pers.loc[work_person_type & over15 & Not_PrimSchl & not_worker & white_col,'Worker_White'] = 1
    # work_pers.loc[work_person_type & over15 & Not_PrimSchl & not_worker & no_col,'Worker_White'] = 1
    work_pers.loc[work_person_type & over15 & Not_PrimSchl & not_worker & blue_col,'Worker_wb'] = 1
    work_pers.loc[work_person_type & over15 & Not_PrimSchl & not_worker & white_col,'Worker_wb'] = 2
    work_pers.loc[work_person_type & over15 & Not_PrimSchl & not_worker & no_col,'Worker_wb'] = 2    
    
    print("Number of Added Workers:{}".format(len(work_pers.loc[work_person_type & over15 & not_worker])))
    print("Number of Added Workers - White:{}".format(len(work_pers.loc[work_person_type & over15 & not_worker & white_col])))
    print("Number of Added Workers - Blue:{}".format(len(work_pers.loc[work_person_type & over15 & not_worker & blue_col])))
    print("Number of Added Workers - None:{}".format(len(work_pers.loc[work_person_type & over15 & not_worker & no_col])))
    work_pers.drop(columns=['does_work'], inplace = True)

    Person = work_pers
    del work_person, trip_rev, over15, blue_col, white_col, no_col, work_pers, work_person_type, not_worker, DEST_WP, duration
    return Person