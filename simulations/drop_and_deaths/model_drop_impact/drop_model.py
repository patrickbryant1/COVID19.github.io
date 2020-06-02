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
from sklearn.ensemble import RandomForestClassifier
import pystan
import matplotlib
import matplotlib.pyplot as plt
import pdb



#Arguments for argparse module:
parser = argparse.ArgumentParser(description = '''Simulate using google mobility data to assess the impact of the drop strength''')

parser.add_argument('--drop_df', nargs=1, type= str, default=sys.stdin, help = 'Path to outdir.')
parser.add_argument('--stan_model', nargs=1, type= str, default=sys.stdin, help = 'Stan model.')
parser.add_argument('--weeks_to_simulate', nargs=1, type= int, default=sys.stdin, help = 'Number of days to simulate.')
parser.add_argument('--outdir', nargs=1, type= str, default=sys.stdin, help = 'Path to outdir.')

###FUNCTIONS###

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
        #Calculate devation from regressed lines
        #stan_data['deviation']=stan_data['observed_deaths']-stan_data['reg_deaths']
        return stan_data

def analyze_deviation(drop_df, stan_data, outdir):
    '''Plot deviation to check clustering
    '''
    drop_df['av_mob_change'] = (np.absolute(drop_df['retail']/100)+ np.absolute(drop_df['grocery and pharmacy']/100)+ np.absolute(drop_df['transit']/100)+ np.absolute(drop_df['work']/100)+np.absolute(drop_df['residential']/100))/5
    cmap = plt.cm.rainbow

    for cov in ['retail', 'grocery and pharmacy', 'transit', 'work', 'residential','av_mob_change']:
        fig, ax = plt.subplots()
        norm = matplotlib.colors.Normalize(vmin=min(drop_df[cov]), vmax=max(drop_df[cov]))
        ax.scatter(stan_data['deaths_at_drop_end'],stan_data['observed_deaths'][0,:],color=cmap(norm(drop_df[cov].values)))
        ax.set_xlabel('drop_end_deaths')
        ax.set_ylabel('Deaths per million')

        ax.plot(stan_data['deaths_at_drop_end'],stan_data['reg_deaths'][0,:])
        sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
        sm.set_array([])  # only needed for matplotlib < 3.1
        fig.colorbar(sm)
        ax.set_title(cov)
        fig.tight_layout()
        fig.savefig(outdir+'plots/'+cov+'.png', format='png', dpi=300)
    pdb.set_trace()

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
weeks_to_simulate = args.weeks_to_simulate[0]
outdir = args.outdir[0]

#Read data
stan_data = format_data(drop_df, weeks_to_simulate)
#Analyze deviations from regressed line
for i in range(5):
    drop_df['deviation'+str(i)]=np.array(stan_data['observed_deaths'][i,:]-stan_data['reg_deaths'][i,:])
analyze_deviation(drop_df, stan_data, outdir)
#Simulate
out = simulate(stan_data, stan_model, outdir)
