#! /usr/bin/env python3
# -*- coding: utf-8 -*-


import argparse
import sys
import os
import glob
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from scipy.stats import pearsonr
import numpy as np
import seaborn as sns

import pdb



#Arguments for argparse module:
parser = argparse.ArgumentParser(description = '''Obtain all simulated forecasts for all countries in terms of the mean number of deaths for and visualize.''')

parser.add_argument('--forecast_csv', nargs=1, type= str, default=sys.stdin, help = 'Path to csv file with forecast data.')
parser.add_argument('--countries', nargs=1, type= str, default=sys.stdin, help = 'Countries to model (csv).')
parser.add_argument('--outdir', nargs=1, type= str, default=sys.stdin, help = 'Path to outdir.')

def evaluate_forecast(forecast_df, countries, outdir):
    '''Evaluate forecast results per country in terms of the predicted (mean) vs the true number of deaths.
    Predicted mean,Predicted 2.5,Predicted 97.5,Predicted 25,Predicted 75,Observed deaths 
    '''

    xlabels = ['Mar-30','Apr-2', 'Apr-5', 'Apr-8', 'Apr-11']
    for i in range(len(countries)):
        country = countries[i]
        country_data = forecast_df[forecast_df['Country'] == country]
        x = np.arange(0,len(country_data))
        dates = country_data['Date'].values
        pred_mean = np.array(country_data['Predicted mean'].values, dtype=float)
        pred_2_5 = np.array(country_data['Predicted 2.5'].values, dtype=float)
        pred_97_5 = np.array(country_data['Predicted 97.5'].values, dtype=float)
        pred_25 = np.array(country_data['Predicted 25'].values, dtype=float)
        pred_75 = np.array(country_data['Predicted 75'].values, dtype=float)
        observed = np.array(country_data['Observed deaths'].values, dtype=float)
    
        #Plot observed as hist and predicted as line
        fig, ax = plt.subplots(figsize=(6/2.54, 4/2.54))
        ax.bar(x,observed, alpha = 0.5)
        ax.plot(x, pred_mean, alpha=1, color='g', label='One week forecast', linewidth = 3.0)
        ax.fill_between(x, pred_2_5, pred_97_5, color='forestgreen', alpha=0.4)
        ax.fill_between(x, pred_25, pred_75, color='forestgreen', alpha=0.6)

        #Plot week separators
        for w in np.arange(6.5,len(x)-1,7):
            ax.axvline(w, linestyle='--', linewidth=1, c= 'k')

        #Format
        xticks=np.arange(0,len(country_data),3)
        ax.set_ylabel('Deaths per day')
        ax.set_xticks(xticks)
        ax.set_xticklabels(xlabels,rotation='vertical')
        ax.set_title(country)
        ax.spines['right'].set_visible(False)
        ax.spines['top'].set_visible(False)
        fig.tight_layout()
        fig.savefig(outdir+country+'_forecast.png', format = 'png')
        plt.close()
    return None


#####MAIN#####
args = parser.parse_args()
countries = args.countries[0].split(',')
forecast_df = pd.read_csv(args.forecast_csv[0])
outdir = args.outdir[0]
#Visualize
#Set font size
matplotlib.rcParams.update({'font.size': 8})
evaluate_forecast(forecast_df, countries, outdir)
