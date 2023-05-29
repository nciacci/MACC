# Functions for Data Analysis 

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


def get_state_data(plant_data, state):
    """
    Returns state data from plant data
    Prints: 
        number of plants in state
        number of coal plants in state
        number of natural gas plants in state
    """
    state_data = plant_data[plant_data['state'] == state]
    print("Number of plants in " + state + ": " + str(len(state_data)))
    print("Number of coal plants in " + state + ": " + str(len(state_data[state_data['primary_fuel'] == 'Coal'])))
    print("Number of natural gas plants in " + state + ": " + str(len(state_data[state_data['primary_fuel'] == 'natural gas'])))

    print()
    return state_data
