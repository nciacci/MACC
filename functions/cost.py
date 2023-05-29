
import numpy
import pandas
import constants
from scipy import stats
from statsmodels.tsa.stattools import adfuller 
from statsmodels.tsa.arima.model import ARIMA
import matplotlib.pyplot as plt

def fuel_demand(heat_rate, gen):
    """
    Calculating the fuel demand for a plant with heat rate heat_rate to generate
    gen amounts of energy. 

    Parameters
    ----------
    heat_rate : float
        The efficiency in btu fuel in/kwh electricity out.
    gen : float
        Total generation to produce in kwh.
        
    Returns
    -------
    float
        Total fuel to generate gen energy with efficiency heat rate.

    """
    return gen*heat_rate

# =============================================================================
# # annualize_cost function to return the annualized cost of a lump sum payment with discount rate discount_rate. 
# # cost: float representing lump sum cost to pay off
# # discount_rate: float representing the discount rate of future costs
# # lifetime: float representing the length of payoff lifetime 
# def annualize_cost(cost, discount_rate, lifetime):
#     annuity_factor = (1-(1/((1+discount_rate)**lifetime)))/discount_rate
#     return cost/annuity_factor
# =============================================================================

def interval_payment(principle, rate, lifetime, payments_per_year=1):
    """
    Parameters
    ----------
    principle : float
        The initial principle to payoff
    rate : float
        A value (usually ~5% or 0.05) that represents the interest rate charged to the principle annually
    lifetime : float
        The lifetime to payoff the principle (in years)
    payments_per_year : float, optional
        The number of sub payments each year. We assume an annual payment, so the default is 1.

    Returns
    -------
    float
        The regular installment payment. This payment will be paid lifetime*payments_per_year times to be paid off

    """
    numerator = numpy.multiply(rate,principle)
    denominator = payments_per_year*(1-(1+rate/payments_per_year)**(-payments_per_year*lifetime))
    return numpy.divide(numerator,denominator)

max_vec = numpy.vectorize(max)

def remaining_capital(principle, age, rate, lifetime, payments_per_year=1):
    """
    Calculates the remaining capital on an initial investment of cost "principle"
    after "age" years. 

    Parameters
    ----------
    principle : float
        The initial capital to payoff
    age : float
        Current age of the plant (in years).
    rate : float
        A value (usually ~5% or 0.05) that represents the interest rate charged to the principle annually
    lifetime : float
        The lifetime to payoff the principle (in years)
    payments_per_year : float, optional
        The number of sub payments each year. We assume an annual payment, so the default is 1.

    Returns
    -------
    remaining_val : float
        value of the original capital that is remaining.

    """
    
    payment = interval_payment(principle, rate, lifetime, payments_per_year)
    num_payments = age*payments_per_year
    equivalent_rate = rate/payments_per_year
    
    
    lifetime_cost = principle*(1+equivalent_rate)**(num_payments)
    amount_paid = payment*((1+equivalent_rate)**(num_payments)-1)/(equivalent_rate)
    remaining_val = max_vec(lifetime_cost - amount_paid, 0.0)
    return remaining_val


def total_cost(var_om, fix_om, fuel_price, principle_cost, stor_cost_cap, stor_cost_om, discount_rate, lifetime, gen, cap, fuel_dem):
    """
    Calculate the total cost of building a new plant annualized to annual payments

    Args:
        var_om ([float])         : Variable cost of operations and maintanace $/Mwh
        fix_om ([float])         : Fixed cost of operations and maintanance $/kw
        fuel_price ([float])     : Cost of fuel input $/mmbtu of fuel
        principle_cost ([float]) : Initial capital cost to build plant $/kw
        stor_cost_cap ([float])  : Initial capital cost to build storage $/kw_generation
        stor_cost_om ([float])   : Fixed cost of operations and maintanance of storage $/kw_generation
        discount_rate ([float])  : Rate of discount for future income/costs (typically between 5% and 20%)
        lifetime ([float])       : Lifetime for the pay off of capital
        gen ([float])            : annual generation of electricity (kwh)
        cap ([float])            : Capacity of plant (mw)
        fuel_dem ([float])       : Demand of fuel (mmbtu)

    Returns:
        [float]: annualized total cost of generation, gen, capacity, cap, fuel demand, fuel_dem, discount rate, and lifetime. 
    """
    
    # Function inputs expect different units than what was input here.
    # update them with new units
    
    var_om_kwh        = numpy.divide(var_om,constants.mw_kw)
    fix_om_mw         = numpy.multiply(numpy.add(stor_cost_om,fix_om),constants.mw_kw)
    principle_cost_mw = numpy.multiply(numpy.add(principle_cost,stor_cost_cap),constants.mw_kw)
    
 
    cost_var_om = numpy.multiply(var_om_kwh,gen)
    cost_fix_om = numpy.multiply(fix_om_mw,cap)
    cost_fuel   = numpy.multiply(fuel_price,fuel_dem)
    cost_cap    = numpy.multiply(principle_cost_mw,cap)
        
    cost_annual_cap = interval_payment(cost_cap, discount_rate, lifetime)
    a = numpy.add(cost_var_om,cost_fix_om)
    b = numpy.add(cost_fuel,cost_annual_cap)
    return numpy.add(a,b) 
total_cost_vec = numpy.vectorize(total_cost)
