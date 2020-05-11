#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
import geopandas as gpd
from bokeh.io import curdoc, output_notebook,show, output_file
from bokeh.models import Slider,CustomJSFilter, CDSView, HoverTool, ColumnDataSource, CustomJS
from bokeh.layouts import widgetbox, row, column, layout
from bokeh.plotting import figure, output_file, show, save
from bokeh.models import GeoJSONDataSource, LinearColorMapper, ColorBar, CDSView
from bokeh.palettes import brewer
import json
import shapely
import matplotlib.pyplot as plt
import argparse
import pdb

###FUNCTIONS###
def read_data():
    '''Read in all data for plotting
    '''

    #WORLD MAP
    #Country polygons
    shapefile = './countries_110m/ne_110m_admin_0_countries.shp'#Read shapefile using Geopandas
    gdf = gpd.read_file(shapefile)[['ADMIN', 'ADM0_A3', 'geometry']]#Rename columns.
    gdf.columns = ['country', 'country_code', 'geometry']
    #Drop Antarctica
    gdf = gdf.drop(gdf.index[159])
    #Population density
    poecdc_capital = pd.read_csv('/home/patrick/COVID19.github.io/visualize/API_EN.POP.DNST_DS2_en_csv_v2_988966/API_EN.POP.DNST_DS2_en_csv_v2_988966.csv')
    #Create json file with population density and country polygon data
    merged = gdf.merge(poecdc_capital, left_on = 'country_code', right_on ='Country Code', how = 'left')
    merged.fillna('No data', inplace = True)
    merged_json = json.loads(merged.to_json())
    json_data = json.dumps(merged_json)
    geosource = GeoJSONDataSource(geojson = json_data)

    #CAPITAL LOCATONS
    #Get populated places (long,lat)
    shapefile ='/home/patrick/COVID19.github.io/visualize/pop_places_110m/ne_110m_populated_places_simple.shp'
    gdf_pop = gpd.read_file(shapefile)
    gdf_pop = gdf_pop.drop_duplicates(subset='sov_a3', keep='last') #Get capitals
    #ecdc
    ecdc_df = pd.read_csv('ecdc_20200505.csv')
    #Merge gdf_pop with ecdc
    ecdc_capital = gdf_pop.merge(ecdc_df, left_on = 'sov_a3', right_on ='countryterritoryCode', how = 'left')
    #Create date index
    ecdc_capital['dateRep'] = pd.to_datetime(ecdc_capital['dateRep'], format='%d/%m/%Y')
    dates = ecdc_capital['dateRep'].dropna().unique() #Drop nans and get unique
    dates = np.sort(dates) #sort
    dates = np.array(dates, dtype='datetime64[D]')
    ecdc_capital['date_index'] = 0
    for i in range(len(dates)):
        index = ecdc_capital[ecdc_capital['dateRep']==dates[i]].index
        ecdc_capital.loc[index,'date_index']=i+1

    #Get the total population 2018 (worldbank data)
    wb_data = pd.read_csv('../worldbank/population_total.csv')
    ecdc_capital = ecdc_capital.merge(wb_data, left_on = 'countryterritoryCode', right_on ='Country Code', how = 'left')
    #Normalize by population size
    ecdc_capital['norm_deaths'] = ecdc_capital['deaths']/ecdc_capital['2018']
    ecdc_capital['norm_cases'] = ecdc_capital['cases']/ecdc_capital['2018']
    #Create a geodf
    ecdc_capital = gpd.GeoDataFrame(ecdc_capital,geometry = ecdc_capital.geometry)
    # Get x and y coordinates
    ecdc_capital['x'] = [geometry.x for geometry in ecdc_capital['geometry']]
    ecdc_capital['y'] = [geometry.y for geometry in ecdc_capital['geometry']]
    ecdc_capital = ecdc_capital.drop('geometry', axis = 1).copy()
    ecdc_capital['deaths_size'] = ecdc_capital['norm_deaths']*1000000
    ecdc_capital['cases_size'] = ecdc_capital['norm_cases']*50000


    #Mobility data
    mobility_data = pd.read_csv('./Global_Mobility_Report.csv')
    #Convert to datetime
    mobility_data['date']=pd.to_datetime(mobility_data['date'], format='%Y/%m/%d')
    #Match mobility data by date and country

    return geosource, ecdc_capital, dates

