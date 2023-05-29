from plotnine import *
import numpy as np
import constants
import pandas as pd 
import os 
import sys

import requests
import csv
import plotly.express as px
import matplotlib.pylab as plt
import plotly.io as pio


def plot_MACC(df, title = "Power Plant MACC", x_lab = "tonnes of CO2", y_lab = "$/tonne CO2", x_min = None, x_max = None, y_min = None, y_max = None, save = True, file = "MACC_plot.png"):
    """
    This function takes a MACC data frame and graphs it in a figure that can be saved externally and is returned

    Args:
        df (pandas df)         : A df with plant level and sorted replacement decisions for a MACC
        title (str, optional)  : The title to be added at the top of the figure. Defaults to "Power Plant MACC".
        x_lab (str, optional)  : X axis label. Defaults to "tonnes of CO2".
        y_lab (str, optional)  : Y axis label. Defaults to "$/tonne CO2".
        x_min (float, optional): Sets a minimum x value to crop the graph at. Defaults to None.
        x_max (float, optional): Sets a maximum x value to crop the graph at. Defaults to None.
        y_min (float, optional): Sets a minimum y value to crop the graph at. Defaults to None.
        y_max (float, optional): Sets a maximum y value to crop the graph at. Defaults to None.
        save (bool, optional)  : Whether to save the figure to "file". Defaults to True.
        file (str, optional)   : File path to save the figure. Defaults to "MACC_plot.png".

    Returns:
        Matplot lib figure     :  A figure to display the MACC
    """
    
    fig = (
      ggplot(df) +
        aes(xmin = "cum_red_prev", 
            xmax = "cum_red",
            ymin = 0, 
            ymax = "metric",
            fill = "ori_rep")+
        geom_rect()+
        # geom_label(aes(x = lab_xloc, y = lab_yloc, label = round(lab_val, 3)), size = 5)+
         labs(
            x=x_lab,
            y=y_lab,
            fill="Fuel Switch",
            title=title)
        + scale_fill_manual(values = constants.colors)
        # ylim(-200,200)+
        # xlim(0,1.2)
    ) 
    if x_min or x_max:
        fig = fig + xlim(x_min,x_max)
    if y_min or y_max:
        fig = fig + ylim(y_min,y_max)

    if save:
        fig = fig + theme_bw()        
        fig = fig + scale_y_continuous(breaks=np.arange(-200, 201, 50), limits=[-200, 200])
        fig = fig + scale_x_continuous(breaks=np.arange(0, 1.01, 0.2), limits=[0, 1])   
        fig.save(file, dpi=600)
    
    return fig

def plot_avg_MACC_per_state(df, title = "Power Plant MACC", x_lab = "tonnes of CO2", y_lab = "$/tonne CO2", x_min = None, x_max = None, y_min = None, y_max = None, save = True, file = "MACC_plot.png"):
    """
    This function takes a MACC data frame and graphs it in a figure that can be saved externally and is returned
    The function averages the MACC number per state then plots it.
    Args:
        df (pandas df)         : A df with plant level and sorted replacement decisions for a MACC
        title (str, optional)  : The title to be added at the top of the figure. Defaults to "Power Plant MACC".
        x_lab (str, optional)  : X axis label. Defaults to "tonnes of CO2".
        y_lab (str, optional)  : Y axis label. Defaults to "$/tonne CO2".
        x_min (float, optional): Sets a minimum x value to crop the graph at. Defaults to None.
        x_max (float, optional): Sets a maximum x value to crop the graph at. Defaults to None.
        y_min (float, optional): Sets a minimum y value to crop the graph at. Defaults to None.
        y_max (float, optional): Sets a maximum y value to crop the graph at. Defaults to None.
        save (bool, optional)  : Whether to save the figure to "file". Defaults to True.
        file (str, optional)   : File path to save the figure. Defaults to "MACC_plot.png".

    Returns:
        Matplot lib figure     :  A figure to display the MACC
    """
    # Sort by state
    # Find avergage MACC per state 
    state_avg_MACC = df.groupby('state')['metric'].mean()
    # Find emissions reduction per state 
    state_red = df.groupby('state')['em_red'].sum()
    # Make new df with data per state instead of plants 
    df_state = pd.DataFrame()
    df_state["state"] = list(constants.US_STATE_ABB)
    df_state = pd.merge(pd.merge(state_avg_MACC,state_red,on="state"),df_state, on='state')
    #Sort by MACC number 
    df_state.sort_values("metric", inplace=True)
    df_state["cum_red"] = np.cumsum(df_state["em_red"])/constants.giga
    df_state["cum_red_prev"] = (np.cumsum(df_state["em_red"])-df_state["em_red"])/constants.giga
    df_state.sort_values("em_red", inplace=True)
    df_state.to_csv(os.path.join(os.getcwd(), "output", "MACC_DATA", "2022_state.csv"))
    

    fig = (
        ggplot(df_state) +
            aes(xmin="cum_red_prev", 
                xmax="cum_red",
                ymin=0, 
                ymax="metric",
                fill="state") +
            geom_rect() +
            #geom_label(aes(x=(df_state['cum_red_prev'] + df_state['cum_red']) / 2, 
                        #y=[-10 if i % 2 == 0 else 10 for i in range(len(df_state))], 
                        #label=df_state['state']), 
                    #size=5, 
                    #position = position_nudge(x = 0.01, y = 0.01)
                    #) 
            
            labs(
                x=x_lab,
                y=y_lab,
                fill='state',
                title=title) +
            scale_fill_manual(values=constants.state_colors) #+
            #guides(fill=False) +
            #theme(legend_position="")
    )

    if x_min or x_max:
        fig = fig + xlim(x_min,x_max)
    if y_min or y_max:
        fig = fig + ylim(y_min,y_max)

    if save:
        fig = fig + theme_bw()        
        fig = fig + scale_y_continuous(breaks=np.arange(-200,201, 50), limits=[-200, 200])
        fig = fig + scale_x_continuous(breaks=np.arange(0, 1.01, 0.2), limits=[0, 1])   
        fig.save(file, dpi=600)
    
    return fig

def highlight_state(df, state, title = "Power Plant MACC", x_lab = "tonnes of CO2", y_lab = "$/tonne CO2", save = True, file = "MACC_plot.png"):
    """
    This function takes a MACC data frame and graphs it in a figure that can be saved externally and is returned.
    It highlights a particular state out of the entire graph and sets all other states to a grey color

    Args:
        df (pandas df)         : A df with plant level and sorted replacement decisions for a MACC
        state (str)            : Which state to emphasize in the figure
        title (str, optional)  : The title to be added at the top of the figure. Defaults to "Power Plant MACC".
        x_lab (str, optional)  : X axis label. Defaults to "tonnes of CO2".
        y_lab (str, optional)  : Y axis label. Defaults to "$/tonne CO2".
        x_min (float, optional): Sets a minimum x value to crop the graph at. Defaults to None.
        x_max (float, optional): Sets a maximum x value to crop the graph at. Defaults to None.
        y_min (float, optional): Sets a minimum y value to crop the graph at. Defaults to None.
        y_max (float, optional): Sets a maximum y value to crop the graph at. Defaults to None.
        save (bool, optional)  : Whether to save the figure to "file". Defaults to True.
        file (str, optional)   : File path to save the figure. Defaults to "MACC_plot.png".

    Returns:
        Matplot lib figure     :  A figure to display the MACC
    """
    
    state_data = df[df.state == state]
    other_data = df[df.state != state]
    other_data.loc[:, "ori_rep"] = "National"
    fig = (
      ggplot() +
        aes(xmin = "cum_red_prev", 
            xmax = "cum_red",
            ymin = 0, 
            ymax = "metric",
            fill = "ori_rep")+
        geom_rect(data = other_data, alpha = 0.4) +
        geom_rect(data = state_data) +
        # geom_label(aes(x = lab_xloc, y = lab_yloc, label = round(lab_val, 3)), size = 5)+
         labs(
            x=x_lab,
            y=y_lab,
            fill="Fuel Switch",
            title=title)
        + scale_fill_manual(values = constants.colors)
        # + scale_alpha_manual(values = constants.alphas, labels = 'none')
        # ylim(-200,200)+
        # xlim(0,1.2)
    ) 

    if save:
        fig.save(file, dpi=600)
    
    return fig

