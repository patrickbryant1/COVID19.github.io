#! /usr/bin/env python3
# -*- coding: utf-8 -*-


import argparse
import sys
import os
import glob
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from scipy.stats import pearsonr
import numpy as np
import seaborn as sns


import pdb



#Arguments for argparse module:
parser = argparse.ArgumentParser(description = '''Visuaize results from model using google mobility data and most of the ICL response team model''')

parser.add_argument('--datadir', nargs=1, type= str, default=sys.stdin, help = 'Path to datadir.')
parser.add_argument('--countries', nargs=1, type= str, default=sys.stdin, help = 'Countries to model (csv).')
parser.add_argument('--end_date', nargs=1, type= str, default=sys.stdin, help = 'Up to which date to include data.')
parser.add_argument('--days_to_simulate', nargs=1, type= int, default=sys.stdin, help = 'Number of days to simulate.')
parser.add_argument('--outdir', nargs=1, type= str, default=sys.stdin, help = 'Path to outdir.')

def read_and_format_data(datadir, countries, days_to_simulate, end_date, covariate_names):
        '''Read in and format all data needed for the model
        '''

        #Get epidemic data
        epidemic_data = pd.read_csv(datadir+'ecdc_20200603.csv')
        #Convert to datetime
        epidemic_data['dateRep'] = pd.to_datetime(epidemic_data['dateRep'], format='%d/%m/%Y')
        epidemic_data = epidemic_data[epidemic_data['dateRep']<=end_date]
        #Mobility data
        mobility_data = pd.read_csv(datadir+'Global_Mobility_Report.csv')
        #Convert to datetime
        mobility_data['date']=pd.to_datetime(mobility_data['date'], format='%Y/%m/%d')
        mobility_data = mobility_data[mobility_data['date']<=end_date]
        #Model data - to be used for plotting
        model_data = {'dates_by_country':np.zeros((days_to_simulate,len(countries)), dtype='datetime64[D]'),
                    'deaths_by_country':np.zeros((days_to_simulate,len(countries))),
                    'cases_by_country':np.zeros((days_to_simulate,len(countries))),
                    'days_by_country':np.zeros(len(countries)),
                    'retail_and_recreation_percent_change_from_baseline':np.zeros((days_to_simulate,len(countries))),
                    'grocery_and_pharmacy_percent_change_from_baseline':np.zeros((days_to_simulate,len(countries))),
                    'transit_stations_percent_change_from_baseline':np.zeros((days_to_simulate,len(countries))),
                    'workplaces_percent_change_from_baseline':np.zeros((days_to_simulate,len(countries))),
                    'residential_percent_change_from_baseline':np.zeros((days_to_simulate,len(countries))),
                    }


        #Get data by country
        for c in range(len(countries)):
                country = countries[c]

                #Get country epidemic data
                country_epidemic_data = epidemic_data[epidemic_data['countriesAndTerritories']==country]
                #Sort on date
                country_epidemic_data = country_epidemic_data.sort_values(by='dateRep')
                #Reset index
                country_epidemic_data = country_epidemic_data.reset_index()

                #Get all dates with at least 10 deaths
                cum_deaths = country_epidemic_data['deaths'].cumsum()
                death_index = cum_deaths[cum_deaths>=10].index[0]
                di30 = death_index-30
                #Get part of country_epidemic_data 30 days before day with at least 10 deaths
                country_epidemic_data = country_epidemic_data.loc[di30:]
                #Reset index
                country_epidemic_data = country_epidemic_data.reset_index()

                print(country, len(country_epidemic_data))
                #Check that foreacast is really a forecast
                N = len(country_epidemic_data)
                model_data['days_by_country'][c]=N
                forecast = days_to_simulate - N
                if forecast <0: #If the number of predicted days are less than the number available
                    days_to_simulate = N
                    forecast = 0
                    print('Forecast error!')
                    pdb.set_trace()

                #Smooth the number of deaths
                deaths = np.array(country_epidemic_data['deaths'])
                sm_deaths = np.zeros(days_to_simulate)
                sm_deaths -=1 #Assign -1 for all forcast days
                #Smooth deaths
                #Do a 7day sliding window to get more even death predictions
                for i in range(7,len(country_epidemic_data)+1):
                    sm_deaths[i-1]=np.average(deaths[i-7:i])
                sm_deaths[0:6] = sm_deaths[6]

                #Save dates
                model_data['dates_by_country'][:N,c] = np.array(country_epidemic_data['dateRep'], dtype='datetime64[D]')
                #Save deaths
                model_data['deaths_by_country'][:,c] = sm_deaths
                #Save cases
                model_data['cases_by_country'][:N,c] = country_epidemic_data['cases']

                #Covariates - assign the same shape as others (days_to_simulate)
                #Mobility data from Google
                country_cov_data = mobility_data[mobility_data['country_region']==country]
                if country == 'United_Kingdom': #Different assignments for UK
                    country_cov_data = mobility_data[mobility_data['country_region']=='United Kingdom']
                #Get whole country - no subregion
                country_cov_data =  country_cov_data[country_cov_data['sub_region_1'].isna()]
                #Make sure the start dates are the same
                country_cov_data = country_cov_data[country_cov_data['date']>=min(country_epidemic_data['dateRep'])]
                #Construct a 1-week sliding average to smooth the mobility data
                for name in covariate_names:
                    mob_i = np.array(country_cov_data[name])
                    y = np.zeros(len(country_epidemic_data))
                    for i in range(7,len(mob_i)+1):
                        #Check that there are no NaNs
                        if np.isnan(mob_i[i-7:i]).any():
                            #If there are NaNs, loop through and replace with value from prev date
                            for i_nan in range(i-7,i):
                                if np.isnan(mob_i[i_nan]):
                                    mob_i[i_nan]=mob_i[i_nan-1]
                        y[i-1]=np.average(mob_i[i-7:i])#Assign average
                    y[0:6] = y[6]#Assign first week
                    country_epidemic_data[name]=y

                    cov_i = np.zeros(days_to_simulate)
                    cov_i[:N] = np.array(country_epidemic_data[name])
                    #Add covariate info to forecast
                    #cov_i[N:days_to_simulate]=cov_i[N-1]
                    model_data[name][:,c] = cov_i
        return model_data


def analyze_corr(model_data, covariate_names, outdir):
    '''Plot parameters for each iteration next to each other as in the R fucntion mcmc_parcoord
    '''


    x =10 #minimum number of days to inculde for correlation analysis
    deaths = model_data['deaths_by_country']
    #Save correlations in array
    correlations = np.zeros((deaths.shape[1],len(covariate_names), int(min(model_data['days_by_country']))-x))
    btw_correlations = np.zeros((5,5))#Correlations btw mobility sectors
    for i in range(deaths.shape[1]):
        country_days = int(model_data['days_by_country'][i])
        country_deaths = deaths[:country_days,i]
        all_country_cov_data = [] #Save all cov data for btw correlation analysis
        for j in range(len(covariate_names)):
            cov_data = model_data[covariate_names[j]][:country_days,i]
            all_country_cov_data.append(cov_data)
            #Correlate with delay
            R,p = pearsonr(country_deaths,cov_data) #0 delay

            correlations[i,j,0]=R
            for k in range(1,correlations.shape[2]): #Include at least 10 points
                R,p = pearsonr(country_deaths[k:],cov_data[:-k])
                correlations[i,j,k]=R
        #Analyze btw correlations
        btw_correlations+=np.corrcoef(np.array(all_country_cov_data))

    #Plot correlations
    keys = ['retail and recreation', 'grocery and pharmacy',
            'transit stations','workplaces','residential']
    cmaps = ['Reds','Purples','Oranges','Greens','Blues']
    colors =['darkorange','tab:purple','magenta', 'tab:olive', 'tab:cyan']
    for j in range(correlations.shape[1]): #Go through all covariates
        fig, ax = plt.subplots(figsize=(6/2.54, 4/2.54))
        all_countries_x=[]
        all_countries_y=[]
        for i in range(correlations.shape[0]):#Go through countries
            all_countries_x.extend(np.arange(28,correlations.shape[2]))
            all_countries_y.extend(correlations[i,j,28:])
            ax.plot(np.arange(correlations.shape[2]),correlations[i,j,:],color=colors[j], linewidth=1, alpha = 0.5)
        #sns.kdeplot(all_countries_x,all_countries_y, shade = True, cmap = colors[j])
        ax.set_title(keys[j])
        ax.set_ylim([-1,1])
        ax.set_xlabel('Time delay for deaths (days)')
        ax.set_ylabel('Pearson R')
        fig.tight_layout()
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        fig.savefig(outdir+'correlations/'+covariate_names[j]+'.png', format='png', dpi=300)

    #Plot between correlations
    fig, ax = plt.subplots(figsize=(6, 4))
    plt.imshow(btw_correlations/11,cmap='summer')
    ax.set_xticks(np.arange(5))
    ax.set_yticks(np.arange(5))
    ax.set_xticklabels(keys,rotation=90)
    ax.set_yticklabels(keys)
    ax.set_title('Pearson R')
    plt.colorbar()
    fig.tight_layout()
    fig.savefig(outdir+'correlations/btw_correlations.png', format='png', dpi=300)


#####MAIN#####
#Set font size
matplotlib.rcParams.update({'font.size': 7})
args = parser.parse_args()
datadir = args.datadir[0]
countries = args.countries[0].split(',')
days_to_simulate=args.days_to_simulate[0] #Number of days to model. Increase for further forecast
end_date=args.end_date[0]
outdir = args.outdir[0]
#Covariate names
covariate_names = ['retail_and_recreation_percent_change_from_baseline',
'grocery_and_pharmacy_percent_change_from_baseline',
'transit_stations_percent_change_from_baseline',
'workplaces_percent_change_from_baseline',
'residential_percent_change_from_baseline']

#Read data
model_data = read_and_format_data(datadir, countries, days_to_simulate, end_date, covariate_names)
#Analyze
analyze_corr(model_data, covariate_names, outdir)
