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
parser.add_argument('--sex_eth_age_data', nargs=1, type= str, default=sys.stdin, help = 'Path to data with sex age and ethnicity per state (csv).')
parser.add_argument('--outdir', nargs=1, type= str, default=sys.stdin, help = 'Path to outdir.')

###FUNCTIONS###
def format_ethnicity(sex_eth_age_data):
    '''Extract ethnicity data per state
    '''
    extracted_data = pd.DataFrame()
    sexes = {0:'Total', 1:'Male', 2:'Female'}
    origins = {1:'Non-Hispanic',2:'Hispanic'}
    ethnicities = {1:'White', 2:'Black',3:'American Indian or Alaska Native',4:'Asian',5:'Native Hawaiian and Other Pacific Islander',6:'More than one race'}
    #Combining origin 1 and ethnicity gives Non-Hispanic + ethinicity (same used in COVID reportings)
    #AGE is single-year of age (0, 1, 2,... 84, 85+ years)
    age_groups = {0:'Under 1 year',4:'1-4 years',14:'5-14 years',24:'15-24 years',34:'25-34 years',44:'35-44 years',54:'45-54 years', 64:'55-64 yeaers', 74:'65-74 years',84:'75-84 years'}
    #Assign columns
    extracted_data['State'] = ''
    extracted_data['Ethnicity'] = ''
    for age in age_groups:
        extracted_data[age_groups[age]] = 0

    for state in sex_eth_age_data['NAME'].unique():
        per_state = sex_eth_age_data[sex_eth_age_data['NAME']==state]
        #Loop through origins
        hispanic_state = per_state[per_state['ORIGIN']==2]
        for eth in ethnicities:
            hispanic_state_eth = hispanic_state[hispanic_state['RACE']==eth] #All the Hispanic ethnicities will be summed
            hispanic_state_eth = hispanic_state.reset_index()
            for age in age_groups:
                hispanic_state_eth_age = np.sum(hispanic_state_eth.loc[age,'POPESTIMATE2019'])
                pdb.set_trace()
def vis_states(epidemic_data, outdir):
    '''Plot the deaths per state and feature
    '''

    states = epidemic_data['State'].unique()
    for state in states:
        fig, ax = plt.subplots(figsize=(18/2.54, 12/2.54))
        state_data = epidemic_data[epidemic_data['State']==state]
        ethnicities = state_data['Race and Hispanic Origin Group'].unique()
        age_groups = state_data['Age group'].unique()
        prev=np.zeros(len(age_groups))
        for ethnicity in ethnicities:
            eth_state_data = state_data[state_data['Race and Hispanic Origin Group']==ethnicity]
            if np.sum(prev)<1:
                ax.bar(eth_state_data['Age group'], eth_state_data['COVID-19 Deaths'], label=ethnicity)
            else:
                ax.bar(eth_state_data['Age group'], eth_state_data['COVID-19 Deaths'],bottom = prev, label=ethnicity)
            prev += eth_state_data['COVID-19 Deaths']
        plt.xticks(rotation='vertical')
        plt.legend()
        ax.set_title(state)
        ax.set_ylabel('Deaths')
        fig.tight_layout()
        fig.savefig(outdir+state.replace(" ", "_")+'.png', format='png')
        plt.close()

def vis_comorbidity(comorbidity_data, conditions, outname):
    '''Visualize the covid comorbidity
    '''
    fig, ax = plt.subplots(figsize=(27/2.54, 18/2.54))
    cols = ['0-24 years', '25-34 years', '35-44 years',
       '45-54 years', '55-64 years', '65-74 years', '75-84 years',
       '85 years and over']

    prev=np.zeros(len(cols))
    for condition in conditions:
        condition_data = comorbidity_data[comorbidity_data['Condition']==condition]
        if np.sum(prev)<1:
            ax.bar(cols,np.array(condition_data[cols])[0], label=condition)
        else:
            ax.bar(cols,np.array(condition_data[cols])[0], bottom = prev, label=condition)
        prev+=np.array(condition_data[cols])[0]
        print(prev)

    plt.xticks(rotation='vertical')
    plt.legend()
    ax.set_title('Comorbidity')
    ax.set_ylabel('Deaths')
    fig.tight_layout()
    fig.savefig(outname, format='png')
    plt.close()


#####MAIN#####
#Set font size
args = parser.parse_args()
epidemic_data = pd.read_csv(args.epidemic_data[0])
comorbidity_data = pd.read_csv(args.comorbidity_data[0])
sex_eth_age_data = pd.read_csv(args.sex_eth_age_data[0])
outdir = args.outdir[0]
#vis_states(epidemic_data, outdir)
#vis_comorbidity(comorbidity_data, comorbidity_data['Condition'].unique()[:1], outdir+'comorbidity/comorbidity1.png')
#vis_comorbidity(comorbidity_data, comorbidity_data['Condition'].unique()[1:], outdir+'comorbidity/comorbidity2.png')
format_ethnicity(sex_eth_age_data)
