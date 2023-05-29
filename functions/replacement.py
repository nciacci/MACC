# -*- coding: utf-8 -*-
"""
Created on Thu Feb 17 14:05:32 2022

@author: jhuster
"""
import os
import cost
import pandas as pd 
import constants
import numpy
from scipy.spatial import distance
import cvxpy as cp 

def size_capacity(gen, cf):
    """
    Parameters
    ----------
    gen : float
        the original generation we are trying to reach
    cf : float between 0 and 1
        A representative capacity factor for the technology

    Returns 
    -------
    capacity of plant with capacity factor cf to reach generation gen.

    """
    
    hours_per_year = 8760
    return numpy.divide(gen,numpy.multiply(cf,hours_per_year))

def estimate_emissions(generation, heatrate, carbon_content):
    """
    Parameters
    ----------
    generation : float
        the amount of electricity generated (kwh)
    heatrate : float
        the efficiency of the power plant (btu/kwh)
    carbon_content : float
        The carbon emissions of the fuel when burned (tonne CO2/btu fuel)

    Returns
    -------
    float
        tonne emitted from burning of the fuel

    """
    return generation*heatrate*carbon_content

def direct_replacement_cost(gen, cf, heatrate, var_om, fix_om, fuel_price, principle_cost, stor_cost_cap, stor_cost_om, discount_rate, lifetime):
    """
    Estimates the direct cost of replacing "gen" generation with a new power plant. 
    Capacity factors, costs, and lifetimes must be parameter inputs. 

    Args:
        gen ([float])           : annual generation of electricity (kwh)
        cf  ([float])           : Capacity factor of replacement plant (NA)
        heatrate([float])       : Heatrate of the replacement (btu/kwh)
        var_om ([float])        : Variable cost of operations and maintanace ($/Mwh)
        fix_om ([float])        : Fixed cost of operations and maintanance ($/kw)
        fuel_price ([float])    : Cost of fuel input ($/mmbtu) of fuel
        principle_cost ([float]): Initial capital cost to build plant ($/kw)
        stor_cost_cap ([float])     : Initial capital cost to build storage ($/kw_generation)
        stor_cost_om ([float])     : Fixed cost of operations and maintanance for storage ($/kw_generation)
        discount_rate ([float]) : Rate of discount for future income/costs (typically between 5% and 20%)
        lifetime ([float])      : Lifetime for the pay off of capital
        
    Returns:
        [float]: annualized total cost of generating, gen, with parameters provided
    """
    cap = size_capacity(gen, cf)/constants.mw_kw
    fuel = numpy.multiply(heatrate,gen)/constants.mmbtu_btu
        
    return cost.total_cost(var_om, fix_om, fuel_price, principle_cost, stor_cost_cap, stor_cost_om, discount_rate, lifetime, gen, cap, fuel)
                
def total_replacement_cost(gen, cf, heatrate, var_om, fix_om, fuel_price, principle_cost, stor_cost_cap, stor_cost_om,discount_rate, lifetime,
                           o_principle, age, o_rate, o_lifeimte, o_ppy=1):
    
 
    """
    Calculate the total cost of replacing an existing powerplant with a new plant
    considering both new capital and remaining historical capital.

    Parameters
    ----------
    gen : float
        the amount of electricity generated (kwh).
    cf : float
        Capacity factor of replacement plant (NA).
    heatrate : float
        Heatrate of the replacement (btu/kwh).
    var_om : float
        Variable cost of operations and maintanace ($/Mwh).
    fix_om : float
        Fixed cost of operations and maintanance ($/kw).
    fuel_price : float
        Cost of fuel input ($/mmbtu) of fuel.
    principle_cost : float
        Initial capital cost to build plant ($/kw).
    stor_cost : float
        Initial capital cost to build storage for plant ($/kw_generation).
    discount_rate : float
        Rate of discount for future income/costs (typically between 5% and 20%).
    lifetime : float
        Lifetime for the pay off of capital.
    o_principle : float
        Original principle to pay off ($).
    age : float
        Current age of the plant (years).
    state: float 
        State that plant is loacted in. 
    o_rate : float
        Original discount/interest rate for the initial principle (%).
    o_lifeimte : float
        Original payoff lifetime for the initial principle (years).
    o_ppy : float, optional
        Original payments per year. The default is 1.

    Returns
    -------
    float
        Total annualized cost of replacing initial plant with an updated plant ($/year).

    """
    
    
    
    
    direct_cost = direct_replacement_cost(gen, cf, heatrate, var_om, fix_om, fuel_price, principle_cost, stor_cost_cap, stor_cost_om, discount_rate, lifetime)
    
    leftover = cost.remaining_capital(o_principle, age, o_rate, o_lifeimte, o_ppy)
    payoff_cost = cost.interval_payment(leftover, discount_rate, lifetime)
    return direct_cost + payoff_cost

def replacement_iteration(principle_cost,discount_rate, lifetime, gen, cap, fuel_dem, states, age,emissions,
                          cf_dict, cost_dict,regional_fuel_price_data,state_plant_cost_data,emissions_dict, metric=0, subset = ["Gas", "Solar", "Wind"]): #var_om, fix_om, 
    """
    

    Parameters
    ----------
    var_om : float
        Variable cost of operations and maintanace ($/Mwh).
    fix_om : float
        Fixed cost of operations and maintanance ($/kw).
    fuel_price : float
        Cost of fuel input ($/mmbtu) of fuel.
    principle_cost : float
        Initial capital cost to build plant ($/kw).
    stor_cost_cap : float
        Initial capital cost to build storage ($/kw_generation).
    discount_rate : float
        Rate of discount for future income/costs (typically between 5% and 20%).
    lifetime : float
        Lifetime for the pay off of capital.
    gen : float
        the amount of electricity generated (kwh).
    cap : float
        Capacity of the original plant (mw).
    fuel_dem : float
        Demand for fuel (mmbtu).
    state: float 
        Staet that the plant is in. 
    age : float
        Age of current plant (years).
    emissions : float
        Total CO2e emissions (metric tonnes).
    cf_dict : dictionary
        Dictionary of capacity factors of replacement plants (NA).
    cost_dict : dictionary
        Dictionary of costs of replacement plants ($/kw, $/MWh).
    regional_fuel_price_data: df
        Pandas dataframe with price for each fuel type in each state. 
    state_plant_cost_data: df 
        Pandas dataframe with capital and O&M cost for each fuel type for each state. 
    emissions_dict : dictionary
        Dictionary of emissions rates by fuel (tonnes/MWh).
    metric : int, optional
        Which metric to judge by 0: cost, 1: Cost/emissions, 2: emissions, 3: Fuel and OM costs, 4: new costs. The default is 0.
    subset : list(str), optional
        The subset of options that can replace your plant. The default is ["Gas", "Solar", "Wind"].
        
    Returns
    -------
    fuels : str
        The fuel that should be used to replace.
    costs : float
        The optimal metric cost. 
    em_red : float
        Emissions avoided from the choice of fuels at score costs.

    """
  
    metrics = {0:dict(zip(subset, [None]*len(subset))), # Cost
               1:dict(zip(subset, [None]*len(subset))), # Ratio cost to emissions
               2:dict(zip(subset, [None]*len(subset))), # Emisisons
               3:dict(zip(subset, [None]*len(subset))), # FOM costs
               4:dict(zip(subset, [None]*len(subset)))} # New Costs
    # For each potential fuel replacement calculate the remaining cost, total new cost, and new emissions, 
    # Then make a decision based on the specified metric
    for fuel in subset:
        fuel_price = [] 
        var_om = []
        fix_om = [] 
        capital = [] 
        storage_cap = []
        storage_om = [] 
        # Create array of state level fuel price, O&M and capital costs 
        for state in states: 
            fuel_price.append(regional_fuel_price_data.loc[regional_fuel_price_data["state"]== state, fuel].iloc[0])
            var_om.append(state_plant_cost_data.loc[state_plant_cost_data["state"]==state,fuel+"_variable_om_per_mwh"].iloc[0])
            fix_om.append(state_plant_cost_data.loc[state_plant_cost_data["state"]==state,fuel+"_fixed_om_per_kw_year"].iloc[0])
            capital.append(state_plant_cost_data.loc[state_plant_cost_data["state"]==state,fuel+"_capital_cost_per_kw"].iloc[0])
            storage_cap.append(state_plant_cost_data.loc[state_plant_cost_data["state"]==state,fuel+"_storage_cap_per_kw"].iloc[0])
            storage_om.append(state_plant_cost_data.loc[state_plant_cost_data["state"]==state,fuel+"_storage_om_per_kw_year"].iloc[0])
        existing_cost = cost.total_cost(var_om, fix_om, fuel_price, principle_cost, storage_cap,storage_om, discount_rate, lifetime, gen, cap, fuel_dem) # we can put cap in if we want to annualize the remaining capital over a new lifetime, but we'll put 0 here. 
        replacement_cost = total_replacement_cost(gen,
                               cf_dict[fuel],
                               cost_dict["heat_rate_btu_per_kwh"][fuel],
                               var_om,                  
                               fix_om,                  
                               fuel_price,             
                               capital,                
                               storage_cap,
                               storage_om,                                                  
                               discount_rate,
                               lifetime,
                               numpy.multiply(capital,constants.mw_kw*cap),
                               age,
                               discount_rate, 
                               lifetime)
        new_emissions = estimate_emissions(gen, 
                                           cost_dict["heat_rate_btu_per_kwh"][fuel], 
                                           emissions_dict[fuel])
        
        metrics[0][fuel] = replacement_cost-existing_cost
        metrics[1][fuel] = cost_per_emissions_abated(existing_cost, replacement_cost, emissions, new_emissions)
        metrics[2][fuel] = emissions-new_emissions
        metrics[3][fuel] = existing_cost/gen
        metrics[4][fuel] = replacement_cost/gen
    emissions_red = numpy.array(list(metrics[2].values()))

    # Pull the array of choices, depending on which evaluation metric is chosen, then 
    # select the replacement choice for each plant that minimizes the metric. 
    # return the fuel choices, the costs, and emissions reductions associated with those choices. 

    options = numpy.array(list(metrics[metric].values()))
    choices = numpy.argmin(options, axis = 0)
    costs = options[choices, numpy.arange(options.shape[1])]      # numpy.amin(options, axis = 0)
    em_red = emissions_red[choices, numpy.arange(options.shape[1])]
    fuels = numpy.array(subset)[choices]
        
    
    return fuels, costs, em_red

