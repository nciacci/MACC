import os
import ftplib
import zipfile

import fileinput
import re

import pandas as pd

def download_unzip_format_cems(year, SAVE_DIR):
    '''Given year, download and unzip all CEMS files for that year.'''

    # Go to FTP folder with CEMS data
    print('Logging in to FTP...')
    ftp = ftplib.FTP('newftp.epa.gov')
    ftp.login()  # log in as anonymous user
    ftp.cwd('/dmdnload/emissions/hourly/monthly/{}/'.format(year))

    # Attempt to list all files in directory
    print('Getting filenames...')
    fnames = []
    try:
        fnames = ftp.nlst()
    except(ftplib.error_perm, resp):
        if str(resp) == '550 No files found':
            print('No files in this directory')
        else:
            raise

    # Download all files
    print('Downloading files...')
    download_path = create_path(os.path.join(SAVE_DIR, 'download', str(year)))
    for fname in fnames:
    # for fname in fnames[:3]:
        print(fname)
        with open(os.path.join(download_path, fname), 'wb') as f:
            ftp.retrbinary('RETR {}'.format(fname), f.write)

    # Unzip all files
    print('Unzipping files...')
    unzip_path = create_path(os.path.join(SAVE_DIR, 'unzipped', str(year)))
    for fname in os.listdir(download_path):
        print(fname)
        with zipfile.ZipFile(os.path.join(download_path, fname), 'r') as f:
            f.extractall(unzip_path) 

    # Process CSV files to ensure consistent and SQL-friendly format
    print('Processing files...')
    process_raw_cems(unzip_path)

def process_raw_cems(csv_dir):
    '''Process CSV files to ensure consistent and SQL-friendly format'''
    fpaths = [os.path.join(csv_dir, f) for f in os.listdir(csv_dir)]
    for line in fileinput.input(fpaths, inplace=1):
        # Remove commas that are inside quotation marks
        line = re.sub('\"([^\"]+),([^\"]+)\"', r'\1-\2',line)
        # Remove quotation marks
        line = line.replace("\"","")
        # Fix files that do not have FAC_ID and UNIT_ID by adding dummy columns for SQL import
        if line.count(',') == 21:
            line = line.rstrip() + ",-1,-1\n"
        print(line, end="")

def create_path(path):
    '''Helper function to create directories if needed.'''
    if not os.path.exists(path):
        os.makedirs(path)
    return path

def aggregate_cems(year, DIR):
    
    print("aggregating files")
    DATA_DIR = create_path(os.path.join(DIR, 'unzipped', str(year)))
    OUTPUT_DIR = create_path(os.path.join(DIR, 'aggregated', str(year)))
    OUTPUT_FILE = os.path.join(OUTPUT_DIR, "aggregated_cems.csv")


    indv_df = []

    for fname in os.listdir(DATA_DIR):
        print(fname)
        df = pd.read_csv(os.path.join(DATA_DIR, fname))
        df_agg = df.groupby(['ORISPL_CODE']).agg({'GLOAD (MW)': 'sum', 'CO2_MASS (tons)': 'sum', 'HEAT_INPUT (mmBtu)':'sum'})
        indv_df.append(df_agg)

    large_df = pd.concat(indv_df).groupby(['ORISPL_CODE']).agg({'GLOAD (MW)': 'sum', 'CO2_MASS (tons)': 'sum', 'HEAT_INPUT (mmBtu)':'sum'})
    large_df.to_csv(OUTPUT_FILE)

    return 0


if __name__ == "__main__":
    DIR = create_path('C:\\Users\\jonat\\Box Sync\\Research\\MACC\\Data\\pulling_data\\CEMS\\data')

    start_year = 2017
    end_year = 2017

    for year in range(start_year, end_year+1):
        print(year)
        # download_unzip_format_cems(year, SAVE_DIR)
        aggregate_cems(year, DIR)