#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import folium
import pandas as pd
import numpy as np
import geopandas as gpd
from bokeh.io import curdoc, output_notebook,show, output_file
from bokeh.models import Slider, HoverTool
from bokeh.layouts import widgetbox, row, column
from bokeh.plotting import figure
from bokeh.models import GeoJSONDataSource, LinearColorMapper, ColorBar
from bokeh.palettes import brewer
from bokeh.io import export_png
import json
import pdb

def get_cumulative(df):
    '''Calculate cumulative cases and deaths
    '''
    #Cumulative calcs
    countries = ecdc_data['countriesAndTerritories'].unique()

    ecdc_data['cumulative_deaths'] = 0
    ecdc_data['cumulative_cases'] = 0
    for country in countries:
        country_data = ecdc_data[ecdc_data['countriesAndTerritories']==country]
        index = country_data.index
        country_data = country_data.reset_index()
        cum_deaths = country_data['deaths'].cumsum().values
        cum_cases = country_data['cases'].cumsum().values
        ecdc_data.loc[index,'cumulative_deaths']=np.array(cum_deaths)
        ecdc_data.loc[index,'cumulative_cases']=np.array(cum_cases)


def json_data(selectedDate):
    df_date = ecdc_df[ecdc_df['dateRep']==selectedDate]
    merged = gdf.merge(df_date, left_on = 'country_code', right_on ='countryterritoryCode', how = 'left')
    merged.fillna('No data', inplace = True)
    merged_json = json.loads(merged.to_json())
    json_data = json.dumps(merged_json)
    return json_data

########MAIN#########
#ecdc data
ecdc_df = pd.read_csv('ecdc_20200817.csv')
ecdc_df['date'] = pd.to_datetime(ecdc_df['dateRep'], format='%d/%m/%Y')
ecdc_df = ecdc_df.sort_values(by=['date'], ascending=False)
ecdc_df = ecdc_df.drop(columns=['date'])

#Read shapefile using Geopandas
shapefile = './countries_110m/ne_110m_admin_0_countries.shp'
#Rename columns.
gdf = gpd.read_file(shapefile)[['ADMIN', 'ADM0_A3', 'geometry']]
gdf.columns = ['country', 'country_code', 'geometry']
#Drop Antarctica
gdf = gdf.drop(gdf.index[159])

#Input GeoJSON source that contains features for plotting.
dates = ecdc_df['dateRep'].unique()
geosource = GeoJSONDataSource(geojson = json_data(dates[0]))

#Define a sequential multi-hue color palette.
palette = brewer['Reds'][9]
#Reverse color order so that dark blue is highest.
palette = palette[::-1]
#Instantiate LinearColorMapper that linearly maps numbers in a range, into a sequence of colors. Input nan_color.
color_mapper = LinearColorMapper(palette = palette, low = 0, high = 500, nan_color = '#d9d9d9')
#Add hover tool
hover = HoverTool(tooltips = [ ('Country/region','@country'),('Deaths', '@deaths')])

#Create color bar.
color_bar = ColorBar(color_mapper=color_mapper, label_standoff=8,
                     width = 500, height = 20,
                     border_line_color=None,location = (0,0),
                     orientation = 'horizontal')
#Create figure object.
p = figure(title = 'Deaths on '+dates[0], plot_height = 600 , plot_width = 950, toolbar_location = None, tools = [hover])
p.xgrid.grid_line_color = None
p.ygrid.grid_line_color = None#Add patch renderer to figure.
p.patches('xs','ys', source = geosource,
          fill_color = {'field' :'deaths', 'transform' : color_mapper},
          line_color = 'black', line_width = 0.25, fill_alpha = 1)

#Specify layout
p.add_layout(color_bar, 'below')
# Define the callback function: update_plot

def update_plot(attr, old, new):
    date = dates[len(dates)-1-slider.value]
    new_data = json_data(date)
    geosource.geojson = new_data
    p.title.text = 'Deaths on '+ date



# Make a slider object: slider
slider = Slider(title = 'Date',start = 0, end = len(dates)-1, step = 1, value = len(dates)-1)
slider.on_change('value', update_plot)# Make a column layout of widgetbox(slider) and plot, and add it to the current document
layout = column(p,widgetbox(slider))
curdoc().add_root(layout)#Display plot inline in Jupyter notebook
#output_notebook()#Display plot
#show(layout)
curdoc().add_periodic_callback(update_plot, 60)
session.loop_until_closed() # run forever
