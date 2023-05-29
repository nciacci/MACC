# Functions to calculate amortized capital and remaining capital
# Created on 22/01/24 by Jonathan Huster

# https://www.educba.com/amortization-formula/

# P: Principle. The initial value to ammortize
# r: annual interest rate
# y: years to complete the loan
# n: number of payments per year (default 1)
# Output: annual cost to pay off P Principle in y years at r interest rate
def annual_cost(P, r, y, n = 1): 
    pay_rate = r/n # Number of payments per annual interest rate
    return P*(pay_rate/(1-(1+pay_rate)**-(y*n)))
    

# P: Principle amount owed initially
# mp: Monthly payment paid
# r: annual interest rate
# y: number of years paid
# n: number of payments per year
def remaining_capital(P, mp, r, y, n=1):
    remaining_balance = P*(1+r/n)**(y*n)
    remaining_balance_annuity = mp*((1+r/n)**(y*n)-1)/(r/n)
    return remaining_balance - remaining_balance_annuity



