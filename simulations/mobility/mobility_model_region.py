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
import read_and_format_SE as rf
import pdb



#Arguments for argparse module:
parser = argparse.ArgumentParser(description = '''Simulate using google mobility data and most of the ICL response team model''')

parser.add_argument('--datadir', nargs=1, type= str, default=sys.stdin, help = 'Path to outdir.')
parser.add_argument('--countries', nargs=1, type= str, default=sys.stdin, help = 'Countries to model (csv).')
parser.add_argument('--stan_model', nargs=1, type= str, default=sys.stdin, help = 'Stan model.')
parser.add_argument('--days_to_simulate', nargs=1, type= int, default=sys.stdin, help = 'Number of days to simulate.')
parser.add_argument('--end_date', nargs=1, type= str, default=sys.stdin, help = 'Up to which date to include data.')
parser.add_argument('--outdir', nargs=1, type= str, default=sys.stdin, help = 'Path to outdir.')
parser.add_argument('--region', nargs=1, type= str, default="SE",  help = 'Region to use (SE,US)')

###FUNCTIONS###

###DISTRIBUTIONS###




def simulate(stan_data, stan_model, outdir):
        '''Simulate using stan: Efficient MCMC exploration according to Bayesian posterior distribution
        for parameter estimation.
        '''

        sm =  pystan.StanModel(file=stan_model)
        fit = sm.sampling(data=stan_data,iter=4000,warmup=2000,chains=8,thin=4, control={'adapt_delta': 0.98, 'max_treedepth': 20})
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
datadir = args.datadir[0]
countries = args.countries[0].split(',') # Does not work due to spaces in names
#countries=["Stockholm","Västra Götaland","Dalarna","Jönköping","Gävleborg","Skåne","Sörmland","Uppsala","Östergötland"]
#countries=["Stockholm","Västra Götaland","Dalarna","Skåne","Sörmland","Östergötland"]
stan_model = args.stan_model[0]
days_to_simulate = args.days_to_simulate[0]
end_date = np.datetime64(args.end_date[0])
outdir = args.outdir[0]
region=args.region[0]

#Read data
stan_data = rf.read_and_format_data(datadir, countries, days_to_simulate, end_date,region)

#Simulate
out = simulate(stan_data, stan_model, outdir)
