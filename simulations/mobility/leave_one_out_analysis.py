#! /usr/bin/env python3
# -*- coding: utf-8 -*-


import argparse
import sys
import os
import glob
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from scipy.stats import gamma
import numpy as np
import seaborn as sns
import pystan

import pdb



#Arguments for argparse module:
parser = argparse.ArgumentParser(description = '''Visuaize results from leave one out analysis of model using google mobility data and most of the ICL response team model. The script compares the means for all countries in all leave one out analyses.''')

parser.add_argument('--datadir', nargs=1, type= str, default=sys.stdin, help = 'Path to outdir.')
parser.add_argument('--country_combos', nargs=1, type= str, default=sys.stdin, help = 'Country combinations modeled in leave one out analysis (csv).')
parser.add_argument('--days_to_simulate', nargs=1, type= int, default=sys.stdin, help = 'Number of days to simulate.')
parser.add_argument('--outdir', nargs=1, type= str, default=sys.stdin, help = 'Path to outdir.')

def read_and_format_data(datadir, country, days_to_simulate):
        '''Read in and format all data needed for the model
        '''

        #Get epidemic data
        epidemic_data = pd.read_csv(datadir+'ecdc_20200412.csv')
        #Convert to datetime
        epidemic_data['dateRep'] = pd.to_datetime(epidemic_data['dateRep'], format='%d/%m/%Y')

        #Model data - to be used for plotting
        stan_data = {'dates_by_country':np.zeros(days_to_simulate, dtype='datetime64[D]'),
             'deaths_by_country':np.zeros(days_to_simulate),
             'cases_by_country':np.zeros(days_to_simulate),
             'days_by_country':0
              }


        #Covariate names
        covariate_names = ['retail','grocery','transit','work','residential']
        #Get data by country
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
        stan_data['days_by_country']=N
        forecast = days_to_simulate - N
        if forecast <0: #If the number of predicted days are less than the number available
            days_to_simulate = N
            forecast = 0
            print('Forecast error!')
            pdb.set_trace()

        #Save dates
        stan_data['dates_by_country'][:N] = np.array(country_epidemic_data['dateRep'], dtype='datetime64[D]')
        #Save deaths
        stan_data['deaths_by_country'][:N] = country_epidemic_data['deaths']
        #Save cases
        stan_data['cases_by_country'][:N] = country_epidemic_data['cases']

        return stan_data

def visualize_results(outdir, country_combos, country_data, days_to_simulate):
    '''Visualize results by reading in all information from all countries in all combinations
    of the leave one out analysis.
    '''
    #Read in intervention dates
    intervention_df = pd.read_csv(datadir+'interventions_only.csv')
    #Get all data from all simulations for each country
    country_means = {"Austria":np.zeros((3,10,days_to_simulate)), #Cases,Deaths,Rt for all combinations and all days  
                     "Belgium":np.zeros((3,10,days_to_simulate)),
                     "Denmark":np.zeros((3,10,days_to_simulate)),
                     "France":np.zeros((3,10,days_to_simulate)),
                     "Germany":np.zeros((3,10,days_to_simulate)),
                     "Italy":np.zeros((3,10,days_to_simulate)),  
                     "Norway":np.zeros((3,10,days_to_simulate)), 
                     "Spain":np.zeros((3,10,days_to_simulate)), 
                     "Sweden":np.zeros((3,10,days_to_simulate)), 
                     "Switzerland":np.zeros((3,10,days_to_simulate)), 
                     "United_Kingdom":np.zeros((3,10,days_to_simulate))
                    }
    #Loop through all country combos
    fetched_combos = {"Austria":0,"Belgium":0,"Denmark":0,"France":0, #Keep track of index for each country
                      "Germany":0,"Italy":0,"Norway":0,"Spain":0,
                      "Sweden":0,"Switzerland":0,"United_Kingdom":0} 
    for i in range(len(country_combos)):
        countries = country_combos.loc[i].values
        summary = pd.read_csv(outdir+'COMBO'+str(i+1)+'/summary.csv')
        #Loop through all countries in combo
        for j in range(len(countries)):
            country= countries[j]
            country_npi = intervention_df[intervention_df['Country']==country]
            #Extract mean modeling results for country j
            means = {'prediction':[],'E_deaths':[], 'Rt':[]}
            for k in range(1,days_to_simulate+1):
                for var in ['prediction', 'E_deaths', 'Rt']:
                    var_ij = summary[summary['Unnamed: 0']==var+'['+str(k)+','+str(j+1)+']']
                    means[var].append(var_ij['mean'].values[0])
            #Save data to country means
            country_means[country][0,fetched_combos[country],:]=means['prediction']
            country_means[country][1,fetched_combos[country],:]=means['E_deaths']
            country_means[country][2,fetched_combos[country],:]=means['Rt']
            fetched_combos[country]+=1 #Increase location index in np array
    pdb.set_trace()



    #Plot alphas - influence of each mobility parameter
    fig, ax = plt.subplots(figsize=(4, 4))
    for i in range(1,6):
        alpha = summary[summary['Unnamed: 0']=='alpha['+str(i)+']']
        alpha_m = 1-np.exp(-alpha['mean'].values[0])
        alpha_2_5 = 1-np.exp(-alpha['2.5%'].values[0])
        alpha_97_5 = 1-np.exp(-alpha['97.5%'].values[0])
        ax.scatter(i,alpha_m)
        ax.plot([i]*2,[alpha_2_5,alpha_97_5])
    ax.set_ylim([0,1])
    ax.set_ylabel('Fractional reduction in R0')
    ax.set_xticklabels(covariate_names,rotation='vertical')
    plt.tight_layout()
    fig.savefig(outdir+'plots/alphas.png', format='png')
    plt.close()



    #plot per country
    #Read in intervention dates
    result_file = open(outdir+'plots/summary_means.csv', 'w')
    for i in range(1,len(countries)+1):
        country= countries[i-1]
        country_npi = intervention_df[intervention_df['Country']==country]
        #Get att stan data for country i
        dates = stan_data['dates_by_country'][:,i-1]
        observed_country_deaths = stan_data['deaths_by_country'][:,i-1]
        observed_country_cases = stan_data['cases_by_country'][:,i-1]
        end = int(stan_data['days_by_country'][i-1])#End of data for country i
        country_retail = stan_data['retail'][:,i-1]
        country_grocery= stan_data['grocery'][:,i-1]
        country_transit = stan_data['transit'][:,i-1]
        country_work = stan_data['work'][:,i-1]
        country_residential = stan_data['residential'][:,i-1]

        #Extract modeling results
        means = {'prediction':[],'E_deaths':[], 'Rt':[]}
        lower_bound = {'prediction':[],'E_deaths':[], 'Rt':[]} #Estimated 2.5 %
        higher_bound = {'prediction':[],'E_deaths':[], 'Rt':[]} #Estimated 97.5 % - together 95 % CI
        lower_bound25 = {'prediction':[],'E_deaths':[], 'Rt':[]} #Estimated 25%
        higher_bound75 = {'prediction':[],'E_deaths':[], 'Rt':[]} #Estimated 55 % - together 75 % CI
        #Get means and 95 % CI for cases (prediction), deaths and Rt for all time steps
        for j in range(1,days_to_simulate+1):
            for var in ['prediction', 'E_deaths', 'Rt']:
                var_ij = summary[summary['Unnamed: 0']==var+'['+str(j)+','+str(i)+']']
                means[var].append(var_ij['mean'].values[0])
                lower_bound[var].append(var_ij['2.5%'].values[0])
                higher_bound[var].append(var_ij['97.5%'].values[0])
                lower_bound25[var].append(var_ij['25%'].values[0])
                higher_bound75[var].append(var_ij['75%'].values[0])

        #Plot cases
        #Per day
        plot_shade_ci(days, end, dates[0], means['prediction'], observed_country_cases,lower_bound['prediction'],
        higher_bound['prediction'], lower_bound25['prediction'], higher_bound75['prediction'], 'Cases per day',
        outdir+'plots/'+country+'_cases.png',country_npi, country_retail, country_grocery, country_transit, country_work, country_residential)
        #Cumulative
        plot_shade_ci(days, end, dates[0], np.cumsum(means['prediction']), np.cumsum(observed_country_cases),np.cumsum(lower_bound['prediction']),
        np.cumsum(higher_bound['prediction']), np.cumsum(lower_bound25['prediction']), np.cumsum(higher_bound75['prediction']),
        'Cumulative cases',outdir+'plots/'+country+'_cumulative_cases.png',country_npi, country_retail, country_grocery, country_transit, country_work, country_residential)
        #Plot Deaths
        plot_shade_ci(days, end,dates[0],means['E_deaths'],observed_country_deaths, lower_bound['E_deaths'], higher_bound['E_deaths'],
        lower_bound25['E_deaths'], higher_bound75['E_deaths'], 'Deaths per day',
        outdir+'plots/'+country+'_deaths.png',country_npi, country_retail, country_grocery, country_transit, country_work, country_residential)
        #Plot R
        plot_shade_ci(days,end,dates[0],means['Rt'],'', lower_bound['Rt'], higher_bound['Rt'], lower_bound25['Rt'],
        higher_bound75['Rt'],'Rt',outdir+'plots/'+country+'_Rt.png',country_npi,
        country_retail, country_grocery, country_transit, country_work, country_residential)
 
       #Print R mean at beginning and end of model
        result_file.write(country+','+str(dates[0])+','+str(np.round(means['Rt'][0],2))+','+str(np.round(means['Rt'][-1],2))+'\n')#Print for table
    #Close outfile
    result_file.close()

    return None


def plot_shade_ci(x,end,start_date,y, observed_y, lower_bound, higher_bound,lower_bound25, higher_bound75,ylabel,outname,country_npi, country_retail, country_grocery, country_transit, country_work, country_residential):
    '''Plot with shaded 95 % CI (plots both 1 and 2 std, where 2 = 95 % interval)
    '''
    dates = np.arange(start_date,np.datetime64('2020-04-20')) #Get dates - increase for longer foreacast
    forecast = len(dates)
    fig, ax1 = plt.subplots(figsize=(9, 4))
    #Plot observed dates
    if len(observed_y)>1:
        ax1.bar(x[:end],observed_y[:end], alpha = 0.5)
    ax1.plot(x[:end],y[:end], alpha=0.5, color='b', label='so far', linewidth = 1.0)
    ax1.fill_between(x[:end], lower_bound[:end], higher_bound[:end], color='cornflowerblue', alpha=0.4)
    ax1.fill_between(x[:end], lower_bound25[:end], higher_bound75[:end], color='cornflowerblue', alpha=0.6)

    #Plot predicted dates
    ax1.plot(x[end:forecast],y[end:forecast], alpha=0.5, color='g', label='forecast', linewidth = 1.0)
    ax1.fill_between(x[end-1:forecast], lower_bound[end-1:forecast] ,higher_bound[end-1:forecast], color='forestgreen', alpha=0.4)
    ax1.fill_between(x[end-1:forecast], lower_bound25[end-1:forecast], higher_bound75[end-1:forecast], color='forestgreen', alpha=0.6)

    #Plot NPIs
    #NPIs
    NPI = ['public_events', 'schools_universities',  'lockdown',
        'social_distancing_encouraged', 'self_isolating_if_ill']
    NPI_labels = {'schools_universities':'schools and universities',  'public_events': 'public events', 'lockdown': 'lockdown',
        'social_distancing_encouraged':'social distancing encouraged', 'self_isolating_if_ill':'self isolating if ill'}
    NPI_markers = {'schools_universities':'*',  'public_events': 'X', 'lockdown': 's',
        'social_distancing_encouraged':'p', 'self_isolating_if_ill':'d'}
    NPI_colors = {'schools_universities':'k',  'public_events': 'blueviolet', 'lockdown': 'mediumvioletred',
        'social_distancing_encouraged':'maroon', 'self_isolating_if_ill':'darkolivegreen'}
    y_npi = max(higher_bound[:forecast])*0.9
    y_step = y_npi/20
    npi_xvals = [] #Save npi xvals to not plot over each npi

    #ax1
    ax1.legend(loc='best', frameon=False, markerscale=2)
    ax1.set_ylabel(ylabel)
    ax1.set_ylim([0,max(higher_bound[:forecast])])
    xticks=np.arange(forecast-1,0,-7)
    ax1.set_xticks(xticks)
    ax1.set_xticklabels(dates[xticks],rotation='vertical')
    #ax2
    ax2.set_ylabel('Relative change')
    ax2.set_ylim([-1,0.4])
    ax2.legend(loc='best', frameon=False)
    fig.tight_layout()
    fig.savefig(outname, format = 'png')
    plt.close()



#####MAIN#####
args = parser.parse_args()
datadir = args.datadir[0]
country_combos = pd.read_csv(args.country_combos[0], header = None)
days_to_simulate=args.days_to_simulate[0] #Number of days to model. Increase for further forecast
outdir = args.outdir[0]

#Get data per country
country_data = {} #Save all data from all extracted country combinations

for country in ["Austria", "Belgium", "Denmark", "France", "Germany", "Italy", "Norway", "Spain", "Sweden", "Switzerland", "United_Kingdom"]:
   
    #Read data
    stan_data = read_and_format_data(datadir, country, days_to_simulate)
    country_data[country]=stan_data
#Visualize
visualize_results(outdir, country_combos, country_data, days_to_simulate)

