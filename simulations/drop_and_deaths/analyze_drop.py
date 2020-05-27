#! /usr/bin/env python3
# -*- coding: utf-8 -*-


import argparse
import sys
import os
import glob
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
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
        drop_dates['drop_start'] = pd.to_datetime(drop_dates['drop_start'], format='%Y/%m/%d')
        drop_dates['drop_end'] = pd.to_datetime(drop_dates['drop_end'], format='%Y/%m/%d')

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
        drop_start_cases = [] #%cases at drop start
        drop_end_cases = [] #%cases at drop end
        drop_duration = []
        fetched_mobility = {'retail_and_recreation_percent_change_from_baseline':[],
                           'grocery_and_pharmacy_percent_change_from_baseline':[],
                           'transit_stations_percent_change_from_baseline':[],
                           'workplaces_percent_change_from_baseline':[],
                           'residential_percent_change_from_baseline':[]}

        #Save start dates for epidemic data
        start_dates = []
        days_after_drop = []
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

            #Check that at least 10 deaths per day has been reached
            country_deaths = np.array(country_epidemic_data['deaths'])
            if max(country_deaths)<10:
                print('Less than 10 deaths per day reached for', country)
                continue
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
            #Get start and end dates
            mobility_start = country_mobility_data['date'][0]
            mobility_end = max(country_mobility_data['date'])

            #Smooth deaths
            sm_deaths = np.zeros(len(country_epidemic_data))
            for i in range(7,len(country_epidemic_data)):
                sm_deaths[i-1]=np.average(country_deaths[i-7:i])
            sm_deaths[0:6] = sm_deaths[7]
            country_epidemic_data['smoothed_deaths']=sm_deaths

            #Get date for after drop and corresponding mobility values
            country_drop_end = drop_dates[drop_dates['Country']==country]['drop_end'].values[0]
            country_drop_day = country_mobility_data[country_mobility_data['date']==country_drop_end].index[0]
            for name in covariate_names:
                #construct a 1-week sliding average to smooth the mobility data
                data = np.array(country_mobility_data[name])
                y = np.zeros(len(country_mobility_data))
                for i in range(7,len(data)):
                    y[i]=np.average(data[i-7:i])

                fetched_mobility[name].append(y[country_drop_day])

            #calculate % deaths last week of total number of deaths
            #Get index for first death
            death_start = np.where(country_deaths>0)[0][0]
            percent_dead_last_week = np.zeros(len(sm_deaths))
            for i in range(death_start+6,len(sm_deaths)): #Loop over all deaths and calculate % for week intervals
                percent_dead_last_week[i] = np.sum(sm_deaths[i-7:i])/np.sum(sm_deaths[:i])

            #Add death percentage to df and merge with mobility
            country_epidemic_data['death_percentage'] = percent_dead_last_week
            country_epidemic_data = country_epidemic_data.merge(country_mobility_data, left_on = 'date', right_on ='date', how = 'left')

            #Smooth cases
            sm_cases = np.zeros(len(country_epidemic_data))
            cases = np.array(country_epidemic_data['cases'])
            for i in range(7,len(country_epidemic_data)):
                sm_cases[i-1]=np.average(cases[i-7:i])
            sm_cases[0:6] = sm_cases[7]
            country_epidemic_data['smoothed_cases']=sm_cases/max(sm_cases)
            #Get %cases at drop start and end
            country_drop_start = drop_dates[drop_dates['Country']==country]['drop_start'].values[0]
            dsi = country_epidemic_data[country_epidemic_data['date']==country_drop_start].index[0] #drop start index
            dei = country_epidemic_data[country_epidemic_data['date']==country_drop_end].index[0] #drop end index

            #Save data
            #Save death percentage 6 weeks after mobility drop
            death_delay =dsi+(7*8)
            days_after_drop.append(len(country_epidemic_data)-1-dsi)
            if death_delay>=len(country_epidemic_data):
                death_delay = len(country_epidemic_data)-1
                print(country, 'has only', len(country_epidemic_data)-1-dsi, 'days of epidemic data after drop')
            death_percentage.append(country_epidemic_data.loc[len(country_epidemic_data)-1,'death_percentage'])
            drop_start_cases.append(country_epidemic_data.loc[dsi,'smoothed_cases']) #%cases at drop start
            drop_end_cases.append(country_epidemic_data.loc[dei,'smoothed_cases'])
            drop_duration.append(dei-dsi)
            #Get biggest drop - decide by plotting
            #identify_drop(country_epidemic_data, country, drop_dates, covariate_names, death_start, mobility_start, mobility_end, outdir)
            fetched_countries.append(country)


        print(len(fetched_countries), 'countries are included in the analysis')
        drop_df = pd.DataFrame() #Save drop values
        drop_df['Country'] = fetched_countries
        drop_df['Death percentage'] = death_percentage
        drop_df['drop_start_cases'] = drop_start_cases#%cases at drop start
        drop_df['drop_end_cases'] = drop_end_cases #%cases at drop end
        drop_df['drop_duration'] = drop_duration
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
        drop_df.to_csv('drop_df.csv')

        return drop_df

