#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import sys
import os
import glob
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from scipy.stats import gamma
import numpy as np
import seaborn as sns


import pdb



#Arguments for argparse module:
parser = argparse.ArgumentParser(description = '''Compare estimates for the basic reproductive number from the mobility model and the EpiEstim R package''')

parser.add_argument('--EpiEstimdir', nargs=1, type= str, default=sys.stdin, help = 'Path to directory with epiestim R estimates.')
parser.add_argument('--stan_results', nargs=1, type= str, default=sys.stdin, help = 'Path to csv with stan results.')
parser.add_argument('--country_meta', nargs=1, type= str, default=sys.stdin, help = 'Country meta data.')
parser.add_argument('--end_date', nargs=1, type= str, default=sys.stdin, help = 'Up to which date to include data.')
parser.add_argument('--short_dates', nargs=1, type= str, default=sys.stdin, help = 'Short date format for plotting (csv).')
parser.add_argument('--outdir', nargs=1, type= str, default=sys.stdin, help = 'Path to outdir.')


def compare_R_estimates(EpiEstimdir, stan_results, country_meta, end_date, short_dates, outdir):
    '''Compare the R estimates from EpiEstim and the mobility model
    '''

    countries = country_meta['Country'].unique()
    for i in range(len(countries)):
        country = countries[i]
        country_days = country_meta.loc[i,'epidemic_days']
        country_start_date = country_meta.loc[i,'start_date']
        #Load epiestim estimates
        country_epiestim = pd.read_csv(EpiEstimdir+country+'_R_estimate.csv')
        #Fix datetime
        country_epiestim['date'] = pd.to_datetime(country_epiestim['date'], format='%d/%m/%Y')
        #Get R estimates up to last date
        country_epiestim = country_epiestim[country_epiestim['date']<=end_date]
        country_epiestim = country_epiestim[country_epiestim['Mean(R)']<=5]

        #Extract mobility modeling results
        means =[]
        lower_bound = []#Estimated 2.5 %
        higher_bound =[] #Estimated 97.5 % - together 95 % CI
        lower_bound25 =[] #Estimated 25%
        higher_bound75 =[] #Estimated 55 % - together 75 % CI
        #Get means and 95 % CI for cases (prediction), deaths and Rt for all time steps
        for j in range(1,country_days+1):#3 week forecast
            var_ij = stan_results[stan_results['Unnamed: 0']=='Rt['+str(j)+','+str(i+1)+']']
            means.append(var_ij['mean'].values[0])
            lower_bound.append(var_ij['2.5%'].values[0])
            higher_bound.append(var_ij['97.5%'].values[0])
            lower_bound25.append(var_ij['25%'].values[0])
            higher_bound75.append(var_ij['75%'].values[0])
        #All dates for country
        country_dates = np.arange(country_start_date,np.datetime64('2020-04-20'))
        #Create df of R estimates from mobility model
        country_mobilityR = pd.DataFrame()
        country_mobilityR['date']=country_dates
        country_mobilityR['mean_R'] = means
        country_mobilityR['0.025_R'] = lower_bound
        country_mobilityR['0.975_R'] = higher_bound
        country_mobilityR['0.25_R'] = lower_bound25
        country_mobilityR['0.75_R'] = higher_bound75
        country_mobilityR = country_mobilityR[country_mobilityR['mean_R']<=5] #Select below 5
        #Join dfs
        df = pd.merge(country_epiestim,country_mobilityR, left_on=['date'], right_on=['date'], how='inner')

        #Visualize
        fig, ax = plt.subplots(figsize=(6/2.54, 6/2.54))
        ax.plot(df['mean_R'],df['Mean(R)'])
        ax.fill_between(df['mean_R'],df['Quantile.0.025(R)'], df['Quantile.0.975(R)'], color='cornflowerblue', alpha=0.4)
        plt.show()

#####MAIN#####
#Set font size
matplotlib.rcParams.update({'font.size': 7})
args = parser.parse_args()
EpiEstimdir = args.EpiEstimdir[0]
stan_results = pd.read_csv(args.stan_results[0])
country_meta = pd.read_csv(args.country_meta[0])
end_date=args.end_date[0]
short_dates = pd.read_csv(args.short_dates[0])
#Make sure the np dates are in the correct format
short_dates['np_date'] = pd.to_datetime(short_dates['np_date'], format='%Y/%m/%d')
outdir = args.outdir[0]
#Compare
compare_R_estimates(EpiEstimdir, stan_results, country_meta, end_date, short_dates, outdir)
