import os
import pandas as pd


def join_CEMS_EIA(CEMS_file, EIA_file, OUT_FILE):
    cems_data = pd.read_csv(CEMS_file)
    eia_data = pd.read_csv(EIA_file)

    merged_data = cems_data.merge(eia_data, how="inner", left_on="ORISPL_CODE", right_on="Plant Code")

    # Convert units and rename columns
    merged_data["GLOAD (kWh)"]= merged_data["GLOAD (MW)"]*1000
    out_cols = ["name", "state", "lat", "lon", "commissioning_year", "primary_fuel", "capacity", "generation", "fuel_consumption", "emissions"]
    in_cols = ["Plant Name","State","Latitude","Longitude","Operating Year", "primary_fuel","Nameplate Capacity (MW)","GLOAD (kWh)"	,"HEAT_INPUT (mmBtu)"	,"CO2_MASS (tons)"]

    col_map = dict(zip(in_cols, out_cols))
    merged_data.rename(columns = col_map, inplace = True)

    with open(OUT_FILE, 'w') as f:
        f.write("# Units: NA, NA, lat, lon, year, NA, NA, MW, kWh, mmbtu, metric tonne CO2\n")
    merged_data.to_csv(OUT_FILE, index=False, columns = out_cols, mode = 'a')

    return merged_data

def create_path(path):
    '''Helper function to create directories if needed.'''
    if not os.path.exists(path):
        os.makedirs(path)
    return path

if __name__ == "__main__":
    DIR = create_path('C:\\Users\\jonat\\OneDrive\\Desktop\\General\\School\\Stanford\\Research\\MACC\\MACCpy\\data\\processing')

    start_year = 2020
    end_year = 2020

    for year in range(start_year, end_year+1):
        CEMS_FILE = os.path.join(DIR, "CEMS", str(year), "aggregated_cems.csv")
        EIA_FILE = os.path.join(DIR, "EIA", str(year), "EIA_mapping_loc.csv")

        OUT_DIR = create_path(os.path.join(DIR, "EIA_CEMS", str(year)))
        OUT_FILE = os.path.join(OUT_DIR, "joined_data.csv")
        
        join_CEMS_EIA(CEMS_FILE, EIA_FILE, OUT_FILE)