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

            #Construct signals
            country_signals = {
                    'R_signal':np.zeros(len(country_epidemic_data)),
                    'retail_and_recreation_percent_change_from_baseline':np.zeros(len(country_epidemic_data)),
                    'grocery_and_pharmacy_percent_change_from_baseline':np.zeros(len(country_epidemic_data)),
                    'transit_stations_percent_change_from_baseline':np.zeros(len(country_epidemic_data)),
                    'workplaces_percent_change_from_baseline':np.zeros(len(country_epidemic_data)),
                    'residential_percent_change_from_baseline':np.zeros(len(country_epidemic_data))
                    }

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
            for i in len(country_signal_data-1): #loop through data to construct signal
                row_i = country_signal_data.loc[i]
                row_i_1 = country_signal_data.loc[i+1]
                country_signal_data.iloc[i+1,'R_signal']='Median(R)'


            pdb.set_trace()




#####MAIN#####
args = parser.parse_args()
R_estimates = args.R_estimates[0]
epidemic_data = pd.read_csv(args.epidemic_data[0])
mobility_data = pd.read_csv(args.mobility_data[0])
outdir = args.outdir[0]

#Construct signals
construct_signals(R_estimates, epidemic_data, mobility_data, outdir)
