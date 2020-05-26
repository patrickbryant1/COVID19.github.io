#! /usr/bin/env python3
# -*- coding: utf-8 -*-


import argparse
import sys
import os
import glob
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from scipy.signal import savgol_filter
from scipy.stats import pearsonr
import pdb



#Arguments for argparse module:
parser = argparse.ArgumentParser(description = '''Analyze the lockdown effect in form of mobility drop.''')

parser.add_argument('--epidemic_data', nargs=1, type= str, default=sys.stdin, help = 'Path to eidemic data (csv).')
parser.add_argument('--mobility_data', nargs=1, type= str, default=sys.stdin, help = 'Google mobility data (csv).')
parser.add_argument('--drop_dates', nargs=1, type= str, default=sys.stdin, help = 'Dates to use for drop values in mobility.')
parser.add_argument('--outdir', nargs=1, type= str, default=sys.stdin, help = 'Path to outdir.')

###FUNCTIONS###
def construct_drop(epidemic_data, mobility_data, drop_dates, outdir):
        '''Read in and format all data needed for the drop analysis
        '''

        #Convert epidemic data to datetime
        epidemic_data['dateRep'] = pd.to_datetime(epidemic_data['dateRep'], format='%d/%m/%Y')
        #Rename date to date
        epidemic_data = epidemic_data.rename(columns={'dateRep':'date'})
        #Convert mobility data to datetime
        mobility_data['date'] = pd.to_datetime(mobility_data['date'], format='%Y/%m/%d')
        #Mobility key conversions
        key_conversions = {'United_States_of_America':'United States'}

        #Covariate names
        covariate_names = {'retail_and_recreation_percent_change_from_baseline':'tab:red',
                           'grocery_and_pharmacy_percent_change_from_baseline':'tab:purple',
                           'transit_stations_percent_change_from_baseline':'tab:pink',
                           'workplaces_percent_change_from_baseline':'tab:olive',
                           'residential_percent_change_from_baseline':'tab:cyan'}


        #Save fetched countries, death percentages and mobility data
        fetched_countries = []
        death_percentage = []
        fetched_mobility = {'retail_and_recreation_percent_change_from_baseline':[],
                           'grocery_and_pharmacy_percent_change_from_baseline':[],
                           'transit_stations_percent_change_from_baseline':[],
                           'workplaces_percent_change_from_baseline':[],
                           'residential_percent_change_from_baseline':[]}

        #Save start dates for epidemic data
        start_dates = []
        #Get unique countries
        countries = epidemic_data['countriesAndTerritories'].unique()
        #fig, ax = plt.subplots(figsize=(18/2.54, 12/2.54))

        for country in countries:
            #Get country epidemic data
            country_epidemic_data = epidemic_data[epidemic_data['countriesAndTerritories']==country]
            #Sort on date
            country_epidemic_data = country_epidemic_data.sort_values(by='date')
            #Reset index
            country_epidemic_data = country_epidemic_data.reset_index()

            #Mobility data from Google
            if country in key_conversions.keys():
                mob_key = key_conversions[country]
            else:
                mob_key = ' '.join(country.split('_'))

            country_mobility_data = mobility_data[mobility_data['country_region']==mob_key]
            #Get whole country - no subregion
            country_mobility_data =  country_mobility_data[country_mobility_data['sub_region_1'].isna()]
            if len(country_mobility_data)<2:
                print('No mobility data for', country)
                continue
            #reset index
            country_mobility_data = country_mobility_data.reset_index()
            #calculate % deaths last week of total number of deaths
            country_deaths = np.array(country_epidemic_data['deaths'])
            if max(country_deaths)<10:
                print('Less than 10 deaths per day for', country)
                continue

            #Get biggest drop - decide by plotting
            #drop_dates = identify_drop(country_mobility_data, country, drop_dates, covariate_names, outdir)

            #Get date for after drop and corresponding mobility values
            country_drop_day = drop_dates[drop_dates['Country']==country]['after_drop'].values[0]
            for name in covariate_names:
                #construct a 1-week sliding average
                data = np.array(country_mobility_data[name])
                y = np.zeros(len(country_mobility_data))
                for i in range(7,len(data)):
                    y[i]=np.average(data[i-7:i])

                fetched_mobility[name].append(y[country_drop_day])

            #Get index for first death
            death_start = np.where(country_deaths>0)[0][0]
            percent_dead_last_week = np.zeros(len(country_deaths))
            for i in range(death_start+7,len(country_deaths)): #Loop over all deaths and calculate % for week intervals
                percent_dead_last_week[i] = np.sum(country_deaths[i-7:i])/np.sum(country_deaths[:i])

            death_percentage.append(percent_dead_last_week[-1])
            #Plot
            #plt.plot(np.arange(len(country_deaths)-death_start-7),percent_dead_last_week[death_start+7:], label=country)
            fetched_countries.append(country)
            #Format plot
            # if len(fetched_countries)%10 ==0:
            #     ax.set_yscale('log')
            #     ax.set_xscale('log')
            #     ax.set_xlabel('Days since 1 week after first death')
            #     ax.set_ylabel('% deaths last week')
            #     ax.set_xlim([20,100])
            #     plt.legend()
            #     fig.tight_layout()
            #     fig.savefig(outdir+'countries_'+str(int(len(fetched_countries)/10)),  format='png')
            #     plt.close()
            #     fig, ax = plt.subplots(figsize=(18/2.54, 12/2.54))



        print(len(fetched_countries), 'countries are included in the analysis')
        drop_df = pd.DataFrame() #Save drop values
        drop_df['Country'] = fetched_countries
        drop_df['Death percentage'] = death_percentage
        drop_df['retail'] = fetched_mobility['retail_and_recreation_percent_change_from_baseline']
        drop_df['grocery and pharmacy'] = fetched_mobility['grocery_and_pharmacy_percent_change_from_baseline']
        drop_df['transit'] = fetched_mobility['transit_stations_percent_change_from_baseline']
        drop_df['work'] = fetched_mobility['workplaces_percent_change_from_baseline']
        drop_df['residential'] = fetched_mobility['residential_percent_change_from_baseline']
        pdb.set_trace()
        drop_df.to_csv('drop_df.csv')

        #plot relationships
        plot_death_vs_drop(drop_df, outdir)

        return None
