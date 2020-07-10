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
from scipy.stats import pearsonr
import pdb



#Arguments for argparse module:
parser = argparse.ArgumentParser(description = '''Analyze the effect of population differences on county death tolls. ''')
parser.add_argument('--county_deaths', nargs=1, type= str, default=sys.stdin, help = 'Path to deaths per county (csv).')
parser.add_argument('--state_deaths', nargs=1, type= str, default=sys.stdin, help = 'Path to deaths per state (csv).')
parser.add_argument('--people', nargs=1, type= str, default=sys.stdin, help = 'Path to data with people data, including e.g. education, per county.')
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
    age_groups = {0:'total',1:'0-4 years',2:'5-9 years',3:'10-14 years',4:'15-19 years',
    5:'20-24 years',6:'25-29 years', 7:'30-34 years', 8:'35-39 years',9:'40-44 years',
    10:'45-49 years', 11:'50-54 years', 12:'55-59 years', 13:'60-64 years',14:'65-69 years',
    15:'70-74 years', 16:'75-79 years', 17:'80-84 years',18:'85 years and over'}

    #Assign columns
    extracted_data['State'] = ''
    extracted_data['County'] = ''
    extracted_data['County total'] = '' #Total population in county
    for eth in ethnicities:
        for age in age_groups:
            extracted_data[ethnicities[eth]+' '+age_groups[age]] = 0

    #Loop through all counties
    #NOTE!!!!!!!!!!!
    #Several states have counties named the same thing.
    #It is therefore necessary to get the county and state at the same time
    states = sex_eth_age_data['STATE'].unique()
    for state in states:
        state_data = sex_eth_age_data[sex_eth_age_data['STATE']==state]
        counties = state_data['CTYNAME'].unique()
        for county in counties:
            county_data = state_data[state_data['CTYNAME']==county]
            #Reset index
            county_data = county_data.reset_index()
            #Get total county pop
            tot_county_pop = county_data.loc[0,'TOT_POP'] #index 0 is the total
            #Save data
            vals = []
            vals.append(state)
            vals.append(county)
            vals.append(tot_county_pop)
            age_fracs = []
            #All the ethnicities
            for eth in ethnicities:
                age_fracs_eth = np.zeros(len(age_groups))
                #Both sexes to get total
                for sex in sexes:
                    for i in range(len(age_groups)):
                        age_fracs_eth[i]+=np.sum(county_data.loc[i,eth+'_'+sex])
                age_fracs.extend(age_fracs_eth)
            vals.extend(np.array(age_fracs)/tot_county_pop)#Normalize with the total county pop
            slice = pd.DataFrame([vals],columns=extracted_data.columns)
            extracted_data=pd.concat([extracted_data,slice])
    #Save df
    extracted_data.to_csv('formatted_eth_age_data_per_county.csv')
    return extracted_data

def cumulative_cases_deaths(case_data,death_data):
    '''Get case and death totals over all dates
    '''

    epidemic_data = pd.DataFrame()
    #Add county identifiers
    epidemic_data[death_data.columns[0:4]] = death_data[death_data.columns[0:4]]
    #Add cases
    epidemic_data['Cumulative cases'] = case_data['6/27/20']
    #Add deaths
    epidemic_data['Cumulative deaths'] = death_data['6/27/2020']

    return epidemic_data


#####MAIN#####
args = parser.parse_args()
county_deaths = pd.read_csv(args.county_deaths[0])
state_deaths = pd.read_csv(args.state_deaths[0])
people = pd.read_csv(args.people[0], encoding='latin-1')
outdir = args.outdir[0]

pdb.set_trace()


#Merge epidemic data with sex_eth_age_data
#complete_df = pd.merge(sex_eth_age_data, epidemic_data, left_on=['State','County'], right_on=['stateFIPS','County'], how='left')