def replacement_df(df,cost_dict,regional_fuel_price_data, state_plant_cost_data,cf_dict, emissions_dict, principle_cost, discount_rate, lifetime, measure_year = 2021, metric=0, subset = ["Gas", "Solar", "Wind"]):
    """
    A wrapper function that allows us to feed in only a dataframe, key dictionaries, and key parameters rather
    than individual costs and parameters when calculating the cost of replacement. 

    Args:
        df (pandas df): 
            Plant level data on generation, emissions, and fuel usage
        cost_dict (dict): 
            A dictionary of costs by fuel and source (eg fuel, OM, capital, etc). prices in $/kw, $/kwh, and $/mmbtu
        regional_fuel_price_data: pandas df
            Pandas dataframe with price for each fuel type in each state. 
        state_plant_cost_data: pandas df
            Pandas dataframe with capital and O&M cost for each fuel type for each state. 
        cf_dict (dict): 
            A dictionary of capacity factors by fuel. For wind and solar, cfs may be a list 
            sorted to match the order of plants in df
        emissions_dict (dict): 
            A dictionary of emissions by fuel in tonneCO2/mmbtu fuel
        principle_cost (float): 
            Amount of principle that existing plants need to pay to originally construct. By default, 0.
        discount_rate (float): 
            A percent discount rate for actors making this switch
        lifetime (float): 
            A payoff lifetime of plants both existing and newly constructed (years)
        measure_year (int, optional): 
            The year these decisions will be made in. Defaults to 2021.
        metric (int, optional): 
            Which decision metric to base our decions off of. Defaults to 0.
        subset (list, optional): 
            Which subset of fuel replacements we consider to be possible. Defaults to ["Gas", "Solar", "Wind"].

    Returns:
        fuels : 
            A list of selected fuels, ordered to match the order of plants in df
        costs : 
            A list of the costs associated with the fuel selection, ordered to match the order of plants in df
        em_red : 
            A list of emissions reductions, ordered to match the order of plants in df
        
    """
    fuels, costs, em_red = replacement_iteration(#df["primary_fuel"].map(cost_dict["variable_om_per_mwh"]),
                                                 #df["primary_fuel"].map(cost_dict["fixed_om_per_kw_year"]),
                                                 #df["primary_fuel"].map(cost_dict["fuel_price_per_mmbtu"]),                           
                                                 principle_cost, # plant_data["primary_fuel"].map(cost_dict["capital_cost_per_kw"]),
                                                 discount_rate,
                                                 lifetime,
                                                 df["generation"],
                                                 df["capacity"],
                                                 df["fuel_consumption"],
                                                 df["state"],
                                                 measure_year-df["commissioning_year"],
                                                 df["emissions"],
                                                 cf_dict,
                                                 cost_dict,
                                                 regional_fuel_price_data,
                                                 state_plant_cost_data,
                                                 emissions_dict,
                                                 metric,
                                                 subset)
    return fuels, costs, em_red

def set_macc(df, neg_cap = -200, cap = 200):
    """
    This function orders a df of replacement decisions by the cost effectiveness of each decision. 
    Then calcualtes the cumulative impacts of these ordered decisions

    Args:
        df (pandas df): 
            A dataframe of plant operations and replacements with associated costs and emissions reductions
        neg_cap (int, optional): 
            How low should the metric be considered to. Defaults to -200.
        cap (int, optional): 
            How high should the metric be considered to. Defaults to 200.

    Returns:
        pandas df : 
            An ordered and filtered version of the df that was fed in, but with additional columns 
            with cumulative impacts
    """
    holder = df.loc[df.metric.between(neg_cap, cap) & (df["em_red"] > 1)].copy()
    holder.sort_values("metric", inplace=True)
    holder["cum_red"] = numpy.cumsum(holder["em_red"])/constants.giga
    holder["cum_red_prev"] = (numpy.cumsum(holder["em_red"])-holder["em_red"])/constants.giga
    holder["ori_rep"] = holder["primary_fuel"] + "\u2192" + holder["rep_fuel"]
    # Added cumulative current emissions 
    holder["cum_emission"] = numpy.cumsum(holder["emissions"])

    return holder
    

def cost_per_emissions_abated(cost_orig, cost_new, emissions_orig, emissions_new):
    """
    Calculate the unit cost per unit emissions abated for a decision

    Args:
        cost_orig (float): 
            The cost of maintaining the original plant $
        cost_new (float): 
            The cost of building and maintaining a new plant $
        emissions_orig (float): 
            The emissions from the original plant given historical operation
        emissions_new (float): 
            Estimated emissions from a replacement plant given a replacement plan

    Returns:
        float: unit cost per unit emissions abated.
    """
    return (cost_new-cost_orig)/(emissions_orig-emissions_new)

def select_cf(loc, data_loc, cf):
    """
    Choosing the closest point from a set of sampled points to find the closest sampled capacity factor for wind and solar

    Args:
        loc (2-d numpy array): 
            A 2-d array of lat/lon pairs of points that we want to find the CFs for 
        data_loc (2-d numpy array): 
            A 2-d array of lat/lon pairs of sampled locations that we can pick from 
        cf (1-d numpy array): 
            An array of capacity factors associated with the data_locs

    Returns:
        numpy 1-d array : The capacity factors of the points closest to loc locations given a set of data data_loc 
    """

    dist_array = distance.cdist(loc, data_loc)
    best_locs = numpy.argmin(dist_array, axis = 1) # the algorithm for best loc could be expanded to include other parameters as well. 
    cf_vals = cf[best_locs]
    
    return cf_vals

    