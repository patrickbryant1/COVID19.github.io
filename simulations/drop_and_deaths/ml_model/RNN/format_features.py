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
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import KFold
import pdb



#Arguments for argparse module:
parser = argparse.ArgumentParser(description = '''Format data.
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


            country_deaths = np.array(country_epidemic_data['deaths'])
            #Ensure no negative corrections are present. Set these to the values of the previous date
            for i in range(len(country_deaths)):
                if country_deaths[i]<0:
                    country_deaths[i] = country_deaths[i-1]


            country_cases = np.array(country_epidemic_data['cases'])
            #Ensure no negative corrections are present. Set these to the values of the previous date
            for i in range(len(country_cases)):
                if country_cases[i]<0:
                    country_cases[i] = country_cases[i-1]

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

            #Smooth cases
            sm_cases = np.zeros(len(country_epidemic_data))
            for i in range(7,len(country_epidemic_data)+1):
                sm_cases[i-1]=np.average(country_cases[i-7:i])
            sm_cases[0:6] = sm_cases[6]
            country_epidemic_data['smoothed_cases']=sm_cases

            #Get population in millions
            country_pop = country_epidemic_data['popData2018'].values[0]/1000000
            #Calculate deaths per million and add to df
            country_epidemic_data['death_per_million'] =sm_deaths/country_pop

            #Construct a 1-week sliding average to smooth the mobility data
            for mob_key in mobility_keys:
                data = np.array(country_mobility_data[mob_key])
                y = np.zeros(len(country_mobility_data))
                for i in range(7,len(data)+1):
                    #Check that there are no NaNs
                    if np.isnan(data[i-7:i]).any():
                        #If there are NaNs, loop through and replace with value from prev date
                        for i_nan in range(i-7,i):
                            if np.isnan(data[i_nan]):
                                data[i_nan]=data[i_nan-1]
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

        return extracted_data

def construct_features(extracted_data,ip,pl):
    '''Construct features for ml model
    '''

    countries = extracted_data['countriesAndTerritories'].unique()
    num_countries = len(countries)
    all_index = np.arange(num_countries)
    #dpm_history = [] #Deaths per million 4 weeks before
    fetched_mobility = ['retail_and_recreation_percent_change_from_baseline',
                       'grocery_and_pharmacy_percent_change_from_baseline',
                       'transit_stations_percent_change_from_baseline',
                       'workplaces_percent_change_from_baseline',
                       'residential_percent_change_from_baseline']
    X = [] #Input features
    y = [] #Labels

    csi = [0] #Country split index in data for train
    fetched_countries = [] #The fetched countries
    train_countries = []
    valid_countries = []
    include_period = ip #How many days to include data
    predict_lag = pl #How many days ahead to predict
    for c in all_index:
        country = countries[c]
        country_data = extracted_data[extracted_data['countriesAndTerritories']==country]
        #Reset index
        country_data = country_data.reset_index()
        country_points=0 #Number of data points for country
        if (len(country_data)-predict_lag-include_period)<1:
            print('Not enough data for', country)
            continue
        #Go through all days
        for i in range(len(country_data)-predict_lag-include_period+1):
            found_nan =False
            country_points+=1 #Increase points
            x = []
            cum_measures = [] #Cumulative data - to capture the full history
            #Include data for the include period
            #Deaths and cases
            x.extend(np.array(country_data.loc[:i+include_period-1, 'death_per_million']))
            cum_measures.append(np.sum(country_data.loc[:i+include_period-1, 'death_per_million']))
            x.extend(np.array(country_data.loc[:i+include_period-1, 'death_per_million']))
            cum_measures.append(np.sum(country_data.loc[:i+include_period-1, 'death_per_million']))
            for key in fetched_mobility:
                curr_mob = np.array(country_data.loc[:i+include_period-1, key])
                if np.isnan(curr_mob).any():
                    found_nan = True
                    break

                x.extend(np.array(country_data.loc[:i+include_period-1, key]))
                cum_measures.append(np.sum(country_data.loc[:i+include_period-1, key]))

            #Check that all data could be computed
            if found_nan ==True:
                print(country, ' contains NaNs')
                continue

                #x.extend(cum_measures)
            #Add the number of epidemic days
            #x.append(i+include_period)
            #Include data for the predict lag
            dpm_change = np.array(country_data.loc[i+include_period:i+include_period+predict_lag-1, 'death_per_million'])
            #Append to data
            X.append(np.array(x))
            y.append(dpm_change)


        #Save country points and fetched countries
        csi.append(country_points)
        fetched_countries.append(country)
    print(len(y), 'data points')
    return np.array(X), np.array(y), np.array(csi), np.array(fetched_countries)


#####MAIN#####
#Set random seed to ensure same random split every time
np.random.seed(seed=0)
#Set font size
args = parser.parse_args()
epidemic_data = pd.read_csv(args.epidemic_data[0])
mobility_data = pd.read_csv(args.mobility_data[0])
outdir = args.outdir[0]
#Extract data and smooth
extract = False
if extract == True:
    extracted_data= format_data(epidemic_data, mobility_data, outdir)
else:
    extracted_data = pd.read_csv('extracted_data.csv')
#Use only Europe
extracted_data=extracted_data[extracted_data['continentExp']=='Europe']
#Construct features
ip=21 #include period, the minimum period to include data
pl=21 #predict lag
X, y, csi, fetched_countries = construct_features(extracted_data,ip,pl)

np.save('X.npy',X)
np.save('y.npy',y)
np.save('csi.npy',csi)
np.save('fetched_countries.npy',fetched_countries)
