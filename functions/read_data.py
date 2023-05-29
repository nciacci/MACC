# -*- coding: utf-8 -*-
"""
Created on Mon Feb  7 22:35:48 2022

@author: jonat
"""
import os 
import pandas as pd
import numpy as np
import constants
import geopandas as gpd
import constants 


def read_data(DIR, fuelName = "22"):
    """
    Parameters
    ----------
    DIR : String
         The location (directory) of the "home" location. Within the folder should
         be data/[file].csv.

    fuelName : String
         The appended name of the file that should be used for fuel price. Name follows data/fuelCost[fuelName].csv

    Returns
    -------
    plant_data : pandas DF
        Data about plant behavior including name, generation, emissions, etc.
    cost_data : pandas DF
        Data about the capital, fuel, and OM costs associated with plants by fuel type.
    cf_data : pandas DF
        Data about capactiy factors for technologies.
    age_data : pandas DF
        Data about the payoff lifetimes (and shutdown lifetimes) of existing plants
    emissions_data : pandas df
        Data about the emissions intesnsity of different fuel/plant types
    pv_cf_data : pandas DF
        Data about the capacity factor of solar pv at set lat/lon points around the US
    wind_cf_data : pandas DF
        Data about the capacity factor of wind at set lat/lon points around the US
    """

    fuelName = str(fuelName)
    
    DATA_DIR = os.path.join(DIR, "data", "processed")
    # Put processing for now until processed 
    DATA_DIR_2 = os.path.join(DIR,"data", "processing","EPA")
    
    plant_data_path            = os.path.join(DATA_DIR, "plant_data.csv")
    pm_plant_path              = os.path.join(DATA_DIR_2, "EPA_PM_EMISSIONS.csv")
    plant_cost_data_path       = os.path.join(DATA_DIR, "plantCost_national_avg"+fuelName+".csv")
    fuel_cost_data_path        = os.path.join(DATA_DIR, "fuelCost"+fuelName+".csv")
    regional_ng_cost_path      = os.path.join(DATA_DIR, "regional_ng_cost_"+fuelName+".csv")
    capacity_factors_data_path = os.path.join(DATA_DIR, "plantCapacityFactor_NREL.csv")
    age_data_path              = os.path.join(DATA_DIR, "plantAge.csv")
    emissions_data_path        = os.path.join(DATA_DIR, "plantEmissions_2023EPA.csv")
    pv_cf_data_path            = os.path.join(DATA_DIR, "pv_open_2020.csv")
    wind_cf_data_path          = os.path.join(DATA_DIR, "Open_Access_Siting_Regime_ATB_Mid_Turbine.csv")

    
    
    plant_data      = pd.read_csv(plant_data_path, header = 1)

    # Add PM data 
    pm_plant_data   = pd.read_csv(pm_plant_path, header = 1) #(lb/MMBtu) 
    pm_plant_data.to_csv(os.path.join(os.getcwd(), "output", "Plant_Processed", "2022_plant_pm.csv"))

    plant_cost_data = pd.read_csv(plant_cost_data_path, index_col = "primary_fuel", comment = "#", header=0)
    fuel_cost_data  = pd.read_csv(fuel_cost_data_path, index_col = "primary_fuel", comment = "#", header=1)
    cf_data         = pd.read_csv(capacity_factors_data_path, header = 1, index_col = "primary_fuel", comment = "#", skip_blank_lines=True)
    age_data        = pd.read_csv(age_data_path, index_col = "primary_fuel", comment = "#", skip_blank_lines=True)
    emissions_data  = pd.read_csv(emissions_data_path, header = 1, index_col = "primary_fuel", comment = "#", skip_blank_lines=True)
    pv_cf_data      = pd.read_csv(pv_cf_data_path, comment = "#", skip_blank_lines=True)
    wind_cf_data    = pd.read_csv(wind_cf_data_path, comment = "#", skip_blank_lines=True)

    # Join cost data together
    cost_data = plant_cost_data.join(fuel_cost_data)
    
#    # Join pm and plant data 

