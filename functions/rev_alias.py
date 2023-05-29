# -*- coding: utf-8 -*-
"""
Created on Sat Feb 26 10:12:05 2022

@author: jonat
"""

import os
import numpy as np

from reV import TESTDATADIR
from reV.config.project_points import ProjectPoints
from reV.generation.generation import Gen

# To be honest, I have no idea what files correspond to what outputs.
# These are the examples they had up for wind and solar, but I don't know
# what they are or what I would change them to. 

file_map = {"Wind":{"res":os.path.join(TESTDATADIR, 'wtk/ri_100_wtk_2012.h5'),
                    "sam":os.path.join(TESTDATADIR, 'SAM/wind_gen_standard_losses_0.json'),
                    "opt":"windpower"},
            "Solar":{"res":os.path.join(TESTDATADIR, 'nsrdb/ri_100_nsrdb_2013.h5'),
                    "sam":os.path.join(TESTDATADIR, 'SAM/naris_pv_1axis_inv13.json'),
                    "opt":"pvsamv1"}}

def get_cf(lat_lons, source, desired_out = ("cf_mean")):
    if source not in file_map:
        raise "Fuel not mapped"
    
    res_file = file_map[source]['res']
    sam_file = file_map[source]['sam']
    opt = file_map[source]['opt']
    
    pp = ProjectPoints.lat_lon_coords(lat_lons, res_file, sam_file)
    gen = Gen.reV_run(opt, pp, sam_file, res_file, output_request=desired_out)
    
    return gen

