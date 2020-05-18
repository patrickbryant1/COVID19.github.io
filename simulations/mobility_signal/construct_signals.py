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
import pdb



#Arguments for argparse module:
parser = argparse.ArgumentParser(description = '''Generate signals for mobility data and R estimates, then correlate time delay.''')

parser.add_argument('--R_estimates', nargs=1, type= str, default=sys.stdin, help = 'Path to dir with R estimates per country.')
parser.add_argument('--epidemic_data', nargs=1, type= str, default=sys.stdin, help = 'Path to eidemic data (csv).')
parser.add_argument('--mobility_data', nargs=1, type= str, default=sys.stdin, help = 'Google mobility data (csv).')
parser.add_argument('--outdir', nargs=1, type= str, default=sys.stdin, help = 'Path to outdir.')

###FUNCTIONS###
def construct_signals(R_estimates, epidemic_data, mobility_data, outdir):
        '''Read in and format all data needed for the signal correlation analysis
        '''

        #Convert epidemic data to datetime
        epidemic_data['dateRep'] = pd.to_datetime(epidemic_data['dateRep'], format='%d/%m/%Y')
        #Convert mobility data to datetime
        mobility_data['date'] = pd.to_datetime(mobility_data['date'], format='%Y/%m/%d')


        #Covariate names
        covariate_names = ['retail_and_recreation_percent_change_from_baseline',
                           'grocery_and_pharmacy_percent_change_from_baseline',
                           'transit_stations_percent_change_from_baseline',
                           'workplaces_percent_change_from_baseline',
                           'residential_percent_change_from_baseline']
        #Get unique countries
        #countries = epidemic_data['countriesAndTerritories'].unique()
        countries = ['Italy']
        for country in countries:
            country_R = pd.read_csv(R_estimates+country+'_R_estimate.csv')
            #Fix datetime
            country_R['date'] = pd.to_datetime(country_R['date'], format='%d/%m/%Y')
            #Get country epidemic data
            country_epidemic_data = epidemic_data[epidemic_data['countriesAndTerritories']==country]
            #Sort on date
            country_epidemic_data = country_epidemic_data.sort_values(by='dateRep')
            #Reset index
            country_epidemic_data = country_epidemic_data.reset_index()
            #Get data for day >= t_c, where t_c is the day where 80 % of the max death count has been reached
            death_80 = max(country_epidemic_data['deaths'])*0.8
            signal_start = min(country_epidemic_data[country_epidemic_data['deaths']>=death_80].index)
            country_epidemic_data = country_epidemic_data.loc[signal_start:]
            #Merge dfs
            country_signal_data = country_epidemic_data.merge(country_R, left_on = 'dateRep', right_on ='date', how = 'left')

            #Mobility data from Google
            country_mobility_data = mobility_data[mobility_data['country_region']==country]
            #Get whole country - no subregion
            country_mobility_data =  country_mobility_data[country_mobility_data['sub_region_1'].isna()]
            #Merge
            country_signal_data = country_signal_data.merge(country_mobility_data, left_on = 'dateRep', right_on ='date', how = 'left')

            #Construct signals
            country_signal_data['R_signal'] = 0
            country_signal_data['retail_signal'] = 0
            country_signal_data['grocery_signal'] = 0
            country_signal_data['transit_signal'] = 0
            country_signal_data['workplaces_signal'] = 0
            country_signal_data['residential_signal'] = 0
            #Look at the smoothing
            #compare_smoothing(country_signal_data, outdir)
            #Smooth
            country_signal_data['Median(R)'] = savgol_filter(country_signal_data['Median(R)'], 5,3)
            country_signal_data['retail_and_recreation_percent_change_from_baseline'] = savgol_filter(country_signal_data['retail_and_recreation_percent_change_from_baseline'], 7,3)
            country_signal_data['grocery_and_pharmacy_percent_change_from_baseline'] = savgol_filter(country_signal_data['grocery_and_pharmacy_percent_change_from_baseline'], 7,3)
            country_signal_data['transit_stations_percent_change_from_baseline'] = savgol_filter(country_signal_data['transit_stations_percent_change_from_baseline'], 7,3)
            country_signal_data['workplaces_percent_change_from_baseline'] = savgol_filter(country_signal_data['workplaces_percent_change_from_baseline'], 7,3)
            country_signal_data['residential_percent_change_from_baseline'] = savgol_filter(country_signal_data['residential_percent_change_from_baseline'], 7,3)

            for i in range(len(country_signal_data)-1): #loop through data to construct signal
                row_i = country_signal_data.loc[i]
                row_i_1 = country_signal_data.loc[i+1]
                country_signal_data.loc[i+1,'R_signal']=row_i_1['Median(R)']-row_i['Median(R)']
                country_signal_data.loc[i+1,'retail_signal']=row_i_1['retail_and_recreation_percent_change_from_baseline']-row_i['retail_and_recreation_percent_change_from_baseline']
                country_signal_data.loc[i+1,'grocery_signal']=row_i_1['grocery_and_pharmacy_percent_change_from_baseline']-row_i['grocery_and_pharmacy_percent_change_from_baseline']
                country_signal_data.loc[i+1,'transit_signal']=row_i_1['transit_stations_percent_change_from_baseline']-row_i['transit_stations_percent_change_from_baseline']
                country_signal_data.loc[i+1,'workplaces_signal']=row_i_1['workplaces_percent_change_from_baseline']-row_i['workplaces_percent_change_from_baseline']
                country_signal_data.loc[i+1,'residential_signal']=row_i_1['residential_percent_change_from_baseline']-row_i['residential_percent_change_from_baseline']

            pdb.set_trace()
def compare_smoothing(country_signal_data, outdir):
    '''Compare different kinds of smoothing
    '''
    keys = ['Median(R)', 'retail_and_recreation_percent_change_from_baseline',
    'grocery_and_pharmacy_percent_change_from_baseline',
    'transit_stations_percent_change_from_baseline',
    'workplaces_percent_change_from_baseline',
    'residential_percent_change_from_baseline']

    for key in keys:
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.plot(range(len(country_signal_data)),country_signal_data[key], label='No smoothing')
        #savgol
        savgol_smoothing = savgol_filter(country_signal_data[key], 7,3)
        ax.plot(range(len(country_signal_data)),savgol_smoothing, label='Savgol smoothing')
        ax.set_title(key)
        plt.legend()
        fig.savefig(outdir+key+'.png',  format='png', dpi=300)


#####MAIN#####
args = parser.parse_args()
R_estimates = args.R_estimates[0]
epidemic_data = pd.read_csv(args.epidemic_data[0])
mobility_data = pd.read_csv(args.mobility_data[0])
outdir = args.outdir[0]

#Construct signals
construct_signals(R_estimates, epidemic_data, mobility_data, outdir)