#     plant_data1 = pd.merge(pm_plant_data,plant_data)
#     # Put pm data in last column 
#     num_cols = len(plant_data1.axes[1])
#     pm_col = plant_data1.pop("PM25RT")
#     plant_data1.insert(num_cols-1,"PM25RT",pm_col)
#     plant_data =plant_data1[num_cols + ["PM25RT"]]
    
    

    #

    return plant_data, cost_data, cf_data, age_data, emissions_data, pv_cf_data, wind_cf_data

def clean_plant_data(df, fuel_subset = constants.default_fossil):
    """
    A function that cleans plant data to remove any observations with:

    1) Missing values in any column
    2) Non-positive generation over a year
    3) Non-positive emissions over a year (Unclear how BECCS would be treated here)
    4) Non-positive capacity
    5) Capacity factors less than 0 or greater than 1.05 (allowing some discrepancy and seasonal fluctuations in efficency/capacity)
    

    Args:
        df (pandas df): 
            Dataframe of plant level data with columns name, state, lat, lon, commissioning_year, 
            primary_fuel, capacity, generation, fuel_consumption, and emissions

        fuel_subset (list(str), optional): 
            A list of strings defining which fuels we are interested in replacing. Defaults to constants.default_fossil.

    Returns:
        df:
            A now clean version of the dataframe that was fed in to the function
    """
    
   
    df_full = df.dropna(inplace = False)
    positive_generation = df_full['generation'] > 0 
    positive_consumption = df_full['fuel_consumption'] > 0
    positive_emissions = df_full['emissions'] > 0
    positive_capacity = df_full['capacity'] > 0
    feasible_cf = (df_full['generation']/(df_full['capacity']*constants.mw_kw*constants.year_hours)).between(constants.min_cf, constants.max_cf)
    in_fuel = df_full.primary_fuel.isin(fuel_subset)

    tests_array = np.array([positive_generation, 
                            positive_consumption, 
                            positive_emissions, 
                            positive_capacity, 
                            feasible_cf, 
                            in_fuel])
    
    return df_full[np.all(tests_array, axis = 0)]

def ABT_process(DIR):
    """
    Returns Cost Trend Data for Coal NG Wind and PV Plants from NREL ABT Data 

    
    Args:
        DIR : String
         The location (directory) of the "home" location. Within the folder should
         be data/[file].csv.
        
    
    Returns:
    [natural_gas_cc_trend,natural_gas_cc_ccs_trend,natural_gas_sc_trend,land_wind_trend, pv_trend,coal_trend]
        natural_gas_cc_trend : pandas DF
        Predicted capex,fixed O&M, Variable O&M cost trends for natural gas combined cycle plants 
        O_M_data : pandas DF
        Economic data about O&M cost for wind project with commissioning year of wind plant 
    """
    DATA_DIR              =  os.path.join(DIR, "data", "raw","NREL")
    raw_trend_path        =  os.path.join(DATA_DIR, "ATBe.csv")
    raw_trend_data        =  pd.read_csv(raw_trend_path, header = 1)

    # Seperate NG, Wind, Solar, and Coal Data using Market and Policy Financial Case, and Moderate Scenario 
    natural_gas_cc_trend=  raw_trend_data[(raw_trend_data['technology_alias'] == "Natural Gas")& (raw_trend_data["core_metric_case"]== "Market") & (raw_trend_data["scenario"]== "Moderate")
                                       & (raw_trend_data["display_name"]== "NG F-Frame CC") ]
    
    natural_gas_cc_ccs_trend=  raw_trend_data[(raw_trend_data['technology_alias'] == "Natural Gas")& (raw_trend_data["core_metric_case"]== "Market") & (raw_trend_data["scenario"]== "Moderate")
                                       & (raw_trend_data["display_name"]== "NG combined cycle 95% CCS (F-frame basis -> Transformational Tech)") ]
    
    natural_gas_sc_trend=  raw_trend_data[(raw_trend_data['technology_alias'] == "Natural Gas")& (raw_trend_data["core_metric_case"]== "Market") & (raw_trend_data["scenario"]== "Moderate")
                                       & (raw_trend_data["display_name"]== "NG F-Frame CT") ]
    
   
    # Using average class 4 case 
    land_wind_trend             =  raw_trend_data[(raw_trend_data['technology_alias'] == "Land-Based Wind") & (raw_trend_data["core_metric_case"]== "Market") & (raw_trend_data["scenario"]== "Moderate")
                                     & (raw_trend_data["techdetail"]=="Class4")]
    
    pv_trend                     =  raw_trend_data[(raw_trend_data['technology_alias'] == "Utility PV")& (raw_trend_data["core_metric_case"]== "Market") & (raw_trend_data["scenario"]== "Moderate")
                                      & (raw_trend_data["techdetail"]=="Class4")]
    

    # Choosing CCS 95% Coal-CCS-95% -> 2nd Gen Tech 
    coal_trend                  =  raw_trend_data[(raw_trend_data['technology_alias'] == "Coal")& (raw_trend_data["core_metric_case"]== "Market") & (raw_trend_data["scenario"]== "Moderate")
                                & (raw_trend_data["techdetail"]== "CCS95AvgCF2ndGen")]
    natural_gas_cc_trend        = natural_gas_cc_trend.drop(columns=["Unnamed: 0","atb_year","core_metric_key","core_metric_case","crpyears","technology",
                                                        "technology_alias","techdetail"	,"display_name","default", "scenario"])
    natural_gas_cc_ccs_trend    = natural_gas_cc_ccs_trend.drop(columns=["Unnamed: 0","atb_year","core_metric_key","core_metric_case","crpyears","technology",
                                                        "technology_alias","techdetail"	,"display_name","default", "scenario"])
    natural_gas_sc_trend        = natural_gas_sc_trend.drop(columns=["Unnamed: 0","atb_year","core_metric_key","core_metric_case","crpyears","technology",
                                                        "technology_alias","techdetail"	,"display_name","default", "scenario"])
    
    
    # Drop unnecessary columns 
    land_wind_trend = land_wind_trend.drop(columns=["Unnamed: 0","atb_year","core_metric_key","core_metric_case","crpyears","technology",
                                                        "technology_alias","techdetail"	,"display_name","default", "scenario"])
    
    pv_trend = pv_trend.drop(columns=["Unnamed: 0","atb_year","core_metric_key","core_metric_case","crpyears","technology",
                                                        "technology_alias","techdetail"	,"display_name","default","scenario"])

    coal_trend = coal_trend.drop(columns=["Unnamed: 0","atb_year","core_metric_key","core_metric_case","crpyears","technology",
                                                        "technology_alias","techdetail"	,"display_name","default","scenario"])


    natural_gas_cc_trend       = natural_gas_cc_trend.rename(columns={"":"","core_metric_parameter":"Cost Type","core_metric_variable":"Year","units":"Unit","value":"Cost"})
    natural_gas_cc_ccs_trend   = natural_gas_cc_ccs_trend.rename(columns={"":"","core_metric_parameter":"Cost Type","core_metric_variable":"Year","units":"Unit","value":"Cost"})
    natural_gas_sc_trend       = natural_gas_sc_trend.rename(columns={"":"","core_metric_parameter":"Cost Type","core_metric_variable":"Year","units":"Unit","value":"Cost"})
    land_wind_trend            = land_wind_trend.rename(columns={"":"","core_metric_parameter":"Cost Type","core_metric_variable":"Year","units":"Unit","value":"Cost"})
    pv_trend                   = pv_trend.rename(columns={"":"","core_metric_parameter":"Cost Type","core_metric_variable":"Year","units":"Unit","value":"Cost"})
    coal_trend                 = coal_trend.rename(columns={"":"","core_metric_parameter":"Cost Type","core_metric_variable":"Year","units":"Unit","value":"Cost"})


    return [natural_gas_cc_trend,natural_gas_cc_ccs_trend,natural_gas_sc_trend,land_wind_trend, pv_trend,coal_trend]
    

