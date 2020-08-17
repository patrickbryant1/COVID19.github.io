#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import folium
import pandas as pd
import numpy as np
import geopandas as gpd
import geoplot
import mapclassify
import matplotlib.pyplot as plt

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




for date in dates:
    ecdc_date = ecdc_df[ecdc_df['dateRep']==date]
    world = pd.merge(gdf, ecdc_date, left_on='country_code', right_on='countryterritoryCode', how='right')
    world.plot(column='deaths', cmap='Reds')

    date = date.split('/')
    plt.savefig('./deaths/world'+date[0]+'_'+date[1]+'_'+date[2]+'_deaths.png', format='png', dpi=300)
    plt.close()
