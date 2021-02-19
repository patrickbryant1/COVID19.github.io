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
from scipy.stats import spearmanr
import pdb



#Arguments for argparse module:
parser = argparse.ArgumentParser(description = '''Analyze the effect of population differences on county death tolls. ''')
parser.add_argument('--case_data', nargs=1, type= str, default=sys.stdin, help = 'Path to case data (csv).')
parser.add_argument('--death_data', nargs=1, type= str, default=sys.stdin, help = 'Path to death data (csv).')
parser.add_argument('--sex_eth_age_data', nargs=1, type= str, default=sys.stdin, help = 'Path to data with sex age and ethnicity per county.')
parser.add_argument('--people', nargs=1, type= str, default=sys.stdin, help = 'Path to data with people data, including e.g. education, per county.')
parser.add_argument('--income', nargs=1, type= str, default=sys.stdin, help = 'Path to data with income data per county.')
parser.add_argument('--jobs', nargs=1, type= str, default=sys.stdin, help = 'Path to data with job data per county.')
parser.add_argument('--health_insurance', nargs=1, type= str, default=sys.stdin, help = 'Path to health insurance data per county.')
parser.add_argument('--life_expectancy', nargs=1, type= str, default=sys.stdin, help = 'Path to life expectancy data per county.')
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

def format_health_insurance(health_insurance):
    '''Format the health insurance data
    '''
    #PCTUI - Percent uninsured in demographic group for <income category>
    #iprcat = income category
    age_cats = {0:'Under 65 years',1:'18-64 years',2:'40-64 years',
                3:'50-64 years',4:'Under 19 years',5:'21-64 years'} #Under 19 only exists for both sexes
    sex_cats = {0:'Both sexes',1:'Male',2:'Female'}
    income_cats = {0:'All income levels',1:'At or below 200% of poverty',
    2:'At or below 250% of poverty',3:'At or below 138% of poverty',
    4:'At or below 400% of poverty',5:'Between 138-400% of poverty'}

    extracted_data = pd.DataFrame()
    extracted_data['stateFIPS']=''
    extracted_data['county_name']=''
    extracted_data['countyFIPS']=''
    for age in age_cats:
        for sex in sex_cats:
            #Under 19 only exists for both sexes
            if age == 4 and sex !=0:
                continue
            for income in income_cats:
                extracted_data['PCTUI '+age_cats[age]+' '+sex_cats[sex]+' '+income_cats[income]]=''

    states = health_insurance['statefips'].unique()
    for state in states:
        state_data = health_insurance[health_insurance['statefips']==state]
        counties = state_data['county_name'].unique()
        for county in counties:
            vals = [] #Save data
            vals.append(state)
            vals.append(county.strip())

            if county.strip() == '':#whole state
                continue
            county_data = state_data[state_data['county_name']==county]
            vals.append(county_data['countyfips'].values[0])
            if len(county_data['racecat'].unique())>1:
                pdb.set_trace()

            #Loop through all sexes and income categories to fetch the percent uninsured
            for age in age_cats:
                county_age_data = county_data[county_data['agecat']==age]
                for sex in sex_cats:
                    #Under 19 only exists for both sexes
                    if age == 4 and sex !=0:
                        continue
                    county_age_sex_data = county_age_data[county_age_data['sexcat']==sex]
                    if len(county_age_sex_data)<1:
                        pdb.set_trace()
                    for income in income_cats:
                        county_age_sex_income_data = county_age_sex_data[county_age_sex_data['iprcat']==income]
                        if len(county_age_sex_income_data)<1:
                            pdb.set_trace()
                        #There is missing data
                        try:
                            vals.append(float(county_age_sex_income_data['PCTUI'].values[0]))
                        except:
                            vals.append(np.nan)


            #Add to extracted data
            slice = pd.DataFrame([vals],columns=extracted_data.columns)
            extracted_data=pd.concat([extracted_data,slice])

    #Save df
    extracted_data.to_csv('formatted_health_insurance_data_per_county.csv')
    return extracted_data

def format_life_expectancy(life_expectancy):
    '''Format the life expectancy data per county
    Life expectancy per age group, e(x)
    '''

    age_groups = life_expectancy['Age Group'].unique()

    extracted_data = pd.DataFrame()
    extracted_data['stateFIPS']=0
    extracted_data['countyFIPS']=0

    for age in age_groups:
        extracted_data['Life expectancy '+age]=0

    states = life_expectancy['STATE2KX'].unique()
    for state in states:
        state_data = life_expectancy[life_expectancy['STATE2KX']==state]
        counties = state_data['CNTY2KX'].unique()
        for county in counties:
            vals = [] #save data
            vals.append(state)
            vals.append(county)
            county_data = state_data[state_data['CNTY2KX']==county]
            for age in age_groups:
                county_age_data = county_data[county_data['Age Group']==age]
                vals.append(np.average(county_age_data['e(x)']))

            #Add to extracted data
            slice = pd.DataFrame([vals],columns=extracted_data.columns)
            extracted_data=pd.concat([extracted_data,slice])

    #Save df
    extracted_data.to_csv('formatted_life_expectancy_data_per_county.csv')

    return extracted_data

