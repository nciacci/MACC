##################################
#  importing the requests library
import requests
import csv
import pandas as pd
import numpy as np
import plotly.express as px
import matplotlib.pylab as plt
import plotly.io as pio


##################
### pre-processing
df = pd.read_csv('2022_MACC.csv')
# fuel types
fuelTypes = ["Coal", "Oil", "Gas", "Solar", "Wind"]


# sum emReduction based on same state
enMixState = []
enMixCoal = []
enMixGas = []
enMixSolar = []
enMixWind = []
for state in df.state.unique():
    # energy mix distribution of given state
    locdf = df[df['state'] == state]
    # split based on MAC metric:
    upToMAC = 200
    idx_split = locdf.metric <= upToMAC
    replaced_df = locdf[idx_split]    
    remained_df = locdf[~idx_split]

    # first remained
    energyMix_remained = []
    for fuel in fuelTypes:
        # find idx
        idx = remained_df.primary_fuel.str.contains(fuel)
        # filter dataframe
        localdf = remained_df[idx]
        # total energy
        localCap = localdf.capacity.sum() / 1000
        energyMix_remained.append(localCap)
    # then replaced
    energyMix_replaced = []
    for fuel in fuelTypes:
        # find idx
        idx = replaced_df.rep_fuel.str.contains(fuel)
        # filter dataframe
        localdf = replaced_df[idx]
        # total energy
        localCap = localdf.new_capacity.sum() / 1000
        energyMix_replaced.append(localCap)
    # combine!
    energyMix = np.array(energyMix_replaced) + np.array(energyMix_remained)
    # normalize
    energyMix = energyMix / energyMix.sum() * 100

    # add
    enMixState.append(state)
    enMixCoal.append(energyMix[0])
    enMixGas.append(energyMix[2])
    enMixSolar.append(energyMix[3])
    enMixWind.append(energyMix[4])






# create df
d = {'state': enMixState, 'Coal': enMixCoal, 'Gas': enMixGas, 'Solar': enMixSolar, 'Wind': enMixWind}
df_enMix = pd.DataFrame(data=d)





# ranges
rangeMin = 0
rangeMax = 100


# the plotting
#
# coal 
fig = px.choropleth(df_enMix,
                    locations='state', 
                    locationmode="USA-states", 
                    scope="usa",
                    color='Coal',
                    color_continuous_scale="turbo",
                    range_color=[rangeMin, rangeMax]
                    #
                    )
# update title
fig.update_layout(coloraxis_colorbar_title_text = '[%]')
fig.update_coloraxes(colorbar_len=0.8)

# save settings
saveBool = True
if saveBool:
    pio.kaleido.scope.default_format = "pdf"
    img_bytes = fig.to_image(format="pdf")
    #
    localName = 'EnergyMix_Coal_MAC1'
    pio.write_image(fig, localName + ".svg", width=1.5*600, height=1*600, scale=1)
    pio.write_image(fig, localName + ".png", width=1.5*2000, height=1*2000, scale=1)
fig.show()

#
# gas 
fig = px.choropleth(df_enMix,
                    locations='state', 
                    locationmode="USA-states", 
                    scope="usa",
                    color='Gas',
                    color_continuous_scale="turbo",
                    range_color=[rangeMin, rangeMax]
                    #
                    )
# update title
fig.update_layout(coloraxis_colorbar_title_text = '[%]')
fig.update_coloraxes(colorbar_len=0.8)

# save settings
saveBool = True
if saveBool:
    pio.kaleido.scope.default_format = "pdf"
    img_bytes = fig.to_image(format="pdf")
    #
    localName = 'EnergyMix_Gas_MAC1'
    pio.write_image(fig, localName + ".svg", width=1.5*600, height=1*600, scale=1)
    pio.write_image(fig, localName + ".png", width=1.5*2000, height=1*2000, scale=1)
fig.show()

#
# solar 
fig = px.choropleth(df_enMix,
                    locations='state', 
                    locationmode="USA-states", 
                    scope="usa",
                    color='Solar',
                    color_continuous_scale="turbo",
                    range_color=[rangeMin, rangeMax]
                    #
                    )
# update title
fig.update_layout(coloraxis_colorbar_title_text = '[%]')
fig.update_coloraxes(colorbar_len=0.8)

# save settings
saveBool = True
if saveBool:
    pio.kaleido.scope.default_format = "pdf"
    img_bytes = fig.to_image(format="pdf")
    #
    localName = 'EnergyMix_Solar_MAC1'
    pio.write_image(fig, localName + ".svg", width=1.5*600, height=1*600, scale=1)
    pio.write_image(fig, localName + ".png", width=1.5*2000, height=1*2000, scale=1)
fig.show()

#
# wind 
fig = px.choropleth(df_enMix,
                    locations='state', 
                    locationmode="USA-states", 
                    scope="usa",
                    color='Wind',
                    color_continuous_scale="turbo",
                    range_color=[rangeMin, rangeMax]
                    #
                    )
# update title
fig.update_layout(coloraxis_colorbar_title_text = '[%]')
fig.update_coloraxes(colorbar_len=0.8)

# save settings
saveBool = True
if saveBool:
    pio.kaleido.scope.default_format = "pdf"
    img_bytes = fig.to_image(format="pdf")
    #
    localName = 'EnergyMix_Wind_MAC1'
    pio.write_image(fig, localName + ".svg", width=1.5*600, height=1*600, scale=1)
    pio.write_image(fig, localName + ".png", width=1.5*2000, height=1*2000, scale=1)
fig.show()

