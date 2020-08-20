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
parser = argparse.ArgumentParser(description = '''Visulaize results from the ICL response team model''')

parser.add_argument('--datadir', nargs=1, type= str, default=sys.stdin, help = 'Path to dir with data.')
parser.add_argument('--results_dir', nargs=1, type= str, default=sys.stdin, help = 'Path to resultsdir.')
parser.add_argument('--countries', nargs=1, type= str, default=sys.stdin, help = 'Countries to model (csv).')
parser.add_argument('--days_to_simulate', nargs=1, type= int, default=sys.stdin, help = 'Number of days to simulate.')
parser.add_argument('--end_date', nargs=1, type= str, default=sys.stdin, help = 'Up to which date to include data.')
parser.add_argument('--short_dates', nargs=1, type= str, default=sys.stdin, help = 'Short date format for plotting (csv).')
parser.add_argument('--outdir', nargs=1, type= str, default=sys.stdin, help = 'Path to outdir.')

def read_and_format_data(datadir, countries, days_to_simulate, end_date):
        '''Read in and format all data needed for the model
        '''

        #Get epidemic data
        epidemic_data = pd.read_csv(datadir+'COVID19uptodate.csv')
        #Convert to datetime
        epidemic_data['DateRep'] = pd.to_datetime(epidemic_data['DateRep'], format='%Y/%m/%d')
        #Select all data up to end_date
        epidemic_data = epidemic_data[epidemic_data['DateRep']<=end_date]
        ## get ifr
        ifr_by_country = pd.read_csv(datadir+"popt-ifr.csv")
        #SI
        serial_interval = pd.read_csv(datadir+"serial-interval.csv")


        #Model data - to be used for plotting
        stan_data = {'dates_by_country':np.zeros((days_to_simulate,len(countries)), dtype='datetime64[D]'),
                    'deaths_by_country':np.zeros((days_to_simulate,len(countries))),
                    'cases_by_country':np.zeros((days_to_simulate,len(countries))),
                    'days_by_country':np.zeros(len(countries))
                    }


        #Get data by country
        for c in range(len(countries)):
                country = countries[c]

                #Get country epidemic data
                country_epidemic_data = epidemic_data[epidemic_data['Country']==country]
                #Sort on date
                country_epidemic_data = country_epidemic_data.sort_values(by='DateRep')
                #Reset index
                country_epidemic_data = country_epidemic_data.reset_index()

                #Get all dates with at least 10 deaths
                cum_deaths = country_epidemic_data['Deaths'].cumsum()
                death_index = cum_deaths[cum_deaths>=10].index[0]
                di30 = death_index-30
                #Get part of country_epidemic_data 30 days before day with at least 10 deaths
                country_epidemic_data = country_epidemic_data.loc[di30:]
                #Reset index
                country_epidemic_data = country_epidemic_data.reset_index()

                print(country, len(country_epidemic_data), np.array(country_epidemic_data['DateRep'], dtype='datetime64[D]')[0])
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
                stan_data['dates_by_country'][:N,c] = np.array(country_epidemic_data['DateRep'], dtype='datetime64[D]')
                #Save deaths
                stan_data['deaths_by_country'][:N,c] = country_epidemic_data['Deaths']
                #Save cases
                stan_data['cases_by_country'][:N,c] = country_epidemic_data['Cases']

        return stan_data

def fix_covariates(covariates):
        '''Change dates so all covariates that happen after the lockdown
        to have the same date as the lockdown. Also add the covariate "any intervention"
        '''
        NPI = ['schools_universities',  'public_events',
        'social_distancing_encouraged', 'self_isolating_if_ill']
        #Add covariate for first intervention
        covariates['first_intervention'] = ''

        for i in range(len(covariates)):
                row = covariates.iloc[i]
                lockdown = row['lockdown']
                first_inter = '2021-04-01'
                for n in NPI:
                        if row[n] < first_inter:
                                first_inter = row[n]
                        if row[n] > lockdown:
                                covariates.at[i,n] = lockdown

                covariates.at[i,'first_intervention'] = first_inter
        return covariates


def plot_posterior(matrix, countries, param):
    '''Visualize the posterior distributions of different parameters
    '''
    for i in range(matrix.shape[1]):
        fig, ax = plt.subplots(figsize=(3/2.54, 3/2.54))
        sns.distplot(matrix[2000:,i]) #The first 2000 samplings are warmup
        ax.set_title(countries[i])
        if countries[i] == 'United_Kingdom':
            ax.set_title('United Kingdom')
        ax.set_xlabel(param)
        #ax.set_xlim([1.5,5.5])
        ax.axvline(x=3.28, ymin=0, ymax=2, linestyle='--',linewidth=1)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        fig.tight_layout()
        fig.savefig(outdir+'figures/posterior/'+param+'_'+countries[i]+'.png', format = 'png',dpi=300 )
        plt.close()


def visualize_results(outdir, datadir, results_dir, countries, stan_data, days_to_simulate, short_dates):
    '''Visualize results
    '''

    #Plot alpha posteriors
    run_colors = {'original':'tab:purple','no_last':'tab:pink', 'no_lock_no_last':'tab:olive'}
    labels  = {'original':'Original (i)','no_last':'No last (ii)', 'no_lock_no_last':'No lockdown or last (iii)'}
    alpha_titles = {0:'Schools and Universities',1:'Self isolating if ill',2:'Public events',3:'First intervention',4:'Lockdown',5:'Social distancing encouraged',6:'Last intervention'}
    alpha_names = {0:'schools_universities',1:'self_isolating_if_ill',2:'public_events',3:'first_intervention',4:'lockdown',5:'social_distancing_encouraged',6:'last_intervention'}

    #Read in data
    #For models fit using MCMC, also included in the summary are the
    #Monte Carlo standard error (se_mean), the effective sample size (n_eff),
    #and the R-hat statistic (Rhat).
    for i in range(7):
        #Create plot for posterior
        fig, ax = plt.subplots(figsize=(6/2.54, 4.5/2.54))
        types = ['original','no_last','no_lock_no_last']
        #Go through all simulations
        for type in types:
            alphas = np.load(results_dir+type+'/alpha.npy', allow_pickle=True)
            sns.distplot(100*(1-np.exp(-alphas[8000:,i])),color=run_colors[type],
            label=labels[type],
            kde_kws={"lw": 0.5},
            hist_kws={"linewidth": 3,"alpha": 0.5}) #The first 8000 samplings are warmup
            print(alpha_titles[i], np.median(100*(1-np.exp(-alphas[8000:,i]))))
        ax.set_title(alpha_titles[i])
        ax.set_ylabel('Density')
        ax.set_xlabel('Relative % reduction in Rt')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        plt.legend()
        fig.tight_layout()
        fig.savefig(outdir+'alpha_'+alpha_names[i]+'.png', format = 'png',dpi=300 )
        plt.close()




#####MAIN#####
#Set font size
matplotlib.rcParams.update({'font.size': 7})
args = parser.parse_args()
datadir = args.datadir[0]
results_dir = args.results_dir[0]
countries = args.countries[0].split(',')
days_to_simulate=args.days_to_simulate[0] #Number of days to model. Increase for further forecast
end_date=args.end_date[0]
short_dates = pd.read_csv(args.short_dates[0])
#Make sure the np dates are in the correct format
short_dates['np_date'] = pd.to_datetime(short_dates['np_date'], format='%Y/%m/%d')
outdir = args.outdir[0]

#Read data
stan_data = read_and_format_data(datadir, countries, days_to_simulate, end_date)

#Visualize
visualize_results(outdir, datadir, results_dir, countries, stan_data, days_to_simulate, short_dates)