def corr_feature_with_death(complete_df, outdir):
    '''Investigate the correlation of different features with the deaths
    '''
    print('Before NaN removal', len(complete_df))
    #Remove NaNs
    complete_df = complete_df.dropna()
    print('After NaN removal', len(complete_df))
    y = np.array(complete_df['Death rate per individual'])
    #'Cumulative cases'
    data = complete_df.drop(['FIPS','Death rate per individual','Death rate per confirmed case','Death rate per confirmed case,individual','Cumulative deaths','Cumulative cases','Case rate per individual'],axis=1)
    X = np.array(data[data.columns[3:]])

    corr = []
    pvals = []
    for i in range(X.shape[1]):
        try:
            R,p = spearmanr(X[:,i],y)
        except:
            pdb.set_trace()
        corr.append(R)
        pvals.append(p)

    #Visualize
    corr_df = pd.DataFrame()
    corr_df['Feature'] = data.columns[3:]
    corr_df['Spearman R'] = np.array(corr)
    corr_df['p-value'] = np.array(pvals)
    #Bonferroni correction
    corr_df = corr_df[corr_df['p-value']<(0.05/X.shape[1])]
    corr_df=corr_df.sort_values(by='Spearman R',ascending=False)
    #All
    fig, ax = plt.subplots(figsize=(18/2.54,150/2.54))
    sns.barplot(x="Spearman R", y="Feature", data=corr_df)
    fig.tight_layout()
    fig.savefig(outdir+'feature_correlations.png', format='png')
    plt.close()
    #top and bottom 10
    fig, ax = plt.subplots(figsize=(12/2.54,12/2.54))
    corr_df = corr_df.reset_index()
    top10 = corr_df.loc[0:9]
    bottom10 = corr_df.loc[len(corr_df)-10:len(corr_df)]
    top_bottom = pd.concat([top10,bottom10])
    sns.barplot(x="Spearman R", y="Feature", data=top_bottom)
    fig.tight_layout()
    fig.savefig(outdir+'top_bottom_feature_correlations.png', format='png')
    plt.close()
    #Save significant features
    corr_df.to_csv('sig_feature_corr.csv')
    pdb.set_trace()


#####MAIN#####
args = parser.parse_args()
case_data = pd.read_csv(args.case_data[0])
death_data = pd.read_csv(args.death_data[0])
#The sex_eth_age_data conatins only 1877 counties of the over 3000 in total
sex_eth_age_data = pd.read_csv(args.sex_eth_age_data[0])
people = pd.read_csv(args.people[0])
income = pd.read_csv(args.income[0])
jobs = pd.read_csv(args.jobs[0])
health_insurance = pd.read_csv(args.health_insurance[0])
life_expectancy = pd.read_csv(args.life_expectancy[0])
#Make sure only YEAR=12 (2019):
sex_eth_age_data = sex_eth_age_data[sex_eth_age_data['YEAR']==12]
outdir = args.outdir[0]
try:
   sex_eth_age_data = pd.read_csv('formatted_eth_age_data_per_county.csv')
except:
   sex_eth_age_data = format_age_per_ethnicity(sex_eth_age_data)

#Format health_insurance
try:
    health_insurance = pd.read_csv('formatted_health_insurance_data_per_county.csv')
except:
    health_insurance = format_health_insurance(health_insurance)

#Format life expectancy
try:
    life_expectancy = pd.read_csv('formatted_life_expectancy_data_per_county.csv')
except:
    life_expectancy = format_life_expectancy(life_expectancy)
#Get cumulative cases and deaths
epidemic_data = cumulative_cases_deaths(case_data,death_data)
#Rename column for merge
epidemic_data = epidemic_data.rename(columns={'County Name':'County'})
epidemic_data = epidemic_data.drop(['State'],axis=1)
#Merge epidemic data with sex_eth_age_data
complete_df = pd.merge(sex_eth_age_data, epidemic_data, left_on=['State','County'], right_on=['stateFIPS','County'], how='left')

#Merge with health_insurance
complete_df = pd.merge(complete_df, health_insurance, left_on=['State','County'], right_on=['stateFIPS','county_name'], how='inner')
complete_df = complete_df.rename(columns={'countyFIPS_x':'FIPS','countyFIPS_y':'countyFIPS'})

#Merge with life life_expectancy
complete_df = pd.merge(complete_df, life_expectancy, left_on=['State','countyFIPS'], right_on=['stateFIPS','countyFIPS'], how='inner')

#Join all on FIPS
#Remove county to avoid duplicates
people = people.drop(['State','County'],axis=1)
complete_df = pd.merge(complete_df, people, on=['FIPS'], how='inner')
#Remove state and county to avoid duplicates
income = income.drop(['State', 'County'],axis=1)
jobs = jobs.drop(['State', 'County'],axis=1)
complete_df = pd.merge(complete_df, income, on=['FIPS'], how='inner')
complete_df = pd.merge(complete_df, jobs, on=['FIPS'], how='inner')
#Get death rate per total county pop
complete_df['Death rate per individual'] = (complete_df['Cumulative deaths']/complete_df['County total'])
complete_df['Case rate per individual'] = (complete_df['Cumulative cases']/complete_df['County total'])
complete_df['Death rate per confirmed case,individual'] = (complete_df['Cumulative deaths']/complete_df['County total'])/complete_df['Cumulative cases']
complete_df['Death rate per confirmed case'] = (complete_df['Cumulative deaths']/complete_df['Cumulative cases'])

#Drop unwanted columns
complete_df = complete_df.drop(['stateFIPS','stateFIPS_x','stateFIPS_y', 'Unnamed: 0_y', 'county_name','Unnamed: 0'],axis=1)
#Save df
complete_df.to_csv('complete_df.csv')
print('Merged')
#Analyze correlations
corr_feature_with_death(complete_df, outdir)