def identify_drop(country_epidemic_data, country, drop_dates, covariate_names, death_start, mobility_start, mobility_end, outdir):
    '''Identify the mobility drop
    '''

    drop_start_date = drop_dates[drop_dates['Country']==country]['drop_start'].values[0] #date for drop start
    drop_end_date = drop_dates[drop_dates['Country']==country]['drop_end'].values[0] #date for drop effect
    drop_end_index = country_epidemic_data[country_epidemic_data['date']==drop_end_date].index[0]

    if mobility_start>min(country_epidemic_data['date']):
        msi = country_epidemic_data[country_epidemic_data['date']==mobility_start].index[0]
    else:
        msi=0
    #Check that start of drop is included in epidemic data - otherwise set to start of mobility
    if drop_start_date<min(country_epidemic_data['date']):
        drop_start_index=msi
    else:
        drop_start_index = country_epidemic_data[country_epidemic_data['date']==drop_start_date].index[0]

    #Percent dead last week
    percent_dead_last_week = np.array(country_epidemic_data['death_percentage'])
    fig, ax1 = plt.subplots(figsize=(9/2.54, 6/2.54))
    for name in covariate_names:
        #construct a 1-week sliding average
        data = np.array(country_epidemic_data[name])
        y = np.zeros(len(country_epidemic_data))
        for i in range(7,len(y)):
            y[i-1]=np.average(data[i-7:i])
        y[0:6] = y[7]
        country_epidemic_data[name]=y
        y_index = country_epidemic_data[name].dropna().index #remove NaNs
        ax1.plot(np.arange(msi,y_index[-1]), y[msi:y_index[-1]], color = covariate_names[name])
    #Plot date for values used as drop start and end
    plt.axvline(drop_start_index, color='k')
    plt.text(drop_start_index,-20,np.array(drop_start_date,  dtype='datetime64[D]'))
    plt.axvline(drop_end_index, color='k')
    plt.text(drop_end_index,0,np.array(drop_end_date,  dtype='datetime64[D]'))

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

def linear_reg(drop_df, outdir):
    '''Pareform LR
    '''
    y = np.array(drop_df['Death percentage'])
    X = [np.array(drop_df['drop_start_cases']), np.array(drop_df['drop_end_cases']),
       np.array(drop_df['drop_duration']), np.array(drop_df['retail']),
       np.array(drop_df['grocery and pharmacy']), np.array(drop_df['transit']),
       np.array(drop_df['work']),np.array(drop_df['residential'])]
    X = np.array(X)
    X=X.T
    reg = LinearRegression().fit(X, y)
    score= reg.score(X,y)
    coef = reg.coef_
    print('Score:',score)
    print('Coef.', coef)

    #Visualize
    col_names = ['','% cases drop start', '% cases drop end', 'drop duration', 'retail',
            'grocery and pharmacy', 'transit', 'work', 'residential']
    fig, ax = plt.subplots(figsize=(12/2.54, 12/2.54))
    ax.bar(np.arange(8), coef)
    ax.set_xticklabels(col_names, rotation='vertical')
    ax.set_ylabel('Regression coefficient')
    fig.tight_layout()
    fig.savefig(outdir+'reg_coef.png',  format='png')
    plt.close()

    #2D plots
    colors = ['b','g']
    fig, ax = plt.subplots(figsize=(12/2.54, 12/2.54))
    for i in range(2):
        fig, ax = plt.subplots(figsize=(12/2.54, 12/2.54))
        ax.scatter(X[:,i], y, color =colors[i])
        z = np.polyfit(X[:,i],y, deg=3)
        p = np.poly1d(z)
        ax.plot(np.sort(X[:,i]),p(np.sort(X[:,i])))
        ax.set_ylabel('% dead last week')
        ax.set_xlabel(col_names[i+1])
        ax.set_title(col_names[i+1])
        fig.legend()
        fig.savefig(outdir+str(i)+'_coef.png',  format='png')
    pdb.set_trace()
    #3D plot
    B1, B2 = np.meshgrid(X[:,0], X[:,1])
    B3 = np.zeros((len(y),len(y)))
    for i in range(len(y)):
        B3[i,:]=y[i]
    fig, ax = plt.subplots(figsize=(12/2.54, 12/2.54))
    ax = plt.axes(projection='3d')
    ax.scatter3D(X[:,0], X[:,1], y, color ='magenta')
    #ax.plot_trisurf(X[:,0], X[:,1], y, cmap='viridis')
    ax.set_xlabel('% cases at drop start')
    ax.set_ylabel('% cases at drop end')
    ax.set_zlabel('% dead last week')
    ax.plot_surface(B1, B2, B3,alpha=0.2)
    #fig.savefig(outdir+'3D_coef.png',  format='png')
    plt.show()
    pdb.set_trace()
#####MAIN#####
#Set font size
matplotlib.rcParams.update({'font.size': 9})
args = parser.parse_args()
epidemic_data = pd.read_csv(args.epidemic_data[0])
mobility_data = pd.read_csv(args.mobility_data[0])
drop_dates = pd.read_csv(args.drop_dates[0])
outdir = args.outdir[0]
#drop_df = construct_drop(epidemic_data, mobility_data, drop_dates, outdir)
drop_df=pd.read_csv('drop_df.csv')
linear_reg(drop_df, outdir)
