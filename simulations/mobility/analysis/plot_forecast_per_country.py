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
    '''

    for i in range(len(countries)):
        country = countries[i]
        country_data = forecast_df[forecast_df['Country'] == country]
        dates = country_data['Date'].values
        forecast = np.array(country_data['Predicted deaths'].values, dtype=float)
        observed = np.array(country_data['Observed_deaths'].values, dtype=float)
        pdb.set_trace()
        pearsonr(observed, forecast) 
    return None


#####MAIN#####
args = parser.parse_args()
countries = args.countries[0].split(',')
forecast_df = pd.read_csv(args.forecast_csv[0])
outdir = args.outdir[0]
#Visualize
evaluate_forecast(forecast_df, countries, outdir)
