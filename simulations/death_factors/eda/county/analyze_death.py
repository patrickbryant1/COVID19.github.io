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
parser.add_argument('--sex_eth_age_data', nargs=1, type= str, default=sys.stdin, help = 'Path to data with sex age and ethnicity per county.')
parser.add_argument('--people', nargs=1, type= str, default=sys.stdin, help = 'Path to data with people data, including e.g. education, per county.')
parser.add_argument('--income', nargs=1, type= str, default=sys.stdin, help = 'Path to data with income data per county.')
parser.add_argument('--jobs', nargs=1, type= str, default=sys.stdin, help = 'Path to data with job data per county.')

parser.add_argument('--outdir', nargs=1, type= str, default=sys.stdin, help = 'Path to outdir.')

###FUNCTIONS###
def format_age_per_ethnicity(sex_eth_age_data):
    '''Extract ethnicity data per state
    Data from https://www2.census.gov/programs-surveys/popest/datasets/2010-2019/counties/asrh/
    Here are the keys:
    https://www2.census.gov/programs-surveys/popest/technical-documentation/file-layouts/2010-2018/cc-est2018-alldata.pdf
    I will need the YEAR=12 variable for the 2019 estimate.
    '''



    extracted_data = pd.DataFrame()
    sexes = ['MALE','FEMALE']
    ethnicities = {'WA':'White', 'BA':'Black','IA':'American Indian or Alaska Native',
    'AA':'Asian','NA':'Native Hawaiian or Other Pacific Islander','TOM':'More than one race',
    'H':'Hispanic'}
    #Combining origin 1 and ethnicity gives Non-Hispanic + ethinicity (same used in COVID reportings)
    #AGE is single-year of age (0, 1, 2,... 84, 85+ years)
    age_groups = {0:'Total for ethnicity',1:'0-4 years',2:'5-9 years',3:'10-14 years',4:'15-19 years',
    5:'20-24 years',6:'25-29 years', 7:'30-34 years', 8:'35-39 years',9:'40-44 years',
    10:'45 -49 years', 11:'50-54 years', 12:'55-59 years', 13:'60-64 years',14:'65-69 years',
    15:'70-74 years', 16:'75-79 years', 17:'80-84 years',18:'85 years and over'}

    #Assign columns
    extracted_data['County'] = ''
    extracted_data['Ethnicity'] = ''
    extracted_data['County total'] = '' #Total population in county
    for age in age_groups:
        extracted_data[age_groups[age]] = 0

    #Loop through all counties
    counties = sex_eth_age_data['CTYNAME'].unique()
    for county in counties:
        county_data = sex_eth_age_data[sex_eth_age_data['CTYNAME']==county]
        #Reset index
        county_data = county_data.reset_index()
        #Get total county pop
        tot_county_pop = np.sum(county_data['TOT_POP'])
        #All the ethnicities
        for eth in ethnicities:
            #Save data
            vals = []
            vals.append(county)
            vals.append(ethnicities[eth])
            vals.append(tot_county_pop)
            age_fracs = np.zeros(len(age_groups))
            for sex in sexes:
                for i in range(len(age_groups)):
                    age_fracs[i]+=np.sum(county_data.loc[i,eth+'_'+sex])
            vals.extend(age_fracs/tot_county_pop)#Normalize with the total county pop
            slice = pd.DataFrame([vals],columns=extracted_data.columns)
            extracted_data=pd.concat([extracted_data,slice])

    #Save df
    extracted_data.to_csv('formatted_eth_age_data_per_county.csv')
    return extracted_data

def sum_deaths(epidemic_data):
    '''Get a death total over all dates
    '''

    epidemic_data['cumulative deaths'] = 0
    for i in range(len(epidemic_data)):
        epidemic_data.loc[i, 'cumulative deaths'] = np.sum(epidemic_data.iloc[i,4:-1])

    index = np.arange(4,len(epidemic_data.columns)-1)
    epidemic_data = epidemic_data.drop(epidemic_data.columns[index],axis=1)
    return epidemic_data

def get_county_variables(jobs,income):
    '''
    Should get income a few years back. The historical income will surely affect the current status.
    Average over the last 10 years as well as having the current median.
    E.g. the employment rate in Autauga has dropped from 8.9 to 3.6 between 2010 and 2018.
    '''
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
try:
    sex_eth_age_data = pd.read_csv('formatted_eth_age_data_per_county.csv')
except:
    sex_eth_age_data = format_age_per_ethnicity(sex_eth_age_data)

#Sum deaths
epidemic_data = sum_deaths(epidemic_data)
#Rename column for merge
epidemic_data = epidemic_data.rename(columns={'County Name':'County'})
#Merge epidemic data with sex_eth_age_data
complete_df = pd.merge(sex_eth_age_data, epidemic_data, on=['County'], how='left')
pdb.set_trace()
vis_states(epidemic_data, eth_age_data_per_state, outdir)
#vis_comorbidity(comorbidity_data, comorbidity_data['Condition'].unique()[:1], outdir+'comorbidity/comorbidity1.png')
#vis_comorbidity(comorbidity_data, comorbidity_data['Condition'].unique()[1:], outdir+'comorbidity/comorbidity2.png')
