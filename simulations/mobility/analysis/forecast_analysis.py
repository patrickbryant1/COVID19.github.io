#! /usr/bin/env python3
# -*- coding: utf-8 -*-


import argparse
import sys
import os
import glob
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from scipy.stats import gamma
import numpy as np
import seaborn as sns
import pystan

import pdb



#Arguments for argparse module:
parser = argparse.ArgumentParser(description = '''Obtain forecast in terms of the mean number of deaths and write to csv.''')

parser.add_argument('--datadir', nargs=1, type= str, default=sys.stdin, help = 'Path to outdir.')
parser.add_argument('--countries', nargs=1, type= str, default=sys.stdin, help = 'Countries to model (csv).')
parser.add_argument('--days_to_simulate', nargs=1, type= int, default=sys.stdin, help = 'Number of days to simulate.')
parser.add_argument('--end_date', nargs=1, type= str, default=sys.stdin, help = 'End date of data used to fit model.')
parser.add_argument('--outdir', nargs=1, type= str, default=sys.stdin, help = 'Path to outdir.')

def read_and_format_data(datadir, countries, days_to_simulate, end_date):
        '''Read in and format all data needed for the model
        '''

        #Get epidemic data
        epidemic_data = pd.read_csv(datadir+'ecdc_20200412.csv')
        #Convert to datetime
        epidemic_data['dateRep'] = pd.to_datetime(epidemic_data['dateRep'], format='%d/%m/%Y')
        #Select all data up to end_date
        epidemic_data = epidemic_data[epidemic_data['dateRep']<=end_date]
        ## get CFR
        cfr_by_country = pd.read_csv(datadir+"weighted_fatality.csv")
        #SI
        serial_interval = pd.read_csv(datadir+"serial_interval.csv")

        days_to_simulate = days_to_simulate
        #Model data - to be used for plotting
        stan_data = {'dates_by_country':np.zeros((days_to_simulate,len(countries)), dtype='datetime64[D]'),
                    'deaths_by_country':np.zeros((days_to_simulate,len(countries))),
                    'cases_by_country':np.zeros((days_to_simulate,len(countries))),
                    'days_by_country':np.zeros(len(countries)),
                    }


        #Get data by country
        for c in range(len(countries)):
                country = countries[c]

                #Get country epidemic data
                country_epidemic_data = epidemic_data[epidemic_data['countriesAndTerritories']==country]
                #Sort on date
                country_epidemic_data = country_epidemic_data.sort_values(by='dateRep')
                #Reset index
                country_epidemic_data = country_epidemic_data.reset_index()

                #Get all dates with at least 10 deaths
                cum_deaths = country_epidemic_data['deaths'].cumsum()
                death_index = cum_deaths[cum_deaths>=10].index[0]
                di30 = death_index-30
                #Get part of country_epidemic_data 30 days before day with at least 10 deaths
                country_epidemic_data = country_epidemic_data.loc[di30:]
                #Reset index
                country_epidemic_data = country_epidemic_data.reset_index()

                print(country, len(country_epidemic_data))
                #Check that foreacast is really a forecast
                N = len(country_epidemic_data)
                stan_data['days_by_country'][c]=N
                forecast = days_to_simulate - N
                if forecast <0: #If the number of predicted days are less than the number available
                    days_to_simulate = N
                    forecast = 0
                    print('Forecast error!')
                    pdb.set_trace()

                #Save dates
                stan_data['dates_by_country'][:N,c] = np.array(country_epidemic_data['dateRep'], dtype='datetime64[D]')
                #Save deaths
                stan_data['deaths_by_country'][:N,c] = country_epidemic_data['deaths']
                #Save cases
                stan_data['cases_by_country'][:N,c] = country_epidemic_data['cases']


        return stan_data

def evaluate_forecast(outdir, countries, stan_data, days_to_simulate):
    '''Evaluate forecast results per country in terms of the predicted (mean) vs the true number of deaths.
    '''

    #Read in data
    summary = pd.read_csv(outdir+'summary.csv')
    days = np.arange(0,days_to_simulate) #Days to simulate
    #Plot rhat
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.hist(summary['Rhat'])
    ax.set_ylabel('Count')
    ax.set_xlabel("Rhat")
    fig.savefig(outdir+'plots/rhat.png', format='png')
    plt.close()

    #Evaluate per country
    result_df = pd.DataFrame()
    forecast_countries = [] #Save country per forecast
    death_week_forecast = [] #Save forecast deaths
    death_week_observed = [] #Save observed deaths
    forecast_dates = [] #Save forecast dates
    for i in range(1,len(countries)+1):
        country= countries[i-1]
        #Get stan data for country i
        dates = stan_data['dates_by_country'][:,i-1]
        observed_country_deaths = stan_data['deaths_by_country'][:,i-1]
        end = int(stan_data['days_by_country'][i-1])#End of data for country i
        #Extract modeled deaths
        means = {'E_deaths':[]}
        lower_bound = {'E_deaths':[]} #Estimated 2.5 %
        higher_bound = {'E_deaths':[]} #Estimated 97.5 % - together 95 % CI
        lower_bound25 = {'E_deaths':[]} #Estimated 25%
        higher_bound75 = {'E_deaths':[]} #Estimated 55 % - together 75 % CI
        #Get means and 95 % CI for cases (prediction), deaths and Rt for all time steps
        var='E_deaths'
        for j in range(1,days_to_simulate+1):
            var_ij = summary[summary['Unnamed: 0']==var+'['+str(j)+','+str(i)+']']
            means[var].append(var_ij['mean'].values[0])
            lower_bound[var].append(var_ij['2.5%'].values[0])
            higher_bound[var].append(var_ij['97.5%'].values[0])
            lower_bound25[var].append(var_ij['25%'].values[0])
            higher_bound75[var].append(var_ij['75%'].values[0])

        #Compare Deaths
        forecast_countries.extend([country]*7)
        death_week_forecast.extend(means['E_deaths'][end-7:end])
        death_week_observed.extend(observed_country_deaths[end-7:end])
        forecast_dates.extend(dates[end-7:end])

    #Save predicted(forecast) and observed deaths 
    result_df['Country'] = forecast_countries
    result_df['Date'] = forecast_dates
    result_df['Predicted deaths'] = death_week_forecast
    result_df['Observed_deaths'] = death_week_observed
    result_df.to_csv(outdir+'forecast.csv')
    return None


#####MAIN#####
args = parser.parse_args()
datadir = args.datadir[0]
countries = args.countries[0].split(',')
days_to_simulate=args.days_to_simulate[0] #Number of days to model. Increase for further forecast
end_date = np.datetime64(args.end_date[0])+7 #Increase to one week ahead for obtaining forecast data
outdir = args.outdir[0]
#Read data
stan_data = read_and_format_data(datadir, countries, days_to_simulate, end_date)
#Visualize
evaluate_forecast(outdir, countries, stan_data, days_to_simulate)