def identify_drop(country_mobility_data, country, drop_dates, covariate_names, outdir):
    '''Identify the mobility drop
    '''

    country_drop_index = drop_dates[drop_dates['Country']==country].index[0]
    drop_day = int(drop_dates.loc[country_drop_index, 'after_drop']) #day for drop effect
    drop_date = country_mobility_data.loc[drop_day, 'date'] #date for drop effect
    drop_dates.loc[country_drop_index,'date'] = drop_date

    fig, ax = plt.subplots(figsize=(6/2.54, 6/2.54))
    for name in covariate_names:
        #construct a 1-week sliding average
        data = np.array(country_mobility_data[name])
        y = np.zeros(len(country_mobility_data)-7)
        for i in range(7,len(data)):
            y[i-7]=np.average(data[i-7:i])

        plt.plot(np.arange(7,len(country_mobility_data)), y, color = covariate_names[name])
        plt.axvline(drop_day)
        plt.text(drop_day,0,np.array(drop_date,  dtype='datetime64[D]'))

    ax.set_xlabel('Days since first death')
    ax.set_ylabel('Mobility change')
    ax.set_title(country)
    fig.tight_layout()
    fig.savefig(outdir+'identify_drop/'+country+'_slide7.png',  format='png')
    plt.close()

    return drop_dates

def plot_death_vs_drop(drop_df, outdir):
    '''Plot relationship btw death percentage today and mobility drop at lockdown
    '''
    covariates = {'retail':'tab:red',
                    'grocery and pharmacy':'tab:purple',
                    'transit':'tab:pink',
                    'work':'tab:olive',
                    'residential':'tab:cyan'}

    for key in covariates:
        fig, ax = plt.subplots(figsize=(9/2.54, 9/2.54))
        ax.scatter(drop_df[key], drop_df['Death percentage'], color = covariates[key])
        ax.set_xlabel('Mobility change in drop')
        ax.set_ylabel('Death percentage 21 May')
        ax.set_yscale('log')
        ax.set_title(key)
        fig.tight_layout()
        fig.savefig(outdir+key+'.png',  format='png')
        plt.close()
#####MAIN#####
#Set font size
matplotlib.rcParams.update({'font.size': 9})
args = parser.parse_args()
epidemic_data = pd.read_csv(args.epidemic_data[0])
mobility_data = pd.read_csv(args.mobility_data[0])
drop_dates = pd.read_csv(args.drop_dates[0])
outdir = args.outdir[0]
construct_drop(epidemic_data, mobility_data, drop_dates, outdir)
