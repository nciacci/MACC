# -*- coding: utf-8 -*-
"""
Created on Tue Feb 22 14:14:47 2022

@author: jonat
"""

# Plotting
PAGE_WIDTH = 6.99  # in
ROW_HEIGHT = 2.5  # in

# Physical 
year_hours = 8760

# Energy conversions

# from_to
mw_kw = 1000
mmbtu_btu = 1e6
giga = 1e9

# Mass 
lb_kg = 0.4536
kg_tonne = 0.001

# US States
US_STATES = {"Alabama","Alaska","Arizona","Arkansas","California","Colorado","Connecticut","Delaware","District of Columbia","Florida","Georgia","Hawaii","Idaho","Illinois","Indiana","Iowa","Kansas","Kentucky","Louisiana","Maine","Maryland","Massachusetts","Michigan","Minnesota","Mississippi","Missouri","Montana","Nebraska","Nevada","New Hampshire","New Jersey","New Mexico","New York","North Carolina","North Dakota","Ohio","Oklahoma","Oregon","Pennsylvania","Rhode Island","South Carolina","South Dakota","Tennessee","Texas","Utah","Vermont","Virginia","Washington","West Virginia","Wisconsin","Wyoming"}

US_STATE_ABB = {"AL","AK","AZ","AR","CA","CO","CT","DE","DC","FL","GA","HI","ID","IL","IN","IA","KS","KY","LA","ME","MD","MA","MI","MN","MS","MO","MT","NE","NV","NH","NJ","NM","NY","NC","ND","OH","OK","OR","PA","RI","SC","SD","TN","TX","UT","VT","VA","WA","WV","WI","WY"}

US_CONTINENTAL = {"Alabama","Arizona","Arkansas","California","Colorado","Connecticut","Delaware","District of Columbia","Florida","Georgia","Idaho","Illinois","Indiana","Iowa","Kansas","Kentucky","Louisiana","Maine","Maryland","Massachusetts","Michigan","Minnesota","Mississippi","Missouri","Montana","Nebraska","Nevada","New Hampshire","New Jersey","New Mexico","New York","North Carolina","North Dakota","Ohio","Oklahoma","Oregon","Pennsylvania","Rhode Island","South Carolina","South Dakota","Tennessee","Texas","Utah","Vermont","Virginia","Washington","West Virginia","Wisconsin","Wyoming"}

US_CONTINENTAL_ABB = {"AL","AZ","AR","CA","CO","CT","DE","DC","FL","GA","ID","IL","IN","IA","KS","KY","LA","ME","MD","MA","MI","MN","MS","MO","MT","NE","NV","NH","NJ","NM","NY","NC","ND","OH","OK","OR","PA","RI","SC","SD","TN","TX","UT","VT","VA","WA","WV","WI","WY"}

US_STATE_REGION = {
    'New England': ['CT', 'ME', 'MA', 'NH', 'RI', 'VT'],
    'Middle Atlantic': ['NJ', 'NY', 'PA'],
    'East North Central': ['IL', 'IN', 'MI', 'OH', 'WI'],
    'West North Central': ['IA', 'KS', 'MN', 'MO', 'NE', 'ND', 'SD'],
    'South Atlantic': ['DE', 'FL', 'GA', 'MD', 'NC', 'SC', 'VA', 'DC', 'WV'],
    'East South Central': ['AL', 'KY', 'MS', 'TN'],
    'West South Central': ['AR', 'LA', 'OK', 'TX'],
    'Mountain': ['AZ', 'CO', 'ID', 'MT', 'NV', 'NM', 'UT', 'WY'],
    'Pacific': ['AK', 'CA', 'HI', 'OR', 'WA']}



# Filtering constraints
min_cf = 0
max_cf = 1.05 

# Default Fossil fuels
default_fossil = ["Coal", "Gas", "Gas_SC", "Gas_CC", "Oil"]

