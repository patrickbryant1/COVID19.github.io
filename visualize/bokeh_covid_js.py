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
import pdb


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
    dates = ecdc_capital['dateRep'].unique()
    ecdc_capital['date_index'] = 0
    for i in range(len(dates)):
        index = ecdc_capital[ecdc_capital['dateRep']==dates[i]].index
        ecdc_capital.loc[index,'date_index']=i+1
    #Create a geodf
    ecdc_capital = gpd.GeoDataFrame(ecdc_capital,
                                 geometry = ecdc_capital.geometry)
    # Get x and y coordinates
    ecdc_capital['x'] = [geometry.x for geometry in ecdc_capital['geometry']]
    ecdc_capital['y'] = [geometry.y for geometry in ecdc_capital['geometry']]
    ecdc_capital = ecdc_capital.drop('geometry', axis = 1).copy()
    ecdc_capital['death_size'] = ecdc_capital['deaths']/10


    return geosource, ecdc_capital

def world_map(geosource, ecdc_capital):
    '''Create world map and write to html with javascript
    '''
    data = dict(longitude=np.array(ecdc_capital['x']),
            latitude=np.array(ecdc_capital['y']),
            date_index=np.array(ecdc_capital['date_index']),
            Deaths=np.array(ecdc_capital['deaths']),
            Death_size=np.array(ecdc_capital['death_size']))
    source = ColumnDataSource(data=data)

    EpidemicDate = Slider(start=0, value=0, end=128, step=1)

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

    #Define a sequential multi-hue color palette.
    palette = brewer['YlGnBu'][9]
    #Reverse color order so that dark blue is highest.
    palette = palette[::-1]
    #Instantiate LinearColorMapper that linearly maps numbers in a range, into a sequence of colors. Input nan_color.
    color_mapper = LinearColorMapper(palette = palette, low = 0, high = 500, nan_color = '#d9d9d9')

    #Create color bar.
    color_bar = ColorBar(color_mapper=color_mapper, label_standoff=8,
                         width = 500, height = 20,
                         border_line_color=None,location = (0,0),
                         orientation = 'horizontal')
    p = figure(title = 'Deaths per day', plot_height = 400 , plot_width = 600,
               toolbar_location = 'below',
               tools = "pan, wheel_zoom, box_zoom, reset")
    p.xgrid.grid_line_color = None
    p.ygrid.grid_line_color = None#Add patch renderer to figure.
    land = p.patches('xs','ys', source = geosource,
              fill_color = {'field' :'2017', 'transform' : color_mapper},
              line_color = 'black', line_width = 0.25, fill_alpha = 1)

    p.add_tools(HoverTool(renderers=[land],
            tooltips = [ ('Country/region','@country'),
                        ('Population density', '@2017')]))

    sites = p.circle('longitude', 'latitude', source=source, view=view,
                      size={'field':'Death_size'}, alpha = 0.5, color = 'red')
    p.add_tools(HoverTool(renderers=[sites],
            tooltips = [ ('Deaths','@Deaths')]))

    inputs = column(EpidemicDate, width=200)

    output_file('../docs/_includes/map.html')
    save(layout([[inputs,p]]))
###MAIN###
#Get and format data
geosource, ecdc_capital = read_data()
#Make html plot
world_map(geosource, ecdc_capital)
