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
parser = argparse.ArgumentParser(description = '''Simulate using google mobility data to assess the impact of the drop strength''')

parser.add_argument('--drop_df', nargs=1, type= str, default=sys.stdin, help = 'Path to outdir.')
parser.add_argument('--stan_model', nargs=1, type= str, default=sys.stdin, help = 'Stan model.')
parser.add_argument('--weeks_to_simulate', nargs=1, type= int, default=sys.stdin, help = 'Number of days to simulate.')
parser.add_argument('--outdir', nargs=1, type= str, default=sys.stdin, help = 'Path to outdir.')

###FUNCTIONS###

def format_data(drop_df):
        '''Read in and format all data needed for the model
        '''

        N=5 #number of weeks to model
        stan_data = {'M':len(drop_df), #number of countries
                    'N':N, #number of weeks to model
                    'deaths_at_drop_end':np.zeros((N,len(countries)), dtype=int),
                    'observed_deaths':np.zeros((N,len(countries)), dtype=int),
                    'reg_deaths':np.zeros((N,len(countries)), dtype=int),
                    'retail_and_recreation_percent_change_from_baseline':np.zeros((N2,len(countries))),
                    'grocery_and_pharmacy_percent_change_from_baseline':np.zeros((N2,len(countries))),
                    'transit_stations_percent_change_from_baseline':np.zeros((N2,len(countries))),
                    'workplaces_percent_change_from_baseline':np.zeros((N2,len(countries))),
                    'residential_percent_change_from_baseline':np.zeros((N2,len(countries))),
                    'EpidemicStart': [],
                    'SI':serial_interval[0:N2],
                    'y':[] #index cases
                    }

        for i in range(len(drop_df)):
            row = drop_df.loc[i]
            pdb.set_trace()
        return stan_data



def simulate(stan_data, stan_model, outdir):
        '''Simulate using stan: Efficient MCMC exploration according to Bayesian posterior distribution
        for parameter estimation.
        '''

        sm =  pystan.StanModel(file=stan_model)
        fit = sm.sampling(data=stan_data,iter=4000,warmup=2000,chains=8,thin=4, control={'adapt_delta': 0.98, 'max_treedepth': 10})
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
drop_df = pd.read_csv(args.drop_df[0])
stan_model = args.stan_model[0]
weeks_to_simulate = args.days_to_simulate[0]
outdir = args.outdir[0]

#Read data
stan_data = format_data(drop_df, weeks_to_simulate)
#Simulate
out = simulate(stan_data, stan_model, outdir)
