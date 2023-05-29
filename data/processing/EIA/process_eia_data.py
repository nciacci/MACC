import os
import numpy as np
import pandas as pd


def merge_EIA(EIA_gen_file, EIA_plant_file, EIA_fuel_map_file, OUTFILE):
    cols = ["Plant Code", "Plant Name", "Generator ID", "Operating Year", "Nameplate Capacity (MW)", "Energy Source 1", "Technology"]
    loc_cols = ["Plant Code", "State", "Latitude" ,"Longitude"]

    eia_data_operable = pd.read_excel(EIA_gen_file, sheet_name="Operable", skiprows = 1, usecols=cols)
    eia_data_retired = pd.read_excel(EIA_gen_file, sheet_name="Retired and Canceled", skiprows = 1, usecols=cols)
    eia_all = pd.concat([eia_data_operable, eia_data_retired])
    
    eia_loc = pd.read_excel(EIA_plant_file, sheet_name="Plant", skiprows = 1, usecols=loc_cols)
    eia_fuel_map = pd.read_csv(EIA_fuel_map_file, index_col = "Technology")
    # eia_fuel_map = pd.read_csv(EIA_fuel_map_file, index_col = "Energy Source 1")
    # eia_primemover_map = pd.read_csv(EIA_primemover_map_file, index_col = "Prime Mover")
    fuel_dict = dict(zip(eia_fuel_map.index, eia_fuel_map.primary_fuel.values))
    # primemover_dict = dict(zip(eia_primemover_map.index, eia_primemover_map.prime_mover.values))
    

    eia_all['Nameplate Capacity (MW)'] = eia_all['Nameplate Capacity (MW)'].replace(' ', 0).fillna(0).astype(int)
    eia_all['Operating Year'] = eia_all['Operating Year'].replace(' ', 9999).fillna(9999).astype(int)
    
    eia_cap = eia_all.groupby(['Plant Code', "Plant Name"]).agg({'Nameplate Capacity (MW)': 'sum'})
    eia_year = eia_all.groupby(['Plant Code', "Plant Name"]).agg({'Operating Year': 'min'})
    eia_cap_fuel = eia_all.groupby(['Plant Code', "Plant Name", "Technology"]).agg({'Nameplate Capacity (MW)': 'sum'}).reset_index()

    eia_assumed_fuel = eia_cap_fuel.groupby(["Plant Code", "Plant Name"], as_index=False).apply(lambda df:df.sort_values("Nameplate Capacity (MW)", ascending=False).head(1)).droplevel(0).sort_values("Plant Code", ascending=False)[["Plant Code", "Plant Name", "Technology"]]

    eia_cap_fuel_pm = eia_assumed_fuel.merge(eia_year, on = "Plant Code", how = "left").merge(eia_cap, on = "Plant Code", how = "left").merge(eia_loc, on = "Plant Code", how = "left")

    eia_cap_fuel_pm["primary_fuel"] = eia_cap_fuel_pm["Technology"].map(fuel_dict)
    # eia_cap_fuel_pm["primary_fuel"] = eia_cap_fuel_pm["Energy Source 1"].map(fuel_dict)
    # eia_cap_fuel_pm["Prime Mover"] = eia_cap_fuel_pm["Prime Mover"].map(primemover_dict)
    eia_cap_fuel_pm.to_csv(OUTFILE, index = False)
    return eia_cap_fuel_pm

def create_path(path):
    '''Helper function to create directories if needed.'''
    if not os.path.exists(path):
        os.makedirs(path)
    return path


if __name__ == "__main__":
    YEAR = 2020

    DIR = create_path('C:\\Users\\jonat\\OneDrive\\Desktop\\General\\School\\Stanford\\Research\\MACC\\MACCpy\\data\\processing\\EIA')
    EIA_FILE = os.path.join(DIR, "..", "..", "raw", "EIA", str(YEAR), "3_1_Generator_Y"+str(YEAR)+".xlsx" )
    EIA_LOC_FILE = os.path.join(DIR, "..", "..", "raw", "EIA", str(YEAR), "2___Plant_Y"+str(YEAR)+".xlsx" )
    EIA_FUEL_FILE = os.path.join(DIR, "eia_tech_mapping.csv" )
    # EIA_FUEL_FILE = os.path.join(DIR, "eia_fuel_mapping.csv" )
    # EIA_PRIMEMOVER_FILE = os.path.join(DIR, "eia_primemover_mapping.csv" )
    OUT_FILE = os.path.join(DIR, str(YEAR), "EIA_mapping_loc.csv")

    merge_EIA(EIA_FILE, EIA_LOC_FILE, EIA_FUEL_FILE, OUT_FILE)
    