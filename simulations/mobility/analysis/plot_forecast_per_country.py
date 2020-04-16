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
    '''Evaluate forecast results per country in terms of the icumulative predicted (mean) vs the true number of cumulative deaths.
    ,Country,Date,Predicted mean,Predicted 2.5,Predicted 97.5,Predicted 25,Predicted 75,Observed deaths, End date 
    '''

    xlabels = ['30 Mar','2 Apr', '5 Apr', '8 Apr', '11 Apr']
    pred_start = np.datetime64('2020-03-30')
    for i in range(len(countries)):
        country = countries[i]
        country_data = forecast_df[forecast_df['Country'] == country]
        end_dates = country_data['End date'].unique() #Get unique end dates
        #Store predictions
        pred_mean = []
        pred_2_5 = []
        pred_97_5 = []
        pred_25 = []
        pred_75 = []
        observed = []
        for ed in end_dates:
            country_ed_data = country_data[country_data['End date']==ed]
            pred_mean.extend([*np.array(country_ed_data['Predicted mean'].values, dtype=float)[-7:]])
            pred_2_5.extend([*np.array(country_ed_data['Predicted 2.5'].values, dtype=float)[-7:]])
            pred_97_5.extend([*np.array(country_ed_data['Predicted 97.5'].values, dtype=float)[-7:]])
            pred_25.extend([*np.array(country_ed_data['Predicted 25'].values, dtype=float)[-7:]])
            pred_75.extend([*np.array(country_ed_data['Predicted 75'].values, dtype=float)[-7:]])
            observed.extend([*np.array(country_ed_data['Observed deaths'].values, dtype=float)[-7:]])
        #Get prediction indices
        #pred_index = np.where(dates>=pred_start)
        #Plot observed as hist and predicted as line
        x = np.arange(0,len(pred_mean))
        fig, ax = plt.subplots(figsize=(6/2.54, 4/2.54))
        ax.bar(x,observed, alpha = 0.5)
        ax.plot(x, pred_mean, alpha=1, color='g', label='One week forecast', linewidth = 1.0)
        ax.fill_between(x, pred_2_5, pred_97_5, color='forestgreen', alpha=0.4)
        ax.fill_between(x, pred_25, pred_75, color='forestgreen', alpha=0.6)
        #Plot week separators
        for w in np.arange(6.5,len(x)-1,7):
            ax.axvline(w, linestyle='--', linewidth=1, c= 'k')

        #Format
        xticks=np.arange(0,len(x),3)
        ax.set_ylabel('Cumulative deaths')
        ax.set_xticks(xticks)
        ax.set_xticklabels(xlabels,rotation='vertical')
        ax.set_title(country)
        ax.spines['right'].set_visible(False)
        ax.spines['top'].set_visible(False)
        fig.tight_layout()
        fig.savefig(outdir+country+'_forecast.png', format = 'png')
        plt.close()

        #Analysis of correspondence
        av_er = [] #Average absolute error per week
        perc_er = [] #Average absolute percent error per week
        for c in range(0,len(pred_mean), 7):
            abs_er = np.absolute(np.array(pred_mean[c:c+7])-np.array(observed[c:c+7]))
            av_er.append(np.average(abs_er))
            perc_er.append(np.average(abs_er/np.array(observed[c:c+7])))
        print(country, av_er[0], av_er[1], perc_er[0], perc_er[1])
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
