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
parser = argparse.ArgumentParser(description = '''Format data from JHS to use in EpiEstim R estimates''')

parser.add_argument('--us_cases', nargs=1, type= str, default=sys.stdin, help = 'Path to case data.')
parser.add_argument('--mobility_data', nargs=1, type= str, default=sys.stdin, help = 'Path to mobility data. Needed for knowledge of which states have sufficient data.')
parser.add_argument('--outdir', nargs=1, type= str, default=sys.stdin, help = 'Path to outdir.')

###FUNCTIONS###
def read_and_format_data(us_cases, mobility_data):
        '''Read in and format all data
        '''
        #Convert to datetime
        mobility_data['date']=pd.to_datetime(mobility_data['date'], format='%Y/%m/%d')
        #Select US
        mobility_data = mobility_data[mobility_data['country_region']=="United States"]
        #Look at the US states
        subregions = mobility_data['sub_region_1'].unique()[1:] #The first subregion is nan (no subregion)
        #Save all extracted data
        complete_df = pd.DataFrame()
        #Get data by state
        for c in range(len(subregions)):
            region =subregions[c]
            #Skip capitol
            if region == 'District of Columbia':
                continue
            print(region)
            #Get region epidemic data
            regional_cases = us_cases[us_cases['Province_State']== region]
            cols = regional_cases.columns
            #Calculate back per day - now cumulative
            cases_per_day = []
            dates = cols[12:]
            #First cases
            cases_per_day.append(np.sum(regional_cases[dates[0]]))
            for d in range(1,len(dates)):#The first 12 columns are not cases
                cases_per_day.append(np.sum(regional_cases[dates[d]])-np.sum(regional_cases[dates[d-1]]))
            #Create dataframe
            regional_epidemic_data = pd.DataFrame()
            regional_epidemic_data['date']=dates
            #Convert to datetime
            regional_epidemic_data['date'] = pd.to_datetime(regional_epidemic_data['date'], format='%m/%d/%y')
            regional_epidemic_data['cases']=cases_per_day

            #Sort on date
            regional_epidemic_data = regional_epidemic_data.sort_values(by='date')

            #Smooth cases
            cases = np.array(regional_epidemic_data['cases'])
            sm_cases = np.zeros(len(cases))
            #Do a 7day sliding window to get more even case predictions
            for i in range(7,len(regional_epidemic_data)+1):
                sm_cases[i-1]=np.average(cases[i-7:i])
            sm_cases[0:6] = sm_cases[6]
            regional_epidemic_data['cases']=sm_cases
            #Append data to final df
            regional_epidemic_data['region']=region
            complete_df = complete_df.append(regional_epidemic_data, ignore_index=True)
        return complete_df


def simulate(stan_data, stan_model, outdir):
        '''Simulate using stan: Efficient MCMC exploration according to Bayesian posterior distribution
        for parameter estimation.
        '''

        sm =  pystan.StanModel(file=stan_model)
        fit = sm.sampling(data=stan_data,iter=4000,warmup=2000,chains=8,thin=4, control={'adapt_delta': 0.92, 'max_treedepth': 20})
        #Save summary
        s = fit.summary()
        summary = pd.DataFrame(s['summary'], columns=s['summary_colnames'], index=s['summary_rownames'])
        summary.to_csv(outdir+'summary.csv')

        #Save fit - each parameter as np array
        out = fit.extract()
        for key in [*out.keys()]:
            fit_param = out[key]
            np.save(outdir+key+'.npy', fit_param)
        return out

#####MAIN#####
args = parser.parse_args()
us_cases = pd.read_csv(args.us_cases[0])
mobility_data = pd.read_csv(args.mobility_data[0])
outdir = args.outdir[0]
#Read data
complete_df = read_and_format_data(us_cases, mobility_data)
#Save complete df
complete_df.to_csv('complete_case_df.csv')
