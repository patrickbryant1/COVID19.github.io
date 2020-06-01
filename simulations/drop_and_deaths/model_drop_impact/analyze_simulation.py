#! /usr/bin/env python3
# -*- coding: utf-8 -*-


import argparse
import sys
import os
import glob
import pandas as pd
import numpy as np
from ast import literal_eval
from sklearn.linear_model import LinearRegression
import pystan

import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import pdb



#Arguments for argparse module:
parser = argparse.ArgumentParser(description = '''Analyze simulations''')

parser.add_argument('--drop_df', nargs=1, type= str, default=sys.stdin, help = 'Path to outdir.')
parser.add_argument('--stan_model', nargs=1, type= str, default=sys.stdin, help = 'Stan model.')
parser.add_argument('--weeks_to_simulate', nargs=1, type= int, default=sys.stdin, help = 'Number of days to simulate.')
parser.add_argument('--outdir', nargs=1, type= str, default=sys.stdin, help = 'Path to outdir.')

def format_data(drop_df, weeks_to_simulate):
        '''Read in and format all data needed for the model
        '''

        N=weeks_to_simulate #number of weeks to model
        stan_data = {'M':len(drop_df), #number of countries
                    'N':N, #number of weeks to model
                    'deaths_at_drop_end':np.log10(np.array(drop_df['drop_end_deaths'])),
                    'observed_deaths':np.zeros((N,len(drop_df))),
                    'reg_deaths':np.zeros((N,len(drop_df))),
                    'covariate1':np.array(drop_df['retail'])/100, #Divide to get fraction
                    'covariate2':np.array(drop_df['grocery and pharmacy'])/100,
                    'covariate3':np.array(drop_df['transit'])/100,
                    'covariate4':np.array(drop_df['work'])/100,
                    'covariate5':np.array(drop_df['residential'])/100,
                    }

        #Assign the observed deaths
        for i in range(len(drop_df)):
            row = drop_df.loc[i]
            stan_data['observed_deaths'][:,i]=np.log10(literal_eval(row['Deaths per million']))

        #Regress the deaths i = 4,5,6,7 and 8 weeks later
        for i in range(N):
            reg = LinearRegression().fit(stan_data['deaths_at_drop_end'].reshape(-1, 1),stan_data['observed_deaths'][i,:].reshape(-1, 1))
            pred = reg.predict(stan_data['deaths_at_drop_end'].reshape(-1, 1))
            stan_data['reg_deaths'][i,:]=pred[:,0]
        return stan_data

