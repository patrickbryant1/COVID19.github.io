#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import folium
import pandas as pd
import numpy as np
import geopandas as gpd
import geoplot
import mapclassify
import matplotlib.pyplot as plt
import matplotlib

import pdb

########MAIN#########
#ecdc data
ecdc_df = pd.read_csv('ecdc_20200828.csv')
ecdc_df['date'] = pd.to_datetime(ecdc_df['dateRep'], format='%d/%m/%Y')
ecdc_df = ecdc_df.sort_values(by=['date'], ascending=False)
ecdc_df = ecdc_df.drop(columns=['date'])
ecdc_df['deaths_per_100000'] = 100000*ecdc_df['deaths']/ecdc_df['popData2019']


#Read shapefile using Geopandas
shapefile = './countries_110m/ne_110m_admin_0_countries.shp'
#Rename columns.
gdf = gpd.read_file(shapefile)[['ADMIN', 'ADM0_A3', 'geometry']]
gdf.columns = ['country', 'country_code', 'geometry']
#Drop Antarctica
gdf = gdf.drop(gdf.index[159])

#Input GeoJSON source that contains features for plotting.
dates = ecdc_df['dateRep'].unique()

def plot_colorbar():
    '''Plots a stand alone colorbar
    '''
    fig,ax = plt.subplots(figsize=(10,10))

    cb = matplotlib.colorbar.ColorbarBase(ax, orientation='horizontal',cmap=matplotlib.cm.Reds)
    fig.tight_layout()
    plt.show()

#Colorbar
#plot_colorbar()
vmin = 0
vmax = 1
names = []
for i in range(0,len(dates),7):
    date = dates[i]
    ecdc_date = ecdc_df[ecdc_df['dateRep']==date]
    world = pd.merge(gdf, ecdc_date, left_on='country_code', right_on='countryterritoryCode', how='right')
    fig,ax = plt.subplots()
    world.plot(ax=ax,column='deaths_per_100000', cmap='Reds',legend=True, vmin=vmin, vmax=vmax,legend_kwds={'orientation':'horizontal'})
    ax.axis('off')

    ax.set_title(date)
    fig.tight_layout()
    date = date.split('/')
    outname='./deaths/world'+date[0]+'_'+date[1]+'_'+date[2]+'_deaths.png'
    fig.savefig(outname, format='png', dpi=300)
    plt.close()
    names.append('world'+date[0]+'_'+date[1]+'_'+date[2]+'_deaths.png')

for i in range(len(names)-1,-1,-1):
    print(names[i]+',')
