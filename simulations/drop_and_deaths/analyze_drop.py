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
parser.add_argument('--outdir', nargs=1, type= str, default=sys.stdin, help = 'Path to outdir.')

###FUNCTIONS###
def construct_drop(epidemic_data, mobility_data, outdir):
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
        covariate_names = ['retail_and_recreation_percent_change_from_baseline',
                           'grocery_and_pharmacy_percent_change_from_baseline',
                           'transit_stations_percent_change_from_baseline',
                           'workplaces_percent_change_from_baseline',
                           'residential_percent_change_from_baseline']

        #Save fetched countries for montage script
        fetched_countries = []
        #Save start dates for epidemic data
        start_dates = []
        #Get unique countries
        countries = epidemic_data['countriesAndTerritories'].unique()
        fig, ax = plt.subplots(figsize=(18/2.54, 12/2.54))
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
            #calculate % deaths last week of total number of deaths
            country_deaths = np.array(country_epidemic_data['deaths'])
            if max(country_deaths)<10:
                print('Less than 10 deaths per day for', country)
                continue
            #Get index for first death
            death_start = np.where(country_deaths>0)[0][0]
            percent_dead_last_week = np.zeros(len(country_deaths))
            for i in range(death_start+7,len(country_deaths)): #Loop over all deaths and calculate % for week intervals
                percent_dead_last_week[i] = np.sum(country_deaths[i-7:i])/np.sum(country_deaths[:i])
            #Plot
            plt.plot(np.arange(len(country_deaths)-death_start-7),percent_dead_last_week[death_start+7:])
            fetched_countries.append(country)

        #Format plot
        ax.set_yscale('log')
        ax.set_xscale('log')
        ax.set_xlabel('Days since 1 week after first death')
        ax.set_ylabel('% deaths last week')
        ax.set_xlim([20,100])
        fig.tight_layout()
        plt.show()
        pdb.set_trace()

        print(len(fetched_countries), 'countries are included in the analysis')
            # #Merge
            # #Merge to the shortest one
            # if len(country_signal_data)>len(country_mobility_data):
            #     country_signal_data = country_mobility_data.merge(country_signal_data, left_on = 'date', right_on ='date', how = 'left')
            # else:
            #     country_signal_data = country_signal_data.merge(country_mobility_data, left_on = 'date', right_on ='date', how = 'left')
            #
            # #Make an array
            # signal_array = np.zeros((6,len(country_signal_data)))
            # signal_array[0,:]=country_signal_data['Median(R)']
            # signal_array[1,:]=country_signal_data['retail_and_recreation_percent_change_from_baseline']
            # signal_array[2,:]=country_signal_data['grocery_and_pharmacy_percent_change_from_baseline']
            # signal_array[3,:]=country_signal_data['transit_stations_percent_change_from_baseline']
            # signal_array[4,:]=country_signal_data['workplaces_percent_change_from_baseline']
            # signal_array[5,:]=country_signal_data['residential_percent_change_from_baseline']


def plot_all_countries():
    '''Plot all countries in overlay per mobility category
    '''

    keys = ['retail and recreation', 'grocery and pharmacy',
            'transit stations','workplaces','residential']
    colors = ['Reds','Purples','Oranges','Greens','Blues']


    #Mobility delay
    for i in range(5):
        all_countries_x = []
        all_countries_y = []
        plotted_countries = 0
        fig, ax = plt.subplots(figsize=(9/2.54, 9/2.54))

        ax.set_title(keys[i])
        ax.set_xlabel('mobility time delay (days)')
        ax.set_ylabel(ylabel)
        ax.set_xlim([-days_to_include-2, days_to_include+2])
        fig.tight_layout()
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        fig.savefig(outdir+'all/'+keys[i]+outname,  format='png')
        plt.close()
        print('Plotting',plotted_countries, 'countries')

#####MAIN#####
#Set font size
matplotlib.rcParams.update({'font.size': 9})
args = parser.parse_args()
epidemic_data = pd.read_csv(args.epidemic_data[0])
mobility_data = pd.read_csv(args.mobility_data[0])
outdir = args.outdir[0]
construct_drop(epidemic_data, mobility_data, outdir)
