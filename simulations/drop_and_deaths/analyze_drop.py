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
from sklearn.linear_model import LinearRegression
import pdb



#Arguments for argparse module:
parser = argparse.ArgumentParser(description = '''Analyze the lockdown effect in form of mobility drop.''')

parser.add_argument('--epidemic_data', nargs=1, type= str, default=sys.stdin, help = 'Path to eidemic data (csv).')
parser.add_argument('--mobility_data', nargs=1, type= str, default=sys.stdin, help = 'Google mobility data (csv).')
parser.add_argument('--drop_dates', nargs=1, type= str, default=sys.stdin, help = 'Dates to use for drop values in mobility.')
parser.add_argument('--outdir', nargs=1, type= str, default=sys.stdin, help = 'Path to outdir.')

###FUNCTIONS###
def construct_drop(epidemic_data, mobility_data, drop_dates, outdir):
        '''Read in and format all data needed for the drop analysis
        '''

        #Convert epidemic data to datetime
        epidemic_data['dateRep'] = pd.to_datetime(epidemic_data['dateRep'], format='%d/%m/%Y')
        #Rename date to date
        epidemic_data = epidemic_data.rename(columns={'dateRep':'date'})
        #Convert mobility data to datetime
        mobility_data['date'] = pd.to_datetime(mobility_data['date'], format='%Y/%m/%d')
        #Convert drop dates to datetime
        drop_dates['date'] = pd.to_datetime(drop_dates['date'], format='%Y/%m/%d')
        #Mobility key conversions
        key_conversions = {'United_States_of_America':'United States'}

        #Covariate names
        covariate_names = {'retail_and_recreation_percent_change_from_baseline':'tab:red',
                           'grocery_and_pharmacy_percent_change_from_baseline':'tab:purple',
                           'transit_stations_percent_change_from_baseline':'tab:pink',
                           'workplaces_percent_change_from_baseline':'tab:olive',
                           'residential_percent_change_from_baseline':'tab:cyan'}


        #Save fetched countries, death percentages and mobility data
        fetched_countries = []
        death_percentage = []
        fetched_mobility = {'retail_and_recreation_percent_change_from_baseline':[],
                           'grocery_and_pharmacy_percent_change_from_baseline':[],
                           'transit_stations_percent_change_from_baseline':[],
                           'workplaces_percent_change_from_baseline':[],
                           'residential_percent_change_from_baseline':[]}

        #Save start dates for epidemic data
        start_dates = []
        #Get unique countries
        countries = epidemic_data['countriesAndTerritories'].unique()
        #fig, ax = plt.subplots(figsize=(18/2.54, 12/2.54))

        for country in countries:
            #Get country epidemic data
            country_epidemic_data = epidemic_data[epidemic_data['countriesAndTerritories']==country]
            #Sort on date
            country_epidemic_data = country_epidemic_data.sort_values(by='date')
            #Reset index
            country_epidemic_data = country_epidemic_data.reset_index()

            #Mobility data from Google
            if country in key_conversions.keys():
                mob_key = key_conversions[country]
            else:
                mob_key = ' '.join(country.split('_'))

            country_mobility_data = mobility_data[mobility_data['country_region']==mob_key]
            #Get whole country - no subregion
            country_mobility_data = country_mobility_data[country_mobility_data['sub_region_1'].isna()]
            if len(country_mobility_data)<2:
                print('No mobility data for', country)
                continue
            #reset index
            country_mobility_data = country_mobility_data.reset_index()
            mobility_start = country_mobility_data['date'][0]
            mobility_end = max(country_mobility_data['date'])
            #calculate % deaths last week of total number of deaths
            country_deaths = np.array(country_epidemic_data['deaths'])
            if max(country_deaths)<10:
                print('Less than 10 deaths per day for', country)
                continue

            #Get date for after drop and corresponding mobility values
            country_drop_date = drop_dates[drop_dates['Country']==country]['date'].values[0]
            country_drop_day = country_mobility_data[country_mobility_data['date']==country_drop_date].index[0]
            for name in covariate_names:
                #construct a 1-week sliding average
                data = np.array(country_mobility_data[name])
                y = np.zeros(len(country_mobility_data))
                for i in range(7,len(data)):
                    y[i]=np.average(data[i-7:i])

                fetched_mobility[name].append(y[country_drop_day])

            #Get index for first death
            death_start = np.where(country_deaths>0)[0][0]
            percent_dead_last_week = np.zeros(len(country_deaths))
            for i in range(death_start+7,len(country_deaths)): #Loop over all deaths and calculate % for week intervals
                percent_dead_last_week[i] = np.sum(country_deaths[i-7:i])/np.sum(country_deaths[:i])
            #Save todays percentage
            death_percentage.append(percent_dead_last_week[-1])
            #Add death percentage to df and merge with mobility
            country_epidemic_data['death_percentage'] = percent_dead_last_week
            country_epidemic_data = country_epidemic_data.merge(country_mobility_data, left_on = 'date', right_on ='date', how = 'left')

            #Smooth cases
            sm_cases = np.zeros(len(country_epidemic_data))
            cases = np.array(country_epidemic_data['cases'])
            for i in range(7,len(country_epidemic_data)):
                sm_cases[i]=np.average(cases[i-7:i])
            country_epidemic_data['smoothed_cases']=sm_cases

            #Get biggest drop - decide by plotting
            identify_drop(country_epidemic_data, country, drop_dates, covariate_names, death_start, mobility_start, mobility_end, outdir)
            fetched_countries.append(country)


        print(len(fetched_countries), 'countries are included in the analysis')
        drop_df = pd.DataFrame() #Save drop values
        drop_df['Country'] = fetched_countries
        drop_df['Death percentage'] = death_percentage
        drop_df['retail'] = fetched_mobility['retail_and_recreation_percent_change_from_baseline']
        drop_df['grocery and pharmacy'] = fetched_mobility['grocery_and_pharmacy_percent_change_from_baseline']
        drop_df['transit'] = fetched_mobility['transit_stations_percent_change_from_baseline']
        drop_df['work'] = fetched_mobility['workplaces_percent_change_from_baseline']
        drop_df['residential'] = fetched_mobility['residential_percent_change_from_baseline']
        drop_df.to_csv('drop_df.csv')

        #plot relationships
        plot_death_vs_drop(drop_df, outdir)
        #Print countries in increaseing death % order
        drop_df = drop_df.sort_values(by='Death percentage')
        countries= np.array(drop_df['Country'])
        for i in range(0,len(drop_df),9):
            print('montage '+'_slide7.png '.join(countries[i:i+9])+ '_slide7.png -tile 3x3 -geometry +2+2')
        pdb.set_trace()
        return drop_df

def identify_drop(country_epidemic_data, country, drop_dates, covariate_names, death_start, mobility_start, mobility_end, outdir):
    '''Identify the mobility drop
    '''

    drop_date = drop_dates[drop_dates['Country']==country]['date'].values[0] #date for drop effect
    drop_index = country_epidemic_data[country_epidemic_data['date']==drop_date].index[0]

    if mobility_start>min(country_epidemic_data['date']):
        msi = country_epidemic_data[country_epidemic_data['date']==mobility_start].index[0]
    else:
        msi=0
    #Percent dead last week
    percent_dead_last_week = np.array(country_epidemic_data['death_percentage'])
    fig, ax1 = plt.subplots(figsize=(9/2.54, 6/2.54))
    for name in covariate_names:
        #construct a 1-week sliding average
        data = np.array(country_epidemic_data[name])
        y = np.zeros(len(country_epidemic_data))
        for i in range(7,len(y)):
            y[i]=np.average(data[i-7:i])
        country_epidemic_data[name]=y
        y_index = country_epidemic_data[name].dropna().index #remove NaNs
        ax1.plot(np.arange(msi,y_index[-1]), y[msi:y_index[-1]], color = covariate_names[name])
    #Plot date for value used as drop
    plt.axvline(drop_index, color='k')
    plt.text(drop_index,0,np.array(drop_date,  dtype='datetime64[D]'))

    ax1.set_xlabel('Epidemic day')
    ax1.set_ylabel('Mobility change')
    ax1.set_title(country)
    ax2 = ax1.twinx()
    ax2.plot(np.arange(death_start+7,len(percent_dead_last_week)), percent_dead_last_week[death_start+7:], color = 'k')
    #Cases
    cases = np.array(country_epidemic_data['smoothed_cases'])/max(country_epidemic_data['smoothed_cases'])
    ax2.bar(np.arange(len(cases)), cases, alpha = 0.3, color = 'g')
    ax2.set_ylabel('% deaths last week')
    ax1.set_xlim([msi, len(country_epidemic_data)]) #start of mobility til end of death %
    ax1.set_ylim([-85,30])
    ax2.set_ylim([0,1])
    fig.tight_layout()
    fig.savefig(outdir+'identify_drop/'+country+'_slide7.png',  format='png')
    plt.close()

    return None

def plot_death_vs_drop(drop_df, outdir):
    '''Plot relationship btw death percentage today and mobility drop at lockdown
    '''
    covariates = {'retail':'tab:red',
                    'grocery and pharmacy':'tab:purple',
                    'transit':'tab:pink',
                    'work':'tab:olive',
                    'residential':'tab:cyan'}

    for key in covariates:
        fig, ax = plt.subplots(figsize=(9/2.54, 9/2.54))
        ax.scatter(drop_df[key], drop_df['Death percentage'], color = covariates[key])
        ax.set_xlabel('Mobility change in drop')
        ax.set_ylabel('Death percentage 21 May')
        #ax.set_yscale('log')
        ax.set_title(key)
        fig.tight_layout()
        fig.savefig(outdir+key+'.png',  format='png')
        plt.close()

def linear_reg(drop_df):
    '''Pareform LR
    '''
    y = np.array(drop_df['Death percentage'])
    X = [np.array(drop_df['retail']),np.array(drop_df['grocery and pharmacy']),np.array(drop_df['transit']),np.array(drop_df['work']),np.array(drop_df['residential'])]
    X = np.array(X)
    X=X.T
    reg = LinearRegression().fit(X, y)
    print('Score:',reg.score(X,y))
    print('Coef.', reg.coef_)
    pdb.set_trace()
#####MAIN#####
#Set font size
matplotlib.rcParams.update({'font.size': 9})
args = parser.parse_args()
epidemic_data = pd.read_csv(args.epidemic_data[0])
mobility_data = pd.read_csv(args.mobility_data[0])
drop_dates = pd.read_csv(args.drop_dates[0])
outdir = args.outdir[0]
drop_df = construct_drop(epidemic_data, mobility_data, drop_dates, outdir)
#drop_df=pd.read_csv('drop_df.csv')
#linear_reg(drop_df)
