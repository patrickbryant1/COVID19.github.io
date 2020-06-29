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
parser = argparse.ArgumentParser(description = '''Analyze the effect of population differences on county death tolls. ''')
parser.add_argument('--epidemic_data', nargs=1, type= str, default=sys.stdin, help = 'Path to eidemic data (csv).')
parser.add_argument('--sex_eth_age_data', nargs=1, type= str, default=sys.stdin, help = 'Path to data with sex age and ethnicity per state.')
parser.add_argument('--outdir', nargs=1, type= str, default=sys.stdin, help = 'Path to outdir.')

###FUNCTIONS###
def parse_county_demography(sex_eth_age_data):
    '''Data from https://www2.census.gov/programs-surveys/popest/datasets/2010-2019/counties/asrh/
    Here are the keys:
    https://www2.census.gov/programs-surveys/popest/technical-documentation/file-layouts/2010-2018/cc-est2018-alldata.pdf
    I will need the YEAR=12 variable for the 2019 estimate.
    '''

    counties = sex_eth_age_data['CTYNAME'].unique()
    for county in

def format_age_per_ethnicity(sex_eth_age_data):
    '''Extract ethnicity data per state
    Data from https://www2.census.gov/programs-surveys/popest/datasets/2010-2019/counties/asrh/
    Here are the keys:
    https://www2.census.gov/programs-surveys/popest/technical-documentation/file-layouts/2010-2018/cc-est2018-alldata.pdf
    I will need the YEAR=12 variable for the 2019 estimate.
    '''



    extracted_data = pd.DataFrame()
    #Use only total
    sex_eth_age_data = sex_eth_age_data[sex_eth_age_data['SEX']==0]
    origins = {1:'Non-Hispanic',2:'Hispanic'}
    ethnicities = {1:'White', 2:'Black',3:'American Indian or Alaska Native',4:'Asian',5:'Native Hawaiian or Other Pacific Islander',6:'More than one race'}
    #Combining origin 1 and ethnicity gives Non-Hispanic + ethinicity (same used in COVID reportings)
    #AGE is single-year of age (0, 1, 2,... 84, 85+ years)
    age_groups = {0:'Under 1 year',4:'1-4 years',14:'5-14 years',24:'15-24 years',34:'25-34 years',44:'35-44 years',54:'45-54 years', 64:'55-64 years', 74:'65-74 years',84:'75-84 years', 85:'85 years and over'}
    age_index = [1,4,14,24,34,44,54,64,74,84]
    #Assign columns
    extracted_data['County'] = ''
    extracted_data['Ethnicity'] = ''
    extracted_data['TOT_POP'] = '' #Total population in county
    for age in age_groups:
        extracted_data[age_groups[age]] = 0

    #Loop through all counties
    counties = sex_eth_age_data['CTYNAME'].unique()
    for county in counties:
        county_data = sex_eth_age_data[sex_eth_age_data['CTYNAME']==county]
        #Save data
        vals = []
        vals.append(county)
        #Get total county pop
        vals.append(county_data['TOT_POP'])
        #Loop through origins
        hispanic_state = per_state[per_state['ORIGIN']==2]
        vals = []
        vals.append(state)
        vals.append('Hispanic or Latino')
        age_counts = np.zeros(len(age_groups))

        #All the ethnicities in Hispanic should be summed
        for eth in ethnicities:
            hispanic_state_eth = hispanic_state[hispanic_state['RACE']==eth] #All the Hispanic ethnicities will be summed
            hispanic_state_eth = hispanic_state_eth.reset_index()
            #First
            age_counts[0]+=np.sum(hispanic_state_eth.loc[0,'POPESTIMATE2019'])
            for i in range(len(age_index)-1):
                age_counts[i+1]+=np.sum(hispanic_state_eth.loc[age_index[i]:age_index[i+1],'POPESTIMATE2019'])
            #Last
            age_counts[-1]+=np.sum(hispanic_state_eth.loc[85:,'POPESTIMATE2019'])
        vals.extend(age_counts)
        slice = pd.DataFrame([vals],columns=extracted_data.columns)
        extracted_data=pd.concat([extracted_data,slice])

        #All the ethnicities in the non Hispanic should not be summed
        #Loop through origins
        non_hispanic_state = per_state[per_state['ORIGIN']==1]
        #All the ethnicities in Hispanic should be summed
        for eth in ethnicities:
            vals = []
            vals.append(state)
            vals.append('Non-Hispanic '+ethnicities[eth])
            age_counts = np.zeros(len(age_groups))

            non_hispanic_state_eth = non_hispanic_state[non_hispanic_state['RACE']==eth] #All the Hispanic ethnicities will be summed
            non_hispanic_state_eth =non_hispanic_state_eth.reset_index()
            #First
            age_counts[0]+=np.sum(non_hispanic_state_eth.loc[0,'POPESTIMATE2019'])
            for i in range(len(age_index)-1):
                age_counts[i+1]+=np.sum(non_hispanic_state_eth.loc[age_index[i]:age_index[i+1],'POPESTIMATE2019'])
            #Last
            age_counts[-1]+=np.sum(non_hispanic_state_eth.loc[85:,'POPESTIMATE2019'])
            vals.extend(age_counts)
            slice = pd.DataFrame([vals],columns=extracted_data.columns)
            extracted_data=pd.concat([extracted_data,slice])

    #Save df
    extracted_data.to_csv('formatted_eth_age_data_per_state.csv')
    return extracted_data

def vis_states(epidemic_data, eth_age_data_per_state, outdir):
    '''Plot the deaths per state and feature
    '''
    #Handle nans
    epidemic_data = epidemic_data.fillna(0)
    states = eth_age_data_per_state['State'].unique()
    for state in states:
        fig, ax = plt.subplots(figsize=(18/2.54, 12/2.54))
        epi_state_data = epidemic_data[epidemic_data['State']==state]
        eth_age_state_data = eth_age_data_per_state[eth_age_data_per_state['State']==state]
        ethnicities = epi_state_data['Race and Hispanic Origin Group'].unique()[:-1]
        age_groups = epi_state_data['Age group'].unique()
        prev=np.zeros(len(age_groups))
        for ethnicity in ethnicities:

            eth_state_data = epi_state_data[epi_state_data['Race and Hispanic Origin Group']==ethnicity]
            #Normalize the deaths with the population distribution per ethnicity
            norm_vals = eth_age_state_data[eth_age_state_data['Ethnicity']==ethnicity]
            if ethnicity=='Unknown':
                continue
            else:
                normalized = (eth_state_data['COVID-19 Deaths'].values/norm_vals[eth_state_data['Age group']].values)[0]
                normalized = normalized*100

            if np.sum(prev)<1:
                ax.bar(eth_state_data['Age group'],normalized,bottom = prev, label=ethnicity)
            else:
                ax.bar(eth_state_data['Age group'], normalized, bottom = prev, label=ethnicity)
            prev += normalized


        plt.xticks(rotation='vertical')
        plt.legend()
        ax.set_title(state)
        ax.set_ylabel('Death % per ethnicity')
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
sex_eth_age_data = pd.read_csv(args.sex_eth_age_data[0])
#Make sure only YEAR=12 (2019):
sex_eth_age_data = sex_eth_age_data[sex_eth_age_data['YEAR']==12]
outdir = args.outdir[0]


vis_states(epidemic_data, eth_age_data_per_state, outdir)
#vis_comorbidity(comorbidity_data, comorbidity_data['Condition'].unique()[:1], outdir+'comorbidity/comorbidity1.png')
#vis_comorbidity(comorbidity_data, comorbidity_data['Condition'].unique()[1:], outdir+'comorbidity/comorbidity2.png')