def world_map(geosource, ecdc_capital, dates, metric):
    '''Create world map and write to html with javascript
    '''
    data = dict(longitude=np.array(ecdc_capital['x']),
            latitude=np.array(ecdc_capital['y']),
            date_index=np.array(ecdc_capital['date_index']),
            Metric=np.array(ecdc_capital[metric]),
            Metric_size=np.array(ecdc_capital[metric+'_size']),
            country = np.array(ecdc_capital['countriesAndTerritories']))
    source = ColumnDataSource(data=data)

    #Define a sequential multi-hue color palette.
    palette = brewer['YlGnBu'][9]
    #Reverse color order so that dark blue is highest.
    palette = palette[::-1]
    #Instantiate LinearColorMapper that linearly maps numbers in a range, into a sequence of colors. Input nan_color.
    color_mapper = LinearColorMapper(palette = palette, low = 0, high = 500, nan_color = '#d9d9d9')
    #Create color bar.
    color_bar = ColorBar(color_mapper=color_mapper, label_standoff=8, title='Population density per sq.km.',
                         width = 500, height = 20,
                         border_line_color=None,location = (0,0),
                         orientation = 'horizontal')
    p = figure(title = 'Deaths per day and population size on '+ str(dates[-1]), plot_height = 600 , plot_width = 950,
               toolbar_location = 'below',
               tools = "pan, wheel_zoom, box_zoom, reset")
    #Turn off plot lines
    p.xgrid.grid_line_color = None
    p.ygrid.grid_line_color = None
    p.xaxis.axis_line_color = None
    p.yaxis.axis_line_color = None
    p.xaxis.major_tick_line_color = None  # turn off x-axis major ticks
    p.xaxis.minor_tick_line_color = None  # turn off x-axis minor ticks
    p.yaxis.major_tick_line_color = None  # turn off y-axis major ticks
    p.yaxis.minor_tick_line_color = None  # turn off y-axis minor ticks
    p.xaxis.major_label_text_font_size = '0pt'  # turn off x-axis tick labels
    p.yaxis.major_label_text_font_size = '0pt'  # turn off y-axis tick labels
    #Add patch renderer to figure.
    land = p.patches('xs','ys', source = geosource,
              fill_color = {'field' :'2017', 'transform' : color_mapper},
              line_color = 'grey', line_width = 0.25, fill_alpha = 1)

    p.add_tools(HoverTool(renderers=[land],
            tooltips = [ ('Country/region','@country'),
                        ('Population density', '@2017')]))


    EpidemicDate = Slider(title='Epidemic day', start=0, value=len(dates)-1, end=len(dates)-1, step=1, orientation='vertical', direction='rtl')

    # this filter selects rows of data source that satisfy the constraint
    custom_filter = CustomJSFilter(args=dict(slider=EpidemicDate), code="""


        const indices = []
        for (var i = 0; i < source.get_length(); i++) {
            if (source.data['date_index'][i]== slider.value) {
                indices.push(true)
            } else {
                indices.push(false)
            }
        }
        return indices
    """)
    view = CDSView(source=source, filters=[custom_filter])

    # force a re-render when the slider changes
    EpidemicDate.js_on_change('value', CustomJS(args=dict(source=source), code="""
       source.change.emit()
    """))

    sites = p.circle('longitude', 'latitude', source=source, view=view,
                      size={'field':'Metric_size'}, alpha = 0.5, color = 'red')
    p.add_tools(HoverTool(renderers=[sites],
            tooltips = [ ('Country/region','@country'), (metric,'@Metric')]))

    inputs = column(EpidemicDate)
    p.add_layout(color_bar, 'below')
    output_file('../docs/_includes/map_'+metric+'.html')
    save(layout([[inputs,p]]))


###MAIN###
#Get and format data
geosource, ecdc_capital, dates = read_data()
#Make html plot
world_map(geosource, ecdc_capital, dates, 'deaths')
