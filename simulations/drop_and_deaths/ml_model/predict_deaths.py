#! /usr/bin/env python3
# -*- coding: utf-8 -*-


import argparse
import sys
import os
import glob
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
import seaborn as sns
from scipy.stats import pearsonr
from sklearn.ensemble import RandomForestRegressor
import pdb



#Arguments for argparse module:
parser = argparse.ArgumentParser(description = '''Predic the number of deaths ahead of time using a RF regressor.
                                                A nonlinear model is necessary due to the irregularity of the
                                                mobility effect. Historical data is used to take the previous
                                                epidemic development into account, which is not possible with
                                                e.g. MCMC simulations. ''')
parser.add_argument('--epidemic_data', nargs=1, type= str, default=sys.stdin, help = 'Path to eidemic data (csv).')
parser.add_argument('--mobility_data', nargs=1, type= str, default=sys.stdin, help = 'Google mobility data (csv).')
parser.add_argument('--outdir', nargs=1, type= str, default=sys.stdin, help = 'Path to outdir.')

###FUNCTIONS###
def format_data(epidemic_data, mobility_data, outdir):
        '''Read in and format all data needed for the analysis
        '''

        #Convert epidemic data to datetime
        epidemic_data['dateRep'] = pd.to_datetime(epidemic_data['dateRep'], format='%d/%m/%Y')
        #Rename date to date
        epidemic_data = epidemic_data.rename(columns={'dateRep':'date'})
        #Convert mobility data to datetime
        mobility_data['date'] = pd.to_datetime(mobility_data['date'], format='%Y/%m/%d')
        #Mobility key conversions
        key_conversions = {'United_States_of_America':'United States'}

        mobility_keys = {'retail_and_recreation_percent_change_from_baseline':[],
                           'grocery_and_pharmacy_percent_change_from_baseline':[],
                           'transit_stations_percent_change_from_baseline':[],
                           'workplaces_percent_change_from_baseline':[],
                           'residential_percent_change_from_baseline':[]}

        #Save fetched countries, death per million historically and for the predictions and mobility data
        extracted_data = pd.DataFrame()
        #Get unique countries
        countries = epidemic_data['countriesAndTerritories'].unique()
        for country in countries:
            #Get country epidemic data
            country_epidemic_data = epidemic_data[epidemic_data['countriesAndTerritories']==country]
            #Sort on date
            country_epidemic_data = country_epidemic_data.sort_values(by='date')
            #Reset index
            country_epidemic_data = country_epidemic_data.reset_index()

            #Check that at least 10 deaths per day has been reached
            country_deaths = np.array(country_epidemic_data['deaths'])
            death_sum=np.sum(country_deaths)
            if death_sum < 100:
                print('Less than 100 deaths for', country)
                continue




            #Mobility data from Google
            if country in key_conversions.keys():
                mob_key = key_conversions[country]
            else:
                mob_key = ' '.join(country.split('_'))

            country_mobility_data = mobility_data[mobility_data['country_region']==mob_key]
            #Get whole country - no subregion
            country_mobility_data = country_mobility_data[country_mobility_data['sub_region_1'].isna()]
            if len(country_mobility_data)<2:
                print('No mobility data for', country)
                continue
            #reset index
            country_mobility_data = country_mobility_data.reset_index()
            #Get start and end dates
            mobility_start = country_mobility_data['date'][0]
            mobility_end = max(country_mobility_data['date'])

            #Smooth deaths
            sm_deaths = np.zeros(len(country_epidemic_data))
            for i in range(7,len(country_epidemic_data)+1):
                sm_deaths[i-1]=np.average(country_deaths[i-7:i])
            sm_deaths[0:6] = sm_deaths[6]
            country_epidemic_data['smoothed_deaths']=sm_deaths
            #Get population in millions
            country_pop = country_epidemic_data['popData2018'].values[0]/1000000
            #Calculate deaths per million and add to df
            country_epidemic_data['death_per_million'] =sm_deaths/country_pop

            #Construct a 1-week sliding average to smooth the mobility data
            for mob_key in mobility_keys:
                data = np.array(country_mobility_data[mob_key])
                y = np.zeros(len(country_mobility_data))
                for i in range(7,len(data)+1):
                    y[i-1]=np.average(data[i-7:i])
                y[0:6] = y[6]
                country_mobility_data[mob_key]=y
            #Merge epidemic data with mobility data
            country_epidemic_data = country_epidemic_data.merge(country_mobility_data, left_on = 'date', right_on ='date', how = 'left')

            #Get all data after the mobility start
            country_epidemic_data = country_epidemic_data[country_epidemic_data['date']>=mobility_start]

            #Save data
            extracted_data = pd.concat([extracted_data, country_epidemic_data])

        extracted_data.to_csv('extracted_data.csv')
        print('Number of fetched countries:',len(extracted_data['countriesAndTerritories'].unique()))

        return None

def construct_features(extracted_data):
    '''Construct features for ml model
    '''

    fetched_countries = extracted_data['countriesAndTerritories'].unique()
    #dpm_history = [] #Deaths per million 4 weeks before
    dpm_pred = [] #Deaths per million 4 weeks after today and on
    fetched_mobility = ['retail_and_recreation_percent_change_from_baseline',
                       'grocery_and_pharmacy_percent_change_from_baseline',
                       'transit_stations_percent_change_from_baseline',
                       'workplaces_percent_change_from_baseline',
                       'residential_percent_change_from_baseline']
    X = [] #Input features
    include_period = 28 #How many days to include data
    predict_lag = 28 #How many days ahead to predict
    for country in fetched_countries:
        country_data = extracted_data[extracted_data['countriesAndTerritories']==country]
        #Reset index
        country_data = country_data.reset_index()
        for i in range(len(country_data)-predict_lag-include_period):
            x = []
            #Include data for the include period
            x.extend(np.array(country_data.loc[i:i+include_period-1, 'death_per_million']))
            for key in fetched_mobility:
                curr_mob = np.array(country_data.loc[i:i+include_period-1, key])

                x.extend(np.array(country_data.loc[i:i+include_period-1, key]))
            X.append(np.array(x))
            #Include data for the predict lag
            dpm_pred.append(country_data.loc[i+include_period+predict_lag-1, 'death_per_million'])

    return np.array(X), np.array(dpm_pred)

def train(X,y):
    '''Fit rf regressor
    '''

    regr = RandomForestRegressor(random_state=0)
    pdb.set_trace()
    regr.fit(X, y)
    pdb.set_trace()

#####MAIN#####
#Set font size
matplotlib.rcParams.update({'font.size': 9})
args = parser.parse_args()
epidemic_data = pd.read_csv(args.epidemic_data[0])
mobility_data = pd.read_csv(args.mobility_data[0])
outdir = args.outdir[0]
try:
    extracted_data = pd.read_csv('extracted_data.csv')
except:
    extracted_data= format_data(epidemic_data, mobility_data, outdir)
X,y = construct_features(extracted_data)
pdb.set_trace()
train(X,y)