def visualize_results(stan_data, outdir):
    '''Visualize results
    '''

    #Read in data
    #For models fit using MCMC, also included in the summary are the
    #Monte Carlo standard error (se_mean), the effective sample size (n_eff),
    #and the R-hat statistic (Rhat).
    summary = pd.read_csv(outdir+'summary.csv')

    alphas = np.load(outdir+'alpha.npy', allow_pickle=True)
    phi = np.load(outdir+'phi.npy', allow_pickle=True)

    #Plot rhat
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.hist(summary['Rhat'])
    ax.set_ylabel('Count')
    ax.set_xlabel("Rhat")
    fig.savefig(outdir+'plots/rhat.png', format='png', dpi=300)
    plt.close()

    #Plot values from each iteration as r function mcmc_parcoord
    mcmc_parcoord(np.concatenate([alphas,np.expand_dims(phi,axis=1)], axis=1), covariate_names+['phi'], outdir)

    #Plot alpha (Rt = R0*-exp(sum{mob_change*alpha1-6}))
    fig, ax = plt.subplots(figsize=(9/2.54, 9/2.54))
    alpha_colors = {0:'tab:red',1:'tab:purple',2:'tab:pink', 3:'tab:olive', 4:'tab:cyan'}
    for i in range(1,6):
        alpha = summary[summary['Unnamed: 0']=='alpha['+str(i)+']']
        alpha_m = alpha['mean'].values[0]
        alpha_2_5 = alpha['2.5%'].values[0]
        alpha_25 = alpha['25%'].values[0]
        alpha_75 = alpha['75%'].values[0]
        alpha_97_5 = alpha['97.5%'].values[0]
        ax.plot([i-0.25,i+0.25],[alpha_m,alpha_m],color = alpha_colors[i-1])
        ax.plot([i]*2,[alpha_2_5,alpha_97_5],  marker = '_',color = alpha_colors[i-1])
        rect = Rectangle((i-0.25,alpha_25),0.5,alpha_75-alpha_25,linewidth=1, color = alpha_colors[i-1], alpha = 0.3)
        ax.add_patch(rect)
    ax.set_ylabel('Fractional reduction in R0')
    ax.set_xticks([1,2,3,4,5])
    ax.set_xticklabels(['retail and recreation', 'grocery and pharmacy', 'transit stations','workplace', 'residential'],rotation='vertical')
    plt.tight_layout()
    fig.savefig(outdir+'plots/alphas.png', format='png', dpi=300)
    plt.close()




    #plot per week delay
    for i in range(1,6):
        #Extract modeling results
        means = {'E_deaths':[]}
        lower_bound = {'E_deaths':[]} #Estimated 2.5 %
        higher_bound = {'E_deaths':[]} #Estimated 97.5 % - together 95 % CI
        lower_bound25 = {'E_deaths':[]} #Estimated 25%
        higher_bound75 = {'E_deaths':[]} #Estimated 55 % - together 75 % CI
        #Get means and 95 % CI for cases (prediction), deaths and Rt for all time steps
        for j in range(1,len(stan_data)):
                var_ij = summary[summary['Unnamed: 0']==var+'['+str(j)+','+str(i)+']']
                means[var].append(var_ij['mean'].values[0])
                lower_bound[var].append(var_ij['2.5%'].values[0])
                higher_bound[var].append(var_ij['97.5%'].values[0])
                lower_bound25[var].append(var_ij['25%'].values[0])
                higher_bound75[var].append(var_ij['75%'].values[0])

        #Plot cases
        #Per day
        plot_shade_ci(days, end, dates[0], means['prediction'], observed_country_cases,lower_bound['prediction'],
        higher_bound['prediction'], lower_bound25['prediction'], higher_bound75['prediction'], 'Cases per day',
        outdir+'plots/'+country+'_cases.png',country_npi, country_retail, country_grocery, country_transit, country_work, country_residential, short_dates)

    return None

def mcmc_parcoord(cat_array, xtick_labels, outdir):
    '''Plot parameters for each iteration next to each other as in the R fucntion mcmc_parcoord
    '''
    xtick_labels.insert(0,'')
    fig, ax = plt.subplots(figsize=(8, 8))
    for i in range(2000,cat_array.shape[0]): #loop through all iterations
            ax.plot(np.arange(cat_array.shape[1]), cat_array[i,:], color = 'k', alpha = 0.1)
    ax.plot(np.arange(cat_array.shape[1]), np.median(cat_array, axis = 0), color = 'r', alpha = 1)
    ax.set_xticklabels(xtick_labels,rotation='vertical')
    ax.set_ylim([-5,20])
    plt.tight_layout()
    fig.savefig(outdir+'plots/mcmc_parcoord.png', format = 'png')
    plt.close()




#####MAIN#####
#Set font size
matplotlib.rcParams.update({'font.size': 9})
args = parser.parse_args()
drop_df = pd.read_csv(args.drop_df[0])
stan_model = args.stan_model[0]
weeks_to_simulate = args.weeks_to_simulate[0]
outdir = args.outdir[0]

#Covariate names
covariate_names = ['retail_and_recreation_percent_change_from_baseline',
'grocery_and_pharmacy_percent_change_from_baseline',
'transit_stations_percent_change_from_baseline',
'workplaces_percent_change_from_baseline',
'residential_percent_change_from_baseline']

#Read data
stan_data = format_data(drop_df, weeks_to_simulate)

#Visualize
visualize_results(stan_data, outdir)

fig.savefig(outdir+'plots/NPI_markers.png', format = 'png')
