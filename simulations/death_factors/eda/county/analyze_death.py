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

def sum_deaths(epidemic_data):
    '''Get a death total over all dates
    '''

    epidemic_data['Cumulative deaths'] = 0
    for i in range(len(epidemic_data)):
        epidemic_data.loc[i, 'Cumulative deaths'] = np.sum(epidemic_data.iloc[i,4:-1])
    #Remove unwanted columns
    index = np.arange(4,len(epidemic_data.columns)-1)
    epidemic_data = epidemic_data.drop(epidemic_data.columns[index],axis=1)
    return epidemic_data

def get_county_variables(people,income,jobs):
    '''
    Should get income a few years back. The historical income will surely affect the current status.
    Average over the last 10 years as well as having the current median.
    E.g. the employment rate in Autauga has dropped from 8.9 to 3.6 between 2010 and 2018.
    '''

    people_cols = ['FIPS', 'State', 'County', 'PopChangeRate1718', 'PopChangeRate1018',
       'TotalPopEst2018', 'NetMigrationRate1018', 'NaturalChangeRate1018',
       'Net_International_Migration_Rate_2010_2018', 'PopChangeRate0010',
       'NetMigrationRate0010', 'NaturalChangeRate0010',
       'Immigration_Rate_2000_2010', 'PopDensity2010', 'Under18Pct2010',
       'Age65AndOlderPct2010', 'WhiteNonHispanicPct2010',
       'BlackNonHispanicPct2010', 'AsianNonHispanicPct2010',
       'NativeAmericanNonHispanicPct2010', 'HispanicPct2010',
       'MultipleRacePct2010', 'NonHispanicWhitePopChangeRate0010',
       'NonHispanicBlackPopChangeRate0010',
       'NonHispanicAsianPopChangeRate0010',
       'NonHispanicNativeAmericanPopChangeRate0010',
       'HispanicPopChangeRate0010', 'MultipleRacePopChangeRate0010',
       'WhiteNonHispanicNum2010', 'BlackNonHispanicNum2010',
       'AsianNonHispanicNum2010', 'NativeAmericanNonHispanicNum2010',
       'HispanicNum2010', 'MultipleRaceNum2010', 'ForeignBornPct',
       'ForeignBornEuropePct', 'ForeignBornMexPct', 'NonEnglishHHPct',
       'Ed1LessThanHSPct', 'Ed2HSDiplomaOnlyPct', 'Ed3SomeCollegePct',
       'Ed4AssocDegreePct', 'Ed5CollegePlusPct', 'AvgHHSize', 'FemaleHHPct',
       'HH65PlusAlonePct', 'OwnHomePct', 'Ed5CollegePlusNum',
       'Ed3SomeCollegeNum', 'Ed2HSDiplomaOnlyNum', 'Ed1LessThanHSNum',
       'TotalPop25Plus', 'ForeignBornAfricaPct', 'TotalPopACS', 'TotalOccHU',
       'ForeignBornAsiaPct', 'Ed4AssocDegreeNum', 'ForeignBornNum',
       'HH65PlusAloneNum', 'OwnHomeNum', 'FemaleHHNum', 'TotalHH',
       'NonEnglishHHNum', 'ForeignBornCentralSouthAmPct',
       'ForeignBornCentralSouthAmNum', 'ForeignBornCaribPct',
       'ForeignBornCaribNum', 'ForeignBornAfricaNum', 'ForeignBornAsiaNum',
       'ForeignBornMexNum', 'ForeignBornEuropeNum', 'Age65AndOlderNum2010',
       'TotalPop2010', 'LandAreaSQMiles2010', 'Under18Num2010',
       'Net_International_Migration_2000_2010', 'NaturalChangeNum0010',
       'NetMigrationNum0010', 'TotalPopEst2012', 'TotalPopEst2013',
       'TotalPopEst2010', 'TotalPopEst2014', 'TotalPopEst2011',
       'Net_International_Migration_2010_2018', 'NaturalChange1018',
       'TotalPopEst2015', 'TotalPopEst2016', 'TotalPopEst2017',
       'NetMigration1018', 'TotalPopEstBase2010']

    income_cols = ['FIPS', 'State', 'County', 'MedHHInc', 'PerCapitaInc',
       'PovertyUnder18Pct', 'PovertyAllAgesPct', 'Deep_Pov_All',
       'Deep_Pov_Children', 'PovertyUnder18Num', 'PovertyAllAgesNum']

    jobs_cols = ['FIPS', 'State', 'County', 'UnempRate2018', 'UnempRate2017',
       'UnempRate2016', 'UnempRate2015', 'UnempRate2014', 'UnempRate2010',
       'UnempRate2007', 'PctEmpChange1018', 'PctEmpChange1718',
       'PctEmpChange0718', 'PctEmpChange0710', 'PctEmpAgriculture',
       'PctEmpMining', 'PctEmpConstruction', 'PctEmpManufacturing',
       'PctEmpTrade', 'PctEmpTrans', 'PctEmpInformation', 'PctEmpFIRE',
       'PctEmpServices', 'PctEmpGovt', 'NumCivEmployed', 'NumUnemployed2010',
       'NumUnemployed2011', 'NumCivLaborForce2011', 'UnempRate2011',
       'NumEmployed2011', 'NumEmployed2010', 'NumCivLaborForce2010',
       'NumUnemployed2009', 'NumEmployed2009', 'NumCivLaborForce2009',
       'UnempRate2008', 'NumCivLaborForce2012', 'NumEmployed2008',
       'NumCivLaborForce2008', 'UnempRate2009', 'NumUnemployed2008',
       'NumUnemployed2014', 'NumUnemployed2018', 'NumEmployed2018',
       'NumCivLaborforce2018', 'NumUnemployed2017', 'NumEmployed2017',
       'NumCivLaborforce2017', 'NumUnemployed2016', 'NumEmployed2016',
       'NumCivLaborforce2016', 'NumCivLaborforce2015', 'NumEmployed2007',
       'NumUnemployed2015', 'UnempRate2012', 'NumEmployed2014',
       'NumCivLaborforce2014', 'UnempRate2013', 'NumUnemployed2013',
       'NumEmployed2013', 'NumCivLaborforce2013', 'NumUnemployed2007',
       'NumCivLaborforce2007', 'NumUnemployed2012', 'NumEmployed2012',
       'NumEmployed2015']



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
args = parser.parse_args()
epidemic_data = pd.read_csv(args.epidemic_data[0])
#The sex_eth_age_data conatins only 1877 counties of the over 3000 in total
sex_eth_age_data = pd.read_csv(args.sex_eth_age_data[0])
people = pd.read_csv(args.people[0])
income = pd.read_csv(args.income[0])
jobs = pd.read_csv(args.jobs[0])
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
epidemic_data = epidemic_data.drop(['State'],axis=1)
#Merge epidemic data with sex_eth_age_data
complete_df = pd.merge(sex_eth_age_data, epidemic_data, left_on=['State','County'], right_on=['stateFIPS','County'], how='left')
complete_df = complete_df.rename(columns={'countyFIPS':'FIPS'})
#Join all on FIPS
#Remove county to avoid duplicates
people = people.drop(['County'],axis=1)
complete_df = pd.merge(complete_df, people, on=['FIPS'], how='inner')
#Remove state and county to avoid duplicates
income = income.drop(['State', 'County'],axis=1)
jobs = jobs.drop(['State', 'County'],axis=1)
complete_df = pd.merge(complete_df, income, on=['FIPS'], how='inner')
complete_df = pd.merge(complete_df, jobs, on=['FIPS'], how='inner')
#Get death rate per total county pop
complete_df['Death rate per 1000'] = 1000*(complete_df['Cumulative deaths']/complete_df['County total'])
#Save df
complete_df.to_csv('complete_df.csv')
pdb.set_trace()
