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
parser = argparse.ArgumentParser(description = '''Simulate using google mobility data and most of the ICL response team model''')

parser.add_argument('--complete_df', nargs=1, type= str, default=sys.stdin, help = 'Path to all input data.')
parser.add_argument('--modelling_results', nargs=1, type= str, default=sys.stdin, help = 'Path to stan model results.')
parser.add_argument('--outdir', nargs=1, type= str, default=sys.stdin, help = 'Path to outdir.')

###FUNCTIONS###
def calculate_diff(complete_df,modelling_results):
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
    #Loop through states
    for i in range(len(states)):
        state_data = complete_df[complete_df['region']==state]
        extreme_indices = [] #Save the indices for the most extreme mobility changes
        #Add covariate data
        for name in covariate_names:
            cov_i = np.array(state_data[name])
            if name == 'residential_percent_change_from_baseline':
                extreme_val = max(cov_i[:N])
            else:
                extreme_val = min(cov_i[:N])
            #Get index
            extreme_index = np.where(cov_i[:N]==extreme_val)[0][0]#Get index for extreme val


        #Use the latest extreme index to fetch R



#####MAIN#####
args = parser.parse_args()
complete_df = pd.read_csv(args.complete_df[0])
modelling_results = pd.read_csv(args.modelling_results[0])
outdir = args.outdir[0]