# Default Replacements
default_replacement = ["Gas", "Wind","Solar"]

# Plotting 

colors = {"Coal"+"\u2192"+"Gas":"#FF6969",
          "Gas_SC"+"\u2192"+"Wind":"#A6D0DD",
          "Gas_CC"+"\u2192"+"Wind":"#A6D0DD",          
          "Gas_SC"+"\u2192"+"Gas":  "#FFD3B0", 
          "Gas_CC"+"\u2192"+"Gas":  "#FFD3B0",
          "Gas"+"\u2192"+"Gas":  "#FFD3B0",           
          "Gas_SC"+"\u2192"+"Solar":"#FFF9DE",
          "Gas_CC"+"\u2192"+"Solar":"#FFF9DE",
          "Gas"+"\u2192"+"Solar":"#FFF9DE",          
          "Oil"+"\u2192"+"Gas":"#98D8AA",
          "Oil"+"\u2192"+"Wind":"#ECC9EE",          
          #
          "Coal"+"\u2192"+"Solar":"#CD9600",
          "Coal"+"\u2192"+"Wind": "#7CAE00",
          "Gas"+"\u2192"+"Wind":"#00A9FF",
          "Oil"+"\u2192"+"Solar":"#800000",
          "National":"#a6a6a6"}

    
state_colors = {
    "AL": "#8F4D56",
    "AK": "#CF71AF",
    "AZ": "#A98175",
    "AR": "#BC8F8F",
    "CA": "#A6D0DD",
    "CO": "#7CAE00",
    "CT": "#CD9600",
    "DE": "#FF6969",
    "FL": "#ECC9EE",
    "GA": "#FFD3B0",
    "HI": "#F7B5D6",
    "ID": "#FFD8B1",
    "IL": "#F08080",
    "IN": "#FF7F50",
    "IA": "#F5DEB3",
    "KS": "#F0E68C",
    "KY": "#90EE90",
    "LA": "#A6A6A6",
    "ME": "#800000",
    "MD": "#FFDAB9",
    "MA": "#FFA07A",
    "MI": "#FFC0CB",
    "MN": "#98D8AA",
    "MS": "#ADD8E6",
    "MO": "#FFF9DE",
    "MT": "#87CEEB",
    "NE": "#FFB6C1",
    "NV": "#FFF8DC",
    "NH": "#DB7093",
    "NJ": "#E6E6FA",
    "NM": "#00A9FF",
    "NY": "#F5F5F5",
    "NC": "#F0FFF0",
    "ND": "#FAFAD2",
    "OH": "#A0522D",
    "OK": "#F5DEB3",
    "OR": "#A9A9A9",
    "PA": "#FFFACD",
    "RI": "#FA8072",
    "SC": "#A6D0DD",
    "SD": "#E9967A",
    "TN": "#FFE4B5",
    "TX": "#D3D3D3",
    "UT": "#FFC8B4",
    "VT": "#B0C4DE",
    "VA": "#87CEFA",
    "WA": "#98FB98",
    "WV": "#BDB76B",
    "WI": "#9370DB",
    "WY": "#E6E6FA"}



# colors = {"Coal_Gas":"#f44336",
#           "Coal_Solar":"#16537e",
#           "Coal_Wind": "#8fce00",
#           "Gas_SC_Gas":  "#f4cccc",
#           "Gas_CC_Gas":  "#ea9999",
#           "Gas_Gas":  "#e06666",
#           "Gas_SC_Solar":"#9fc5e8",
#           "Gas_CC_Solar":"#6fa8dc",
#           "Gas_Solar":"#3d85c6",
#           "Gas_SC_Wind":"#b6d7a8",
#           "Gas_CC_Wind":"#6aa84f",
#           "Gas_Wind":"#274e13",
#           "Oil_Gas":"#990000",
#           "Oil_Wind":"#d9ead3",
#           "Oil_Solar":"#073763",
#          "National":"#a6a6a6"}