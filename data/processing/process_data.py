# -*- coding: utf-8 -*-
"""
Created on Thu Mar 31 12:15:26 2022

@author: jonat
"""
import os
import sys

sys.path.insert(0, './EIA/')
sys.path.insert(0, './EIA_CEMS/')

import process_eia_data
import join_CEMS_EIA


def create_path(path):
    '''Helper function to create directories if needed.'''
    if not os.path.exists(path):
        os.makedirs(path)
    return path

if __name__ == '__main__': 
    DIR = create_path('C:\\Users\\jonat\\OneDrive\\Desktop\\General\\School\\Stanford\\Research\\MACC\\MACCpy\\data\\processing')
    EIA_DIR = create_path(os.path.join(DIR,"EIA"))
    CEMS_DIR = create_path(os.path.join(DIR,"CEMS"))
    
    OUT_FILE = os.path.join(DIR,"..", "processed", "plant_data.csv")
    
    
    start_year = 2020
    end_year = 2020
    
    for year in range(start_year, end_year+1):
        # Process EIA
        EIA_RAW_FILE = os.path.join(EIA_DIR, "..", "..", "raw", "EIA", str(year), "3_1_Generator_Y2017.xlsx" )
        EIA_LOC_FILE = os.path.join(EIA_DIR, "..", "..", "raw", "EIA", str(year), "2___Plant_Y2017.xlsx" )
        EIA_FUEL_FILE = os.path.join(EIA_DIR, "eia_tech_mapping.csv" )
        EIA_CLEAN_FILE = os.path.join(EIA_DIR, str(year), "EIA_mapping.csv")
        
        process_eia_data.merge_EIA(EIA_RAW_FILE, EIA_LOC_FILE, EIA_FUEL_FILE, EIA_CLEAN_FILE)    
        
        # Process CEMS
        
        # Join EIA and CEMS
        CEMS_FILE = os.path.join(DIR, "CEMS", str(year), "aggregated_cems.csv")
        join_CEMS_EIA.join_CEMS_EIA(CEMS_FILE, EIA_CLEAN_FILE, OUT_FILE)
    # Write output


def process_epa_region(DIR): 
 "used to process NERC regional cost factors for NERC regions"
    # process region data 

# create an empty pandas data frame with the required columns
df = pd.DataFrame(columns=['region', 'combined_cycle', 'combined_cycle_cc', 'combustion_turbine', 'land_turbine', 'solar_pv_storage', 'coal', 'coal_30_ccs', 'coal_90_ccs'])

# open the text file for reading
with open('region.txt', 'r') as file:
# read the file line by line
    for line in file:
    # split the line into a list of values using space as the separator
        values = line.strip().split()
    # create a dictionary with the values and column names as keys
        row_dict = {
        'region': values[0],
        "Gas": float(values[1]),
        'Gas_CC': float(values[1]),
        'Gas_CC_CCS': float(values[2]),
        'Gas_SC': float(values[3]),
        'Wind': float(values[6]),
        'Solar': float(values[7]),
        'Coal': float(values[10]),
        'Coal_30_CCS': float(values[11]),
        'Coal_90_CCS': float(values[12])
        }
        # append the dictionary as a new row to the data frame
        df = df.append(row_dict, ignore_index=True)

df.to_csv(os.path.join(os.getcwd(), "data", "processing", "EPA", "NERC_regional_cost_factors.csv"))


nerc_states = {
                'ERC_PHDL': ['AR', 'LA', 'OK', 'TX'],
                'ERC_REST': ['AL', 'AR', 'FL', 'GA', 'KS', 'LA', 'MO', 'MS', 'OK', 'TX'],
                'ERC_WEST': ['AZ', 'CA', 'NM', 'NV', 'UT'],
                'FRCC': ['FL', 'GA', 'NC','SC'],
                'MIS_AMSO': ['KS', 'MO', 'NE', 'OK'],
                'MIS_AR': ['AR'],
                'MIS_MS': ['LA', 'MS'],
                'MIS_IA': ['IA', 'MN', 'ND', 'SD'],
                'MIS_IL': ['IL'],
                'MIS_INKY': ['IN', 'KY'],
                'MIS_LA': ['LA'],
                'MIS_LMI': ['MI', 'WI'],
                'MIS_MAPP': ['AR', 'IA', 'IL', 'IN', 'KS', 'KY', 'MI', 'MN', 'MO', 'ND', 'NE', 'OH', 'OK', 'SD', 'TN', 'WI'],
                'MIS_MIDA': ['DE', 'DC', 'MD', 'NJ', 'OH', 'PA', 'VA', 'WV'],
                'MIS_MNWI': ['MI', 'WI'],
                'MIS_MO': ['MO'],
                'MIS_WOTA': ['MI', 'MN', 'WI'],
                'MIS_WUMS': ['AR', 'LA', 'MS'],
                'NENG_CT': ['CT'],
                'NENG_ME': ['ME'],
                'NENGREST': ['MA', 'NH', 'RI', 'VT'],
                'NY_Z_A': ['NY'],
                'NY_Z_B': ['NY'],
                'NY_Z_C&E': ['NY'],
                'NY_Z_D': ['NY'],
                'NY_Z_F': ['NY'],
                'NY_Z_G-I': ['NY'],
                'NY_Z_J': ['NY'],
                'NY_Z_K': ['NY'],
                'PJM_AP': ['DE', 'NJ', 'PA'],
                'PJM_ATSI': ['MI', 'OH'],
                'PJM_COMD': ['DE', 'DC', 'MD', 'NJ', 'PA', 'VA', 'WV'],
                'PJM_Dom': ['NJ', 'PA'],
                'PJM_EMAC': ['IL', 'IN', 'MI', 'OH'],
                'PJM_PENE': ['IL', 'IN', 'KY', 'MI', 'OH', 'TN', 'VA', 'WV'],
                'PJM_SMAC': ['MD', 'VA', 'WV'],
                'PJM_West': ['IL', 'IN', 'KY', 'MI', 'OH'],
                'PJM_WMAC': ['DC', 'MD', 'PA', 'VA', 'WV'],
                'S_C_KY': ['KY', 'TN', 'VA'],
                'S_C_TVA': ['AL', 'GA', 'KY', 'MS', 'NC', 'SC', 'TN', 'VA'],
                'S_D_AECI': ['AR', 'IA', 'MO', 'OK'],
                "S_SOU": ["MS","AL","GA"],
                "S_VACA": ["AZ", "CA", "NV"],
                "SPP_N": ["KS", "NE", "OK", "SD", "ND"],
                "SPP_NEBR": ["IA", "MN", "MO", "ND", "NE", "SD"],
                "SPP_SPS": ["CO", "KS", "NM", "OK", "TX"],
                "SPP_WAUE": ["IA", "MI", "MN", "MT", "ND", "SD", "WI"],
                "SPP_WEST": ["AZ", "CA", "CO", "ID", "KS", "MT", "ND", "NE", "NM", "NV", "OK", "OR", "SD", "TX", "UT", "WA", "WY"],
                "WEC_BANC": ["AK"],
                "WEC_CALN": ["CA"],
                "WEC_LADW": ["AZ", "CA"],
                "WEC_SDGE": ["CA"],
                "WECC_AZ": ["AZ"],
                "WECC_CO": ["CO"],
                "WECC_ID": ["ID"],
                "WECC_IID": ["CA"],
                "WECC_MT": ["MT"],
                "WECC_NM": ["NM"],
                "WECC_NNV": ["NV"],
                "WECC_PNW": ["OR", "WA"],
                "WECC_SCE": ["CA"],
                "WECC_SNV": ["NV"],
                "WECC_UT": ["UT"],
                "WECC_WY": ["WY"]}
us_states = ['AL','AK','AZ', 'AR', 'CA', 'CO', 'CT',"DC",'DE', 'FL', 'GA', 'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD', 'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ', 'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC', 'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY']
df1 = pd.DataFrame({
    "state": us_states,
    "Gas": [0]*len(us_states),
    "Gas_CC": [0]*len(us_states),
    "Gas_CC_CCS": [0]*len(us_states),
    "Gas_SC": [0]*len(us_states),
    "Wind": [0]*len(us_states),
    "Solar": [0]*len(us_states),
    "Coal": [0]*len(us_states),
    "Coal_30_CCS": [0]*len(us_states),
    "Coal_90_CCS": [0]*len(us_states)
})
state_lists = {state: [[] for _ in range(8)] for state in us_states}
for region in nerc_states: 
    states = nerc_states[region]
    for state in states: 
        state_lists[state][0].append(df.loc[df["region"]==region,"Gas"].iloc[0]) 
        state_lists[state][0].append(df.loc[df["region"]==region,"Gas_CC"].iloc[0]) 
        state_lists[state][1].append(df.loc[df["region"]==region,"Gas_CC_CCS"].iloc[0])                           
        state_lists[state][2].append(df.loc[df["region"]==region,"Gas_SC"].iloc[0])                                   
        state_lists[state][3].append(df.loc[df["region"]==region,"Wind"].iloc[0])        
        state_lists[state][4].append(df.loc[df["region"]==region,"Solar"].iloc[0]) 
        state_lists[state][5].append(df.loc[df["region"]==region,"Coal"].iloc[0]) 
        state_lists[state][6].append(df.loc[df["region"]==region,"Coal_30_CCS"].iloc[0])          
        state_lists[state][7].append(df.loc[df["region"]==region,"Coal_90_CCS"].iloc[0])

for state1 in us_states:
    if len(state_lists[state1][0]) == 0:
        df1.loc[df1["state"]==state1, "Gas"] = 1
        df1.loc[df1["state"]==state1, "Gas_CC"] = 1
        df1.loc[df1["state"]==state1, "Gas_CC_CCS"] = 1
        df1.loc[df1["state"]==state1, "Gas_SC"] = 1
        df1.loc[df1["state"]==state1, "Wind"] = 1
        df1.loc[df1["state"]==state1, "Solar"] = 1
        df1.loc[df1["state"]==state1, "Coal"] = 1
        df1.loc[df1["state"]==state1, "Coal_30_CCS"] = 1
        df1.loc[df1["state"]==state1, "Coal_90_CCS"] = 1
    else:
        df1.loc[df1["state"]==state1, "Gas"] = sum(state_lists[state1][0])/len(state_lists[state1][0])
        df1.loc[df1["state"]==state1, "Gas_CC"] = sum(state_lists[state1][0])/len(state_lists[state1][0])
        df1.loc[df1["state"]==state1, "Gas_CC_CCS"] = sum(state_lists[state1][1])/len(state_lists[state1][1])
        df1.loc[df1["state"]==state1, "Gas_SC"] = sum(state_lists[state1][2])/len(state_lists[state1][2])
        df1.loc[df1["state"]==state1, "Wind"] = sum(state_lists[state1][3])/len(state_lists[state1][3])
        df1.loc[df1["state"]==state1, "Solar"] = sum(state_lists[state1][4])/len(state_lists[state1][4])
        df1.loc[df1["state"]==state1, "Coal"] = sum(state_lists[state1][5])/len(state_lists[state1][5])
        df1.loc[df1["state"]==state1, "Coal_30_CCS"] = sum(state_lists[state1][6])/len(state_lists[state1][6])
        df1.loc[df1["state"]==state1, "Coal_90_CCS"] = sum(state_lists[state1][7])/len(state_lists[state1][7])
df1.to_csv(os.path.join(os.getcwd(), "data", "processing", "EPA", "NERC_state_cost_factors.csv"))