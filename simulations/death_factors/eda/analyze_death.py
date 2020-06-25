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
parser = argparse.ArgumentParser(description = '''Analyze the effect of population differences on state death tolls. ''')
parser.add_argument('--epidemic_data', nargs=1, type= str, default=sys.stdin, help = 'Path to eidemic data (csv).')
parser.add_argument('--comorbidity_data', nargs=1, type= str, default=sys.stdin, help = 'Path to comorbidity data (csv).')
parser.add_argument('--outdir', nargs=1, type= str, default=sys.stdin, help = 'Path to outdir.')

###FUNCTIONS###
def vis_states(epidemic_data, comorbidity_data, outdir):
    '''Plot the deaths per state and feature
    '''

    states = epidemic_data['State'].unique()
    for state in states:
        fig, ax = plt.subplots(figsize=(18/2.54, 12/2.54))
        state_data = epidemic_data[epidemic_data['State']==state]
        ethnicities = state_data['Race and Hispanic Origin Group'].unique()
        age_groups = state_data['Age group'].unique()
        for ethnicity in ethnicities:
            eth_state_data = state_data[state_data['Race and Hispanic Origin Group']==ethnicity]
            ax.bar(eth_state_data['Age group'], eth_state_data['COVID-19 Deaths'],label=ethnicity)
        plt.xticks(rotation='vertical')
        plt.legend()
        ax.set_title(state)
        fig.tight_layout()
        fig.savefig(outdir+state.replace(" ", "_")+'.png', format='png')
        plt.close()


    
#####MAIN#####
#Set font size
args = parser.parse_args()
epidemic_data = pd.read_csv(args.epidemic_data[0])
comorbidity_data = pd.read_csv(args.comorbidity_data[0])
outdir = args.outdir[0]
vis_states(epidemic_data, comorbidity_data, outdir)