def plot_state_MACC(df,state,title = "Power Plant MACC", x_lab = "tonnes of CO2", y_lab = "$/tonne CO2", x_min = None, x_max = None, y_min = None, y_max = None, save = True, file = "MACC_plot.png"):
    """
    This function takes a MACC data frame and graphs it in a figure that can be saved externally and is returned
    The function averages the MACC number per state then plots it.
    Args:
        df (pandas df)         : A df with plant level and sorted replacement decisions for a MACC
        title (str, optional)  : The title to be added at the top of the figure. Defaults to "Power Plant MACC".
        x_lab (str, optional)  : X axis label. Defaults to "tonnes of CO2".
        y_lab (str, optional)  : Y axis label. Defaults to "$/tonne CO2".
        x_min (float, optional): Sets a minimum x value to crop the graph at. Defaults to None.
        x_max (float, optional): Sets a maximum x value to crop the graph at. Defaults to None.
        y_min (float, optional): Sets a minimum y value to crop the graph at. Defaults to None.
        y_max (float, optional): Sets a maximum y value to crop the graph at. Defaults to None.
        save (bool, optional)  : Whether to save the figure to "file". Defaults to True.
        file (str, optional)   : File path to save the figure. Defaults to "MACC_plot.png".

    Returns:
        Matplot lib figure     :  A figure to display the MACC
    """

    title = state + " 2022 MACC"

    # Sort by state
    state_data = df[df.state == state]
    # Reset emissions 
    state_data["cum_red"] = np.cumsum(state_data["em_red"])/constants.giga
    state_data["cum_red_prev"] =(np.cumsum(state_data["em_red"])-state_data["em_red"])/constants.giga
   

    # Save state data 
    state_data.to_csv(os.path.join(os.getcwd(), "output", "MACC_DATA","State",state+"_2022.csv"))
    
    

    # Plot 
    fig = (
      ggplot(state_data) +
        aes(xmin = "cum_red_prev", 
            xmax = "cum_red",
            ymin = 0, 
            ymax = "metric",
            fill = "ori_rep")+
        geom_rect()+
        # geom_label(aes(x = lab_xloc, y = lab_yloc, label = round(lab_val, 3)), size = 5)+
         labs(
            x=x_lab,
            y=y_lab,
            fill="Fuel Switch",
            title=title)
        + scale_fill_manual(values = constants.colors)
    ) 
    if x_min or x_max:
        fig = fig + xlim(x_min,x_max)
    if y_min or y_max:
        fig = fig + ylim(y_min,y_max)

    if save:
        fig = fig + theme_bw()        
        fig.save(file, dpi=600)

    
    return fig

def age_dist_plot(df):
    # ranges
    rangeMin = df["age"].min()
    rangeMax = df["age"].max()
        
    # the plotting
    #
    # coal 
    fig = px.choropleth(df,
                        locations='state', 
                        locationmode="USA-states", 
                        scope="usa",
                        color='age',
                        color_continuous_scale="turbo",
                        range_color=[rangeMin, rangeMax]
                        #
                        )
    # update title
    fig.update_layout(coloraxis_colorbar_title_text = 'age (yrs)')
    fig.update_coloraxes(colorbar_len=0.8)

    # save settings
    saveBool = True
    if saveBool:
        pio.kaleido.scope.default_format = "pdf"
        img_bytes = fig.to_image(format="pdf")
        #
        localName = 'Age Distribution Coal'
        pio.write_image(fig, localName + ".svg", width=1.5*600, height=1*600, scale=1)
        pio.write_image(fig, localName + ".png", width=1.5*2000, height=1*2000, scale=1)
    fig.show()

def cf_plot(df,df_MACC): 
    import plotly.graph_objects as go

    # Create a scatter_geo trace
    trace = go.Scattergeo(
        lon = df['longitude'],
        lat = df['latitude'],
        mode = 'markers',
        marker = dict(
            size = 5,
            color = df['capacity_factor'],
            colorscale = 'YlOrRd',
            cmax = df['capacity_factor'].max(),
            cmin = df['capacity_factor'].min(),
            colorbar = dict(title = 'Capacity Factor')
        )
        )
    # Define a dictionary to map power plant types to marker symbols
    type_to_symbol = {
    'Wind': 'circle',
    'Gas': 'square',
    'Solar': 'diamond',
    # Add more type-symbol mappings as needed
    }
    # Define the border color and width
    border_color = 'black'
    border_width = 1
    marker_symbols = [type_to_symbol[plant_type] for plant_type in df_MACC['rep_fuel']]
    marker_sizes = df_MACC['new_capacity']/1000*2

    marker1 = go.scattergeo.Marker(
    symbol=marker_symbols,  # Assign the marker symbols based on the power plant types
    size=marker_sizes,  # Set the marker sizes based on the power plant sizes
    line=dict(
        color=border_color,  # Set the border color
        width=border_width  # Set the border width
    )
)
    trace1 = go.Scattergeo(
        lon = df_MACC['lon'],
        lat = df_MACC['lat'],
        mode = 'markers',
        marker = marker1
        )
    # Create the layout
    layout = go.Layout(
        title = 'Capacity Factors for Wind in the US',
        geo = dict(
            scope = 'usa',
            projection = dict(type='albers usa'),
            showland = True,
            landcolor = 'rgb(217, 217, 217)',
            subunitcolor = 'rgb(255, 255, 255)',
            countrycolor = 'rgb(255, 255, 255)',
            countrywidth = 0.5,
            subunitwidth = 0.5,
            showsubunits=True
        )
    )

    # Create the figure
    fig = go.Figure(data=[trace,trace1], layout=layout)

    # Display the plot
    fig.show()
    # save settings
    saveBool = True

