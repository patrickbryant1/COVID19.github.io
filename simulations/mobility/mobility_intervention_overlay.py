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
parser = argparse.ArgumentParser(description = '''Plot the mobility data for each country in overlay with different NPIs''')

parser.add_argument('--datadir', nargs=1, type= str, default=sys.stdin, help = 'Path to outdir.')
parser.add_argument('--outdir', nargs=1, type= str, default=sys.stdin, help = 'Path to outdir.')



def read_data_and_plot(datadir, countries, geoIds, outdir):
    '''Read in mobility data and dates for NPI and
    generate overlay plots showing the correlation between
    NPIs and mobility patterns.
    '''
    #Covariate names
    covariate_names = ['retail','grocery','transit','work','residential']
    #NPIs
    NPI = ['schools_universities',  'public_events', 'lockdown',
        'social_distancing_encouraged', 'self_isolating_if_ill']
    #Read in intervention dates
    intervention_df = pd.read_csv(datadir+'interventions_only.csv')

    for i in range(len(countries)):
        country = countries[i]
        interventions = 
        geoId = geoIds[i]

        for name in covariate_names:
            country_cov_name = pd.read_csv(datadir+'europe/'+geoId+'-'+name+'.csv')
            country_cov_name['Date'] = pd.to_datetime(country_cov_name['Date'])
            sns.lineplot(x=country_cov_name['Date'], y=np.array(country_cov_name['Change'], dtype=np.float32), label = name)
        for
        plt.axvline(2.8, 0,0.17)
        plt.legend()
        plt.show()


#####MAIN#####
args = parser.parse_args()
datadir = args.datadir[0]
outdir = args.outdir[0]
#Read data
countries = ["Denmark", "Italy", "Germany", "Spain", "United_Kingdom", "France", "Norway", "Belgium", "Austria", "Sweden", "Switzerland"]
geoIds = ["DK","IT","DE","ES","UK","FR","NO", "BE", "AT", "SE", "CH"]
read_data_and_plot(datadir, countries, geoIds, outdir)