def process_regional_fuel_price(DIR): 

    DATA_DIR                  =  os.path.join(DIR, "data", "processing","EIA")
    processing_ng_path        =  os.path.join(DATA_DIR,"2022", "NG_Regional_Prices.csv")
    processing_coal_path      =  os.path.join(DATA_DIR, "2021", "Coal_Price_Region_21.csv")
    processing_ng_data        =  pd.read_csv(processing_ng_path, header = 0)
    processing_coal_data      =  pd.read_csv(processing_coal_path, header = 1,comment= "#")

    # Need to get rid of and just make original file 
    DATA_DIR_2                      = os.path.join(DIR, "data", "processed")


    # Get oringial fuel cost data not based on region for 2022 
    fuel_cost_data_path             = os.path.join(DATA_DIR_2, "fuelCost22.csv")
    fuel_cost_data                  = pd.read_csv(fuel_cost_data_path, index_col = "primary_fuel", comment = "#", header=1)

    # Make empty dataframe 
    regional_fuel_price = pd.DataFrame() 
    regional_fuel_price["state"] = list(constants.US_STATE_ABB) 


    ## EIA 2022 NG Price Processing 

    # Find missing prices 
    missing_prices      = processing_ng_data.loc[processing_ng_data['fuel_price_per_mmbtu'] <= 0]
    # Find National Average 
    national_average    = float(processing_ng_data.loc[processing_ng_data['state'] == "avg", 'fuel_price_per_mmbtu'])
    # Get list of states 
    states = pd.DataFrame(processing_ng_data['state'])

    # Load the US states dataset
    zipfile             = "zip://"+os.path.join(os.getcwd(), "data", "raw", "mapping", "cb_2018_us_state_20m.zip")
    usa                 = gpd.read_file(zipfile)

    for state in missing_prices["state"]:
        state1              = usa[usa['STUSPS'] == state]
        # Find bordering states 
        bordering_state     = usa[usa.intersects(state1.unary_union)]
        bordering_state     = bordering_state['STUSPS'].tolist()
        price               = 0 
        counter             = 0 
        # Calculate average price based on bordering states 
        for border_state in bordering_state: 
            if processing_ng_data.set_index('state').loc[border_state, 'fuel_price_per_mmbtu'] > 0: 
                price       = price + processing_ng_data.set_index('state').loc[border_state, 'fuel_price_per_mmbtu'] 
                counter    += 1 
            if counter > 0: 
                avg_price  = price/counter 
                processing_ng_data.loc[processing_ng_data['state'] == state , 'fuel_price_per_mmbtu'] = avg_price   
            # If there is no data on bordering states then sit price to national average 
            else:
                processing_ng_data.loc[processing_ng_data['state'] == state , 'fuel_price_per_mmbtu'] = national_average
    # Add to dataframe 
    regional_fuel_price["Gas"]    = processing_ng_data["fuel_price_per_mmbtu"]
    regional_fuel_price["Gas_SC"] = processing_ng_data["fuel_price_per_mmbtu"]
    regional_fuel_price["Gas_CC"] = processing_ng_data["fuel_price_per_mmbtu"] 


    # EIA 2021 Coal Data Processing 

    # Add empty coal column
    regional_fuel_price["Coal"] = 0
    # Find states in region and assign their price to the regional value 
    for region in constants.US_STATE_REGION.keys(): 
        region_price = processing_coal_data.loc[processing_coal_data["Region"]==region,"fuel_price_per_mmbtu"].iloc[0]
        states_in_region = constants.US_STATE_REGION[region]
        for state in states_in_region: 
            regional_fuel_price.loc[regional_fuel_price["state"]==state, "Coal"] = region_price
    

    # Add Oil
    regional_fuel_price["Oil"] = np.repeat(fuel_cost_data["fuel_price_per_mmbtu"]["Oil"],len(regional_fuel_price["Gas"]))
    # Add Wind 
    regional_fuel_price["Wind"] = np.repeat(fuel_cost_data["fuel_price_per_mmbtu"]["Wind"],len(regional_fuel_price["Gas"]))
    # Add Solar 
    regional_fuel_price["Solar"] = np.repeat(fuel_cost_data["fuel_price_per_mmbtu"]["Solar"],len(regional_fuel_price["Gas"]))
    # Add Hydro
    regional_fuel_price["Hydro"] = np.repeat(fuel_cost_data["fuel_price_per_mmbtu"]["Hydro"],len(regional_fuel_price["Gas"]))
    # Add Geothermal
    regional_fuel_price["Geothermal"] = np.repeat(fuel_cost_data["fuel_price_per_mmbtu"]["Geothermal"],len(regional_fuel_price["Gas"]))
    # Add CSP
    regional_fuel_price["CSP"] = np.repeat(fuel_cost_data["fuel_price_per_mmbtu"]["CSP"],len(regional_fuel_price["Gas"]))
    # Add Nuclear
    regional_fuel_price["Nuclear"] = np.repeat(fuel_cost_data["fuel_price_per_mmbtu"]["Nuclear"],len(regional_fuel_price["Gas"]))
    # Add Biomass
    regional_fuel_price["Biomass"] = np.repeat(fuel_cost_data["fuel_price_per_mmbtu"]["Biomass"],len(regional_fuel_price["Gas"]))

    # Save output 
    regional_fuel_price.to_csv(os.path.join(os.getcwd(),"data", "processed","regional_fuel_cost_22.csv"))

    return regional_fuel_price

