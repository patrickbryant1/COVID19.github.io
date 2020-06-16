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

    diff_df = pd.DataFrame()
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
        mean_cases, mean_deaths = model_continued_lockdown(means['prediction'],means['Rt'], exi,days, f, SI)
        lower_cases,lower_deaths = model_continued_lockdown(lower_bound['prediction'],lower_bound['Rt'], exi,days, f, SI)
        higher_cases, higher_deaths = model_continued_lockdown(higher_bound['prediction'],higher_bound['Rt'], exi,days, f, SI)
        lower25_cases,lower25_deaths = model_continued_lockdown(lower_bound25['prediction'],lower_bound25['Rt'], exi,days, f, SI)
        higher75_cases, higher75_deaths = model_continued_lockdown(higher_bound75['prediction'],higher_bound75['Rt'], exi,days, f, SI)
        #Add to df
        state_lockdown = pd.DataFrame()
        #Means
        state_lockdown['mean_cases']=mean_cases
        state_lockdown['mean_deaths']=mean_deaths
        state_lockdown['mean_Rt']=means['Rt'][exi]
        #95 %
        state_lockdown['lower_cases']=lower_cases
        state_lockdown['lower_deaths']=lower_deaths
        state_lockdown['lower_Rt']=lower_bound['Rt'][exi]
        state_lockdown['higher_cases']=higher_cases
        state_lockdown['higher_deaths']=higher_deaths
        state_lockdown['higher_Rt']=higher_bound['Rt'][exi]
        #50%
        state_lockdown['lower25_cases']=lower25_cases
        state_lockdown['lower25_deaths']=lower25_deaths
        state_lockdown['lower25_Rt']=lower_bound25['Rt'][exi]
        state_lockdown['higher75_cases']=higher75_cases
        state_lockdown['higher75_deaths']=higher75_deaths
        state_lockdown['higher75_Rt']=higher_bound75['Rt'][exi]
        state_lockdown['state'] = state
        state_lockdown['extreme_index']=exi

        #Add the parks
        
        diff_df = diff_df.append(state_lockdown, ignore_index=True)


    #Save df
    diff_df.to_csv('lockdown_df.csv')
    print('Saved lockdown dataframe')
    return None

def model_continued_lockdown(cases,R, exi,days, f, SI):
    '''Calculate what would have happened if the lockdown was continued
    '''

    pred_cases = np.zeros(days)
    pred_cases[:exi]=cases[:exi]
    pred_deaths = np.zeros(days)
    for i in range(exi,days):
        convolution=0 #reset
    	#loop through all days up to current
        for j in range(0,i-1):
            #Cases today due to cumulative probability, sum(cases*rel.change due to SI)
            convolution += pred_cases[j]*SI[i-j]
        pred_cases[i] = R[exi] * convolution #Scale with average spread per case

	#Step through all days til end of forecast
    for i in range(exi,days):
        for j in range(0,i-1):
          pred_deaths[i] += pred_cases[j]*f[i-j] #Deaths today due to cumulative probability, sum(deaths*rel.change due to f)

    return pred_cases, pred_deaths
#####MAIN#####
args = parser.parse_args()
complete_df = pd.read_csv(args.complete_df[0])
modelling_results = pd.read_csv(args.modelling_results[0])
days_to_simulate = args.days_to_simulate[0]
outdir = args.outdir[0]
calculate_diff(complete_df,modelling_results,days_to_simulate)
