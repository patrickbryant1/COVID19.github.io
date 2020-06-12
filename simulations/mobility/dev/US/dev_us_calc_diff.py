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

import pdb



#Arguments for argparse module:
parser = argparse.ArgumentParser(description = '''Simulate using google mobility data and most of the ICL response team model''')

parser.add_argument('--complete_df', nargs=1, type= str, default=sys.stdin, help = 'Path to all input data.')
parser.add_argument('--modelling_results', nargs=1, type= str, default=sys.stdin, help = 'Path to stan model results.')
parser.add_argument('--days_to_simulate', nargs=1, type= int, default=sys.stdin, help = 'Number of days to simulate.')
parser.add_argument('--outdir', nargs=1, type= str, default=sys.stdin, help = 'Path to outdir.')

###FUNCTIONS###
def conv_gamma_params(mean,std):
        '''Returns converted shape and scale params
        shape (α) = 1/std^2
        scale (β) = mean/shape
        '''
        shape = 1/(std*std)
        scale = mean/shape

        return shape,scale

def infection_to_death():
        '''Simulate the time from infection to death: Infection --> Onset --> Death'''
        #Infection to death: sum of ito and otd
        itd_shape, itd_scale = conv_gamma_params((5.1+18.8), (0.45))
        itd = gamma(a=itd_shape, scale = itd_scale) #a=shape
        return itd

def serial_interval_distribution(N2):
        '''Models the the time between when a person gets infected and when
        they subsequently infect another other people
        '''
        serial_shape, serial_scale = conv_gamma_params(6.5,0.62)
        serial = gamma(a=serial_shape, scale = serial_scale) #a=shape

        return serial.pdf(np.arange(1,N2+1))

def get_death_f(N2):
    '''Calculate death fraction
    '''
    #Fatality rate - fixed
    cfr = 0.01
    #Infection to death
    itd = infection_to_death()
    #Get hazard rates for all days in country data
    #This can be done only once now that the cfr is constant
    h = np.zeros(N2) #N2 = N+forecast
    f = np.cumsum(itd.pdf(np.arange(1,len(h)+1,0.5))) #Cumulative probability to die for each day
    for i in range(1,len(h)):
        #for each day t, the death prob is the area btw [t-0.5, t+0.5]
        #divided by the survival fraction (1-the previous death fraction), (fatality ratio*death prob at t-0.5)
        #This will be the percent increase compared to the previous end interval
        h[i] = (cfr*(f[i*2+1]-f[i*2-1]))/(1-cfr*f[i*2-1])

    #The number of deaths today is the sum of the past infections weighted by their probability of death,
    #where the probability of death depends on the number of days since infection.
    s = np.zeros(N2)
    s[0] = 1
    for i in range(1,len(s)):
        #h is the percent increase in death
        #s is thus the relative survival fraction
        #The cumulative survival fraction will be the previous
        #times the survival probability
        #These will be used to track how large a fraction is left after each day
        #In the end all of this will amount to the adjusted death fraction
        s[i] = s[i-1]*(1-h[i-1]) #Survival fraction

    #Multiplying s and h yields fraction dead of fraction survived
    f = s*h #This will be fed to the Stan Model

    return f

def calculate_diff(complete_df,modelling_results,days_to_simulate):
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

    #Get death fraction
    f = get_death_f(days_to_simulate)
    #Get serial interval distribution
    SI = serial_interval_distribution(days_to_simulate)

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
        calculate_continued_lockdown(means, lower_bound, higher_bound, lower_bound25, higher_bound75, exi, f, SI)



def calculate_continued_lockdown(means, lower_bound, higher_bound, lower_bound25, higher_bound75, exi, f, SI):
    '''Calculate what would have happened if the lockdown was continued
    '''
    pdb.set_trace()
#####MAIN#####
args = parser.parse_args()
complete_df = pd.read_csv(args.complete_df[0])
modelling_results = pd.read_csv(args.modelling_results[0])
days_to_simulate = args.days_to_simulate[0]
outdir = args.outdir[0]
calculate_diff(complete_df,modelling_results,days_to_simulate)
