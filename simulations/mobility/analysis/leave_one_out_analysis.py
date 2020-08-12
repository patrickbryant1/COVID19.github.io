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
import pystan

import pdb



#Arguments for argparse module:
parser = argparse.ArgumentParser(description = '''Visuaize results from leave one out analysis of model using google mobility data and most of the ICL response team model. The script compares the means for all countries in all leave one out analyses.''')

parser.add_argument('--datadir', nargs=1, type= str, default=sys.stdin, help = 'Path to outdir.')
parser.add_argument('--epidemic_data', nargs=1, type= str, default=sys.stdin, help = 'Path to ECDC data.')
parser.add_argument('--country_combos', nargs=1, type= str, default=sys.stdin, help = 'Country combinations modeled in leave one out analysis (csv).')
parser.add_argument('--days_to_simulate', nargs=1, type= int, default=sys.stdin, help = 'Number of days to simulate.')
parser.add_argument('--outdir', nargs=1, type= str, default=sys.stdin, help = 'Path to outdir.')

def read_and_format_data(epidemic_data, country, days_to_simulate):
        '''Read in and format all data needed for the model
        '''

        #Model data - to be used for plotting
        model_data = {'dates_by_country':np.zeros(days_to_simulate, dtype='datetime64[D]'),
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
        model_data['days_by_country']=N
        forecast = days_to_simulate - N
        if forecast <0: #If the number of predicted days are less than the number available
            days_to_simulate = N
            forecast = 0
            print('Forecast error!')
            pdb.set_trace()

        #Save dates
        model_data['dates_by_country'][:N] = np.array(country_epidemic_data['dateRep'], dtype='datetime64[D]')
        #Save deaths
        model_data['deaths_by_country'][:N] = country_epidemic_data['deaths']
        #Save cases
        model_data['cases_by_country'][:N] = country_epidemic_data['cases']

        return model_data

def visualize_results(datadir, outdir, country_combos, country_data, all_countries, days_to_simulate):
    '''Visualize results by reading in all information from all countries in all combinations
    of the leave one out analysis.
    '''
    #Get all data from all simulations for each country
    country_means = {"Austria":np.zeros((3,10,country_data['Austria']['days_by_country'])), #Cases,Deaths,Rt for all combinations and all days
                     "Belgium":np.zeros((3,10,country_data['Belgium']['days_by_country'])),
                     "Denmark":np.zeros((3,10,country_data['Denmark']['days_by_country'])),
                     "France":np.zeros((3,10,country_data['France']['days_by_country'])),
                     "Germany":np.zeros((3,10,country_data['Germany']['days_by_country'])),
                     "Italy":np.zeros((3,10,country_data['Italy']['days_by_country'])),
                     "Norway":np.zeros((3,10,country_data['Norway']['days_by_country'])),
                     "Spain":np.zeros((3,10,country_data['Spain']['days_by_country'])),
                     "Sweden":np.zeros((3,10,country_data['Sweden']['days_by_country'])),
                     "Switzerland":np.zeros((3,10,country_data['Switzerland']['days_by_country'])),
                     "United_Kingdom":np.zeros((3,10,country_data['United_Kingdom']['days_by_country']))
                    }

    #Loop through all country combos
    fetched_combos = {"Austria":0,"Belgium":0,"Denmark":0,"France":0, #Keep track of index for each country
                      "Germany":0,"Italy":0,"Norway":0,"Spain":0,
                      "Sweden":0,"Switzerland":0,"United_Kingdom":0}
    missing_country_order =  {"Austria":[],"Belgium":[],"Denmark":[],"France":[], #Keep track of index for each country
                              "Germany":[],"Italy":[],"Norway":[],"Spain":[],
                              "Sweden":[],"Switzerland":[],"United_Kingdom":[]}
    for i in range(len(country_combos)):
        countries = country_combos.loc[i].values
        for check in all_countries:
            if check not in countries:
                missing_country = check
        if missing_country == "United_Kingdom":
            missing_country = "United Kingdom"
        summary = pd.read_csv(datadir+'summary'+str(i+1)+'.csv')
        #Loop through all countries in combo
        for j in range(len(countries)):
            country= countries[j]
            data = country_data[country]
            end_iter = data['days_by_country']
            missing_country_order[country].append(missing_country) #Save missing country to see which was left out in the sim

            #Extract mean modeling results for country j
            means = {'prediction':[],'E_deaths':[], 'Rt':[]}
            for k in range(1,end_iter+1):
                for var in ['prediction', 'E_deaths', 'Rt']:
                    var_ij = summary[summary['Unnamed: 0']==var+'['+str(k)+','+str(j+1)+']']
                    try:
                        means[var].append(var_ij['mean'].values[0])
                    except:
                        pdb.set_trace()
            #Save data to country means
            country_means[country][0,fetched_combos[country],:]=means['prediction']
            country_means[country][1,fetched_combos[country],:]=means['E_deaths']
            country_means[country][2,fetched_combos[country],:]=means['Rt']
            fetched_combos[country]+=1 #Increase location index in np array


    #Plot alphas - influence of each mobility parameter
    covariate_names = ['retail and recreation','grocery and pharmacy', 'transit stations','workplace','residential']
    alpha_colors =  {0:'darkorange',1:'tab:purple',2:'tab:pink', 3:'tab:olive', 4:'tab:cyan'}
    for i in range(1,12): #Loop through all mobility params
        alphas = np.load(datadir+'alpha'+str(i)+'.npy')
        for j in range(5):
            fig, ax = plt.subplots(figsize=(3/2.54, 3/2.54))
            sns.distplot(alphas[2000:,j],color=alpha_colors[j]) #The first 2000 samplings are warmup
            ax.set_title(all_countries[i-1])
            if all_countries[i-1] == 'United_Kingdom':
                ax.set_title('United Kingdom')
            ax.set_xlabel('Value')
            ax.set_ylabel('Density')
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            fig.tight_layout()
            fig.savefig(outdir+'plots/LOO/'+all_countries[i-1]+'_'+str(j)+'.png', format = 'png', dpi=300)
            plt.close()


    #plot per country
    days = np.arange(0,days_to_simulate) #Days to simulate
    for country in country_means:
        means = country_means[country]
        data = country_data[country]
        dates = data['dates_by_country']
        observed_country_deaths = data['deaths_by_country']
        observed_country_cases = data['cases_by_country']
        end = data['days_by_country']#End of data for country i
        missing_order = missing_country_order[country] #Order of exclusion for LOO
        #Plot cases
        #Per day
        #
        # plot_shade_ci(days, end, dates[0], means[0,:,:], observed_country_cases, 'Cases per day',
        # outdir+'/plots/LOO/'+country+'_cases.png', missing_order)
        # #Cumulative
        # plot_shade_ci(days, end, dates[0], np.cumsum(np.array(means[0,:,:],dtype='int16'),axis=1), np.cumsum(observed_country_cases),
        # 'Cumulative cases',outdir+'/plots/LOO/'+country+'_cumulative_cases.png', missing_order)
        # #Plot Deaths
        # plot_shade_ci(days, end, dates[0],means[1,:,:],observed_country_deaths,'Deaths per day',
        # outdir+'/plots/LOO/'+country+'_deaths.png', missing_order)
        # #Plot R
        # plot_shade_ci(days, end, dates[0],means[2,:,:],'','Rt',outdir+'/plots/LOO/'+country+'_Rt.png', missing_order)
        # #Correlations
        corr = np.corrcoef(means[2,:,:])
        plot_corr(corr, missing_order, outdir+'/plots/LOO/'+country+'_Rt_corr.png', country)
        print(country+','+'Rt'+','+str(np.average(np.corrcoef(means[2,:,:]))-(10/100))) #10 of 100 will be self corr.

    return None

def plot_corr(corr, missing_order, outname, country):
    '''Plot corr matrix
    '''
    if country == "United_Kingdom":
        country = "United Kingdom"

    fig, ax = plt.subplots(figsize=(6/2.54, 6/2.54))
    im = ax.imshow(corr)
    ax.set_xticks(np.arange(10))
    ax.set_yticks(np.arange(10))
    ax.set_xticklabels(missing_order, rotation = 90)
    ax.set_yticklabels(missing_order)
    ax.set_title(country)
    fig.tight_layout()
    fig.savefig(outname, format = 'png', dpi=300)
    plt.close()

def plot_colorbar():
    '''Plots a stand alone colorbar
    '''
    fig,ax = plt.subplots(figsize=(6/2.54, 3/2.54))

    cb = matplotlib.colorbar.ColorbarBase(ax, orientation='horizontal',cmap=matplotlib.cm.viridis)
    ax.set_title('Pearson Correlation')
    fig.tight_layout()
    fig.savefig('pearson_corr_scale.png', format = 'png', dpi=300)
    plt.show()

def plot_shade_ci(x,end,start_date,y, observed_y, ylabel, outname, missing_order):
    '''Plot with shaded 95 % CI (plots both 1 and 2 std, where 2 = 95 % interval)
    '''
    country_colors = {"Austria":'k', #Cases,Deaths,Rt for all combinations and all days
                     "Belgium":'tab:blue',
                     "Denmark":'tab:orange',
                     "France":'tab:green',
                     "Germany":'darkorange',
                     "Italy":'tab:purple',
                     "Norway":'tab:brown',
                     "Spain":'tab:pink',
                     "Sweden":'tab:gray',
                     "Switzerland":'tab:olive',
                     "United Kingdom":'tab:cyan'
                    }

    dates = np.arange(start_date,np.datetime64('2020-04-20')) #Get dates - increase for longer foreacast
    forecast = len(dates)
    fig, ax = plt.subplots(figsize=(9/2.54, 6/2.54))
    #Plot observed dates
    if len(observed_y)>1:
        ax.bar(x[:end],observed_y[:end], alpha = 0.5)
    #Plot the mean for each LOO combo
    for i in range(10):
        missing_country = missing_order[i]
        #Plot so far
        ax.plot(x[:end],y[i,:end], alpha=0.2, color = country_colors[missing_country],linewidth = 2.0, label = missing_country)
        #Plot predicted dates
        ax.plot(x[end-1:forecast],y[i,end-1:forecast], alpha=0.2, color='g', linewidth = 2.0)

    #Format axis
    ax.set_ylabel(ylabel)
    ax.set_ylim([0,np.amax(y[:,:forecast])])
    xticks=np.arange(forecast-1,0,-7)
    ax.set_xticks(xticks)
    ax.set_xticklabels(dates[xticks],rotation='vertical')
    ax.legend()
    fig.tight_layout()
    fig.savefig(outname, format = 'png', dpi=300)
    plt.close()



#####MAIN#####
#Set font size
matplotlib.rcParams.update({'font.size': 6})
args = parser.parse_args()
datadir = args.datadir[0]
#Get epidemic data
epidemic_data = pd.read_csv(args.epidemic_data[0])
#Convert to datetime
epidemic_data['dateRep'] = pd.to_datetime(epidemic_data['dateRep'], format='%d/%m/%Y')
#Get everything before 19 april
epidemic_data = epidemic_data[epidemic_data['dateRep']<='2020-04-19']
country_combos = pd.read_csv(args.country_combos[0], header = None)
days_to_simulate=args.days_to_simulate[0] #Number of days to model. Increase for further forecast
outdir = args.outdir[0]
#Get data per country
country_data = {} #Save all data from all extracted country combinations
all_countries = ["Austria", "Belgium", "Denmark", "France", "Germany", "Italy", "Norway", "Spain", "Sweden", "Switzerland", "United_Kingdom"]
for country in all_countries:
    #Read data
    model_data = read_and_format_data(epidemic_data, country, days_to_simulate)
    country_data[country]=model_data

#Visualize
visualize_results(datadir, outdir, country_combos, country_data, all_countries, days_to_simulate)
