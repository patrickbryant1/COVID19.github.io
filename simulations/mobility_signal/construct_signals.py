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


def read_and_format_data(R_estimates, epidemic_data, mobility_data, outdir):
        '''Read in and format all data needed for the signal correlation analysis
        '''

        #Convert epidemic data to datetime
        epidemic_data['dateRep'] = pd.to_datetime(epidemic_data['dateRep'], format='%d/%m/%Y')


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
            country_R = pd.read_csv(r_estimates+country+'_R_estimate.csv')
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
            pdb.set_trace()


            country_signals = {
                    'R_signal':np.zeros(len(country_epidemic_data)),
                    'retail_and_recreation_percent_change_from_baseline':np.zeros(len(country_epidemic_data)),
                    'grocery_and_pharmacy_percent_change_from_baseline':np.zeros(len(country_epidemic_data)),
                    'transit_stations_percent_change_from_baseline':np.zeros(len(country_epidemic_data)),
                    'workplaces_percent_change_from_baseline':np.zeros(len(country_epidemic_data)),
                    'residential_percent_change_from_baseline':np.zeros(len(country_epidemic_data))
                    }

                #Mobility data from Google
                country_cov_data = mobility_data[mobility_data['country_region']==country]
                if country == 'United_Kingdom': #Different assignments for UK
                    country_cov_data = mobility_data[mobility_data['country_region']=='United Kingdom']
                #Get whole country - no subregion
                country_cov_data =  country_cov_data[country_cov_data['sub_region_1'].isna()]
                #Get matching dates
                country_cov_data = country_cov_data[country_cov_data['date'].isin(country_epidemic_data['dateRep'])]
                end_date = max(country_cov_data['date']) #Last date for mobility data
                for name in covariate_names:
                    country_epidemic_data.loc[country_epidemic_data.index,name] = 0 #Set all to 0
                    for d in range(len(country_epidemic_data)): #loop through all country data
                        row_d = country_epidemic_data.loc[d]
                        date_d = row_d['dateRep'] #Extract date
                        try:
                            change_d = np.round(float(country_cov_data[country_cov_data['date']==date_d][name].values[0])/100, 2) #Match mobility change on date
                            if not np.isnan(change_d):
                                country_epidemic_data.loc[d,name] = change_d #Add to right date in country data
                        except:
                            continue #Date too far ahead



#####MAIN#####
args = parser.parse_args()
R_estimates = args.R_estimates[0]
epidemic_data = pd.read_csv(args.epidemic_data[0])
mobility_data = pd.read_csv(args.mobility_data[0])
outdir = args.outdir[0]

#Read data
read_and_format_data(R_estimates, epidemic_data, mobility_data, outdir)
#Simulate
out = simulate(stan_data, stan_model, outdir)