def process_regional_plant_cost(DIR,mult_fact,tax = 0): 

    
    """ Multiplication factor is used for sensitivity analysis
    tax: 
    if tax = 1, then tax incentive is included in the cost else it is not included 

    """
    

    DATA_DIR                     =  os.path.join(DIR, "data", "processing","EPA")
    DATA_DIR_2                   =  os.path.join(DIR, "data", "processed")
    avg_cost_data_path           =  os.path.join(DATA_DIR_2, "plantCost_national_avg22.csv")
    tax_credit_path              =  os.path.join(DATA_DIR_2, "tax_credits.csv")
    process_EPA_cost_path        =  os.path.join(DATA_DIR, "NERC_state_cost_factors.csv")
    process_EPA_cost_data        =  pd.read_csv(process_EPA_cost_path, header = 0)
    avg_cost_data                =  pd.read_csv(avg_cost_data_path, header = 0, comment= "#")
    tax_credit_data              =  pd.read_csv(tax_credit_path, header = 0, comment= "#")
    df = pd.DataFrame(columns = ["state","Coal_variable_om_per_mwh","Coal_fixed_om_per_kw_year","Coal_capital_cost_per_kw","Gas_variable_om_per_mwh","Gas_fixed_om_per_kw_year","Gas_capital_cost_per_kw","Gas_CC_variable_om_per_mwh","Gas_CC_fixed_om_per_kw_year","Gas_CC_capital_cost_per_kw",
                                 "Gas_SC_variable_om_per_mwh","Gas_SC_fixed_om_per_kw_year","Gas_SC_capital_cost_per_kw","Wind_variable_om_per_mwh","Wind_fixed_om_per_kw_year","Wind_capital_cost_per_kw","Solar_variable_om_per_mwh","Solar_fixed_om_per_kw_year","Solar_capital_cost_per_kw",
                                "Wind_storage_om_per_kw_year","Wind_storage_cap_per_kw","Solar_storage_om_per_kw_year","Solar_storage_cap_per_kw","Gas_storage_om_per_kw_year","Gas_storage_cap_per_kw",
                                "Gas_CC_storage_om_per_kw_year","Gas_CC_storage_cap_per_kw","Gas_SC_storage_om_per_kw_year","Gas_SC_storage_cap_per_kw"])

    df["state"] = list(constants.US_STATE_ABB)

    if tax ==0: 
        tax_credit = 0 
        grant = 0
    for plant_type in list(avg_cost_data["primary_fuel"]): 
        reg_capital_cost = avg_cost_data.loc[avg_cost_data["primary_fuel"]==plant_type,"capital_cost_per_kw"].iloc[0]
        reg_fixed_o_m = avg_cost_data.loc[avg_cost_data["primary_fuel"]==plant_type,"fixed_om_per_kw_year"].iloc[0]
        reg_var_o_m = avg_cost_data.loc[avg_cost_data["primary_fuel"]==plant_type,"variable_om_per_mwh"].iloc[0]
        reg_stor_cap = avg_cost_data.loc[avg_cost_data["primary_fuel"]==plant_type,"storage_cap_per_kw"].iloc[0]
        reg_stor_om = avg_cost_data.loc[avg_cost_data["primary_fuel"]==plant_type,"storage_om_per_kw_year"].iloc[0]
        for state in list(df["state"]): 
            if tax == 1: 
                if plant_type == "Wind" or plant_type == "Solar":
                    tax_credit = tax_credit_data.loc[tax_credit_data["state"]=="national","Amount"].iloc[0]
                    grant = 0 
                if state in list(tax_credit_data["state"]): 
                    if  plant_type == "Wind": 
                        if tax_credit_data.loc[tax_credit_data["state"]==state,"w_flag"].iloc[0] == 1 and tax_credit_data.loc[tax_credit_data["state"]==state,"grant"].iloc[0] == 0:
                            tax_credit = tax_credit_data.loc[tax_credit_data["state"]==state,"Amount"].iloc[0] + tax_credit
                        if tax_credit_data.loc[tax_credit_data["state"]==state,"w_flag"].iloc[0] == 1 and tax_credit_data.loc[tax_credit_data["state"]==state,"grant"].iloc[0] == 1:
                            grant = tax_credit_data.loc[tax_credit_data["state"]==state,"Amount"].iloc[0]
                    if plant_type == "Solar": 
                        if tax_credit_data.loc[tax_credit_data["state"]==state,"s_flag"].iloc[0] == 1 and tax_credit_data.loc[tax_credit_data["state"]==state,"grant"].iloc[0] == 0:
                            tax_credit = tax_credit_data.loc[tax_credit_data["state"]==state,"Amount"].iloc[0] + tax_credit
                        if tax_credit_data.loc[tax_credit_data["state"]==state,"s_flag"].iloc[0] == 1 and tax_credit_data.loc[tax_credit_data["state"]==state,"grant"].iloc[0] == 1:
                            grant = tax_credit_data.loc[tax_credit_data["state"]==state,"Amount"].iloc[0]
                    if plant_type == "Gas" or plant_type == "Gas_CC" or plant_type == "Gas_SC" or plant_type == "Coal":  
                        tax_credit = 0 
                        grant = 0
                if plant_type == "Coal" or plant_type == "Gas" or plant_type == "Gas_CC" or plant_type == "Gas_SC":
                    tax_credit = 0 
                    grant = 0
            factor = process_EPA_cost_data.loc[process_EPA_cost_data["state"]==state,plant_type].iloc[0]
            df.loc[df["state"]==state, plant_type +"_variable_om_per_mwh"] = factor*reg_var_o_m
            df.loc[df["state"]==state, plant_type +"_fixed_om_per_kw_year"] = factor*reg_fixed_o_m
            df.loc[df["state"]==state, plant_type +"_capital_cost_per_kw"] = (factor*reg_capital_cost) + (factor*reg_capital_cost*tax_credit) + grant 
            df.loc[df["state"]==state, plant_type +"_storage_cap_per_kw"] = ((factor*reg_stor_cap) + (factor*reg_stor_cap*tax_credit))*mult_fact
            df.loc[df["state"]==state, plant_type +"_storage_om_per_kw_year"] = factor*reg_stor_om*mult_fact
    if tax ==0: 
        df.to_csv(os.path.join(os.getcwd(),"data", "processed","state_plant_cost_22.csv"))
    if tax == 1: 
        df.to_csv(os.path.join(os.getcwd(),"data", "processed","state_plant_cost_22_ITC.csv"))
    return df 
    


    
