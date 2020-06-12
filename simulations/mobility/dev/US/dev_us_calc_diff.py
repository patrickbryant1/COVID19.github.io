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
parser = argparse.ArgumentParser(description = '''Simulate using google mobility data and most of the ICL response team model''')

parser.add_argument('--complete_df', nargs=1, type= str, default=sys.stdin, help = 'Path to all input data.')
parser.add_argument('--modelling_results', nargs=1, type= str, default=sys.stdin, help = 'Path to stan model results.')
parser.add_argument('--outdir', nargs=1, type= str, default=sys.stdin, help = 'Path to outdir.')

###FUNCTIONS###
def calculate_diff(complete_df,modelling_results):
    '''Calculate the scenario that would have been obtained if lockdown had not ended
    Get the R estimate at the extreme points in mobility.
    '''
    #Covariate names
    covariate_names = ['retail_and_recreation_percent_change_from_baseline',
   'grocery_and_pharmacy_percent_change_from_baseline',
   'transit_stations_percent_change_from_baseline',
   'workplaces_percent_change_from_baseline',
   'residential_percent_change_from_baseline']

    states = complete_df['region'].unique()
    #Loop through states
    for i in range(1,len(states)+1):

        state= states[i-1]
        state_data = complete_df[complete_df['region']==state]
        days = len(state_data)#Number of days for state i
        extreme_indices = [] #Save the indices for the most extreme mobility changes
        #Add covariate data
        for name in covariate_names:
            cov_i = np.array(state_data[name])
            if name == 'residential_percent_change_from_baseline':
                extreme_val = max(cov_i)
            else:
                extreme_val = min(cov_i)
            #Get index
            extreme_index = np.where(cov_i==extreme_val)[0][0]#Get index for extreme val
            extreme_indices.append(extreme_index)
        #Get the latest extreme point reached
        exi = max(extreme_indices)
        #Extract modeling results
        means = {'prediction':np.zeros((days)),'E_deaths':np.zeros((days)), 'Rt':np.zeros((days))}
        lower_bound = {'prediction':np.zeros((days)),'E_deaths':np.zeros((days)), 'Rt':np.zeros((days))} #Estimated 2.5 %
        higher_bound = {'prediction':np.zeros((days)),'E_deaths':np.zeros((days)), 'Rt':np.zeros((days))} #Estimated 97.5 % - together 95 % CI
        lower_bound25 = {'prediction':np.zeros((days)),'E_deaths':np.zeros((days)), 'Rt':np.zeros((days))} #Estimated 25%
        higher_bound75 = {'prediction':np.zeros((days)),'E_deaths':np.zeros((days)), 'Rt':np.zeros((days))} #Estimated 55 % - together 75 % CI
        #Get means and 95 % CI for cases (prediction), deaths and Rt for all time steps
        for j in range(1,days+1):
            for var in ['prediction', 'E_deaths','Rt']:
                    var_ij = modelling_results[modelling_results['Unnamed: 0']==var+'['+str(j)+','+str(i)+']']
                    means[var][j-1]=var_ij['mean'].values[0]
                    lower_bound[var][j-1]=var_ij['2.5%'].values[0]
                    higher_bound[var][j-1]=var_ij['97.5%'].values[0]
                    lower_bound25[var][j-1]=var_ij['25%'].values[0]
                    higher_bound75[var][j-1]=var_ij['75%'].values[0]

        #Use the latest extreme index to fetch R

        pdb.set_trace()

def calculate_continued_lockdown(means, lower_bound, higher_bound, lower_bound25, higher_bound75, exi):
    '''Calculate what would have happened if the lockdown was continued
    '''
#####MAIN#####
args = parser.parse_args()
complete_df = pd.read_csv(args.complete_df[0])
modelling_results = pd.read_csv(args.modelling_results[0])
outdir = args.outdir[0]
calculate_diff(complete_df,modelling_results)
