#! /usr/bin/env python3
# -*- coding: utf-8 -*-


import argparse
import sys
import os
import glob
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from scipy.stats import gamma
import numpy as np
import seaborn as sns


import pdb



#Arguments for argparse module:
parser = argparse.ArgumentParser(description = '''Visulaize results from the ICL response team model''')

parser.add_argument('--datadir', nargs=1, type= str, default=sys.stdin, help = 'Path to dir with data.')
parser.add_argument('--results_dir', nargs=1, type= str, default=sys.stdin, help = 'Path to resultsdir.')
parser.add_argument('--countries', nargs=1, type= str, default=sys.stdin, help = 'Countries to model (csv).')
parser.add_argument('--days_to_simulate', nargs=1, type= int, default=sys.stdin, help = 'Number of days to simulate.')
parser.add_argument('--end_date', nargs=1, type= str, default=sys.stdin, help = 'Up to which date to include data.')
parser.add_argument('--short_dates', nargs=1, type= str, default=sys.stdin, help = 'Short date format for plotting (csv).')
parser.add_argument('--outdir', nargs=1, type= str, default=sys.stdin, help = 'Path to outdir.')

def read_and_format_data(datadir, countries, days_to_simulate, end_date):
        '''Read in and format all data needed for the model
        '''

        #Get epidemic data
        epidemic_data = pd.read_csv(datadir+'COVID19uptodate.csv')
        #Convert to datetime
        epidemic_data['DateRep'] = pd.to_datetime(epidemic_data['DateRep'], format='%Y/%m/%d')
        #Select all data up to end_date
        epidemic_data = epidemic_data[epidemic_data['DateRep']<=end_date]
        ## get ifr
        ifr_by_country = pd.read_csv(datadir+"popt-ifr.csv")
        #SI
        serial_interval = pd.read_csv(datadir+"serial-interval.csv")


        #Model data - to be used for plotting
        stan_data = {'dates_by_country':np.zeros((days_to_simulate,len(countries)), dtype='datetime64[D]'),
                    'deaths_by_country':np.zeros((days_to_simulate,len(countries))),
                    'cases_by_country':np.zeros((days_to_simulate,len(countries))),
                    'days_by_country':np.zeros(len(countries))
                    }


        #Get data by country
        for c in range(len(countries)):
                country = countries[c]

                #Get country epidemic data
                country_epidemic_data = epidemic_data[epidemic_data['Country']==country]
                #Sort on date
                country_epidemic_data = country_epidemic_data.sort_values(by='DateRep')
                #Reset index
                country_epidemic_data = country_epidemic_data.reset_index()

                #Get all dates with at least 10 deaths
                cum_deaths = country_epidemic_data['Deaths'].cumsum()
                death_index = cum_deaths[cum_deaths>=10].index[0]
                di30 = death_index-30
                #Get part of country_epidemic_data 30 days before day with at least 10 deaths
                country_epidemic_data = country_epidemic_data.loc[di30:]
                #Reset index
                country_epidemic_data = country_epidemic_data.reset_index()

                print(country, len(country_epidemic_data), np.array(country_epidemic_data['DateRep'], dtype='datetime64[D]')[0])
                #Check that foreacast is really a forecast
                N = len(country_epidemic_data)
                stan_data['days_by_country'][c]=N
                forecast = days_to_simulate - N
                if forecast <0: #If the number of predicted days are less than the number available
                    days_to_simulate = N
                    forecast = 0
                    print('Forecast error!')
                    pdb.set_trace()

                #Save dates
                stan_data['dates_by_country'][:N,c] = np.array(country_epidemic_data['DateRep'], dtype='datetime64[D]')
                #Save deaths
                stan_data['deaths_by_country'][:N,c] = country_epidemic_data['Deaths']
                #Save cases
                stan_data['cases_by_country'][:N,c] = country_epidemic_data['Cases']

        return stan_data

def fix_covariates(covariates):
        '''Change dates so all covariates that happen after the lockdown
        to have the same date as the lockdown. Also add the covariate "any intervention"
        '''
        NPI = ['schools_universities',  'public_events',
        'social_distancing_encouraged', 'self_isolating_if_ill']
        #Add covariate for first intervention
        covariates['first_intervention'] = ''

        for i in range(len(covariates)):
                row = covariates.iloc[i]
                lockdown = row['lockdown']
                first_inter = '2021-04-01'
                for n in NPI:
                        if row[n] < first_inter:
                                first_inter = row[n]
                        if row[n] > lockdown:
                                covariates.at[i,n] = lockdown

                covariates.at[i,'first_intervention'] = first_inter
        return covariates


def plot_posterior(matrix, countries, param):
    '''Visualize the posterior distributions of different parameters
    '''
    for i in range(matrix.shape[1]):
        fig, ax = plt.subplots(figsize=(3/2.54, 3/2.54))
        sns.distplot(matrix[2000:,i]) #The first 2000 samplings are warmup
        ax.set_title(countries[i])
        if countries[i] == 'United_Kingdom':
            ax.set_title('United Kingdom')
        ax.set_xlabel(param)
        #ax.set_xlim([1.5,5.5])
        ax.axvline(x=3.28, ymin=0, ymax=2, linestyle='--',linewidth=1)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        fig.tight_layout()
        fig.savefig(outdir+'figures/posterior/'+param+'_'+countries[i]+'.png', format = 'png',dpi=300 )
        plt.close()


def visualize_results(outdir, datadir, results_dir, countries, stan_data, days_to_simulate, short_dates):
    '''Visualize results
    '''
    #Investigate parameter posterior distributions
    param = 'mu'
    param_matrix = np.load(results_dir+'mu.npy', allow_pickle=True)
    plot_posterior(param_matrix, countries, 'mean R0')

    #Plot last intervention
    try:
        last_intervention = np.load(results_dir+'last_intervention.npy', allow_pickle=True)
        for i in range(len(countries)):
            fig, ax = plt.subplots(figsize=(6/2.54, 4.5/2.54))
            sns.distplot(100*(1-np.exp(-last_intervention[8000:,i])))
            print(countries[i]+' last intervention', np.median(100*(1-np.exp(-last_intervention[8000:,i]))))
            ax.set_ylabel('Density')
            ax.set_xlabel("Relative % reduction in Rt")
            ax.set_title(countries[i]+' last intervention')
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            fig.tight_layout()
            fig.savefig(outdir+'figures/posterior/'+countries[i]+'_last_intervention.png', format='png', dpi=300)
            plt.close()
    except:
        print('No last intervention')


    #Plot lockdown effect (all but Sweden)
    try:
        lockdown = np.load(results_dir+'lockdown.npy', allow_pickle=True)

        for i in range(len(countries)):
            fig, ax = plt.subplots(figsize=(4.5/2.54, 4.5/2.54))
            sns.distplot(100*(1-np.exp(-lockdown[8000:,i])))
            ax.set_ylabel('Density')
            ax.set_xlabel("Relative % reduction in Rt")
            ax.set_title(countries[i])
            ax.set_xlim([-100,100])
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            fig.tight_layout()
            fig.savefig(outdir+'figures/posterior/'+countries[i]+'_lockdown.png', format='png', dpi=300)
            plt.close()
    except:
        print('No lockdown')
    #Read in data
    #For models fit using MCMC, also included in the summary are the
    #Monte Carlo standard error (se_mean), the effective sample size (n_eff),
    #and the R-hat statistic (Rhat).
    summary = pd.read_csv(results_dir+'summary.csv')
    alphas = np.load(results_dir+'alpha.npy', allow_pickle=True)
    phi = np.load(results_dir+'phi.npy', allow_pickle=True)
    days = np.arange(0,days_to_simulate) #Days to simulate
    #Plot rhat
    fig, ax = plt.subplots(figsize=(6/2.54, 4.5/2.54))
    ax.hist(summary['Rhat'])
    ax.set_ylabel('Count')
    ax.set_xlabel("Rhat")
    fig.savefig(outdir+'figures/rhat.png', format='png', dpi=300)
    plt.close()

    #Plot alpha posteriors
    alpha_colors = {0:'tab:red',1:'tab:purple',2:'tab:pink', 3:'tab:olive', 4:'tab:cyan',5:'b',6:'k'}
    alpha_titles = {0:'Schools and Universities',1:'Self isolating if ill',2:'Public events',3:'First intervention',4:'Lockdown',5:'Social distancing encouraged',6:'Last intervention'}
    alpha_names = {0:'schools_universities',1:'self_isolating_if_ill',2:'public_events',3:'first_intervention',4:'lockdown',5:'social_distancing_encouraged',6:'last_intervention'}

    for i in range(7):
        fig, ax = plt.subplots(figsize=(6/2.54, 4.5/2.54))
        sns.distplot(100*(1-np.exp(-alphas[8000:,i])),color=alpha_colors[i]) #The first 2000 samplings are warmup
        print(alpha_titles[i], np.median(100*(1-np.exp(-alphas[8000:,i]))))
        ax.set_title(alpha_titles[i])
        ax.set_ylabel('Density')
        ax.set_xlabel('Relative % reduction in Rt')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        fig.tight_layout()
        fig.savefig(outdir+'figures/posterior/alpha_'+alpha_names[i]+'.png', format = 'png',dpi=300 )
        plt.close()

    #plot per country
    #Read in intervention dates
    #NPI and their implementation dates
    covariates = pd.read_csv(datadir+'interventions.csv')
    #Change dates
    intervention_df = fix_covariates(covariates)
    for i in range(1,len(countries)+1):
        country= countries[i-1]
        country_npi = intervention_df[intervention_df['Country']==country]
        #Get att stan data for country i
        dates = stan_data['dates_by_country'][:,i-1]
        observed_country_deaths = stan_data['deaths_by_country'][:,i-1]
        observed_country_cases = stan_data['cases_by_country'][:,i-1]
        end = int(stan_data['days_by_country'][i-1])


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
        plot_shade_ci(country,days, end, dates[0], means['prediction'], observed_country_cases,lower_bound['prediction'],
        higher_bound['prediction'], lower_bound25['prediction'], higher_bound75['prediction'], 'Cases per day',
        outdir+'figures/'+country+'_cases.png',country_npi, short_dates)
        #Cumulative
        plot_shade_ci(country,days, end, dates[0], np.cumsum(means['prediction']), np.cumsum(observed_country_cases),np.cumsum(lower_bound['prediction']),
        np.cumsum(higher_bound['prediction']), np.cumsum(lower_bound25['prediction']), np.cumsum(higher_bound75['prediction']),
        'Cumulative cases',outdir+'figures/'+country+'_cumulative_cases.png',country_npi, short_dates)
        #Plot Deaths
        #Per day
        plot_shade_ci(country,days, end,dates[0],means['E_deaths'],observed_country_deaths, lower_bound['E_deaths'], higher_bound['E_deaths'],
        lower_bound25['E_deaths'], higher_bound75['E_deaths'], 'Deaths per day',
        outdir+'figures/'+country+'_deaths.png',country_npi, short_dates)
        #Cumulative
        plot_shade_ci(country,days, end,dates[0],np.cumsum(means['E_deaths']),np.cumsum(observed_country_deaths), np.cumsum(lower_bound['E_deaths']), np.cumsum(higher_bound['E_deaths']),
        np.cumsum(lower_bound25['E_deaths']), np.cumsum(higher_bound75['E_deaths']), 'Cumulative deaths',
        outdir+'figures/'+country+'_cumulative_deaths.png',country_npi, short_dates)
        #Plot R
        plot_shade_ci(country,days,end,dates[0],means['Rt'],'', lower_bound['Rt'], higher_bound['Rt'], lower_bound25['Rt'],
        higher_bound75['Rt'],'Rt',outdir+'figures/'+country+'_Rt.png',country_npi, short_dates)


    return None


def plot_shade_ci(country,x,end,start_date,y, observed_y, lower_bound, higher_bound,lower_bound25, higher_bound75,ylabel,outname,country_npi, short_dates):
    '''Plot with shaded 95 % CI (plots both 1 and 2 std, where 2 = 95 % interval)
    '''
    dates = np.arange(start_date,np.datetime64('2020-05-05')) #Get dates - increase for longer foreacast
    selected_short_dates = np.array(short_dates[short_dates['np_date'].isin(dates)]['short_date']) #Get short version of dates
    if len(dates) != len(selected_short_dates):
        pdb.set_trace()
    fig, ax1 = plt.subplots(figsize=(6/2.54, 4.5/2.54))
    #Plot observed dates
    if len(observed_y)>1:
        ax1.bar(x[:end],observed_y[:end], alpha = 0.5) #3 week forecast
    ax1.plot(x[:end],y[:end], alpha=0.5, color='b', label='Simulation', linewidth = 2.0)
    ax1.fill_between(x[:end], lower_bound[:end], higher_bound[:end], color='cornflowerblue', alpha=0.4)
    ax1.fill_between(x[:end], lower_bound25[:end], higher_bound75[:end], color='cornflowerblue', alpha=0.6)


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
    if ylabel == 'Rt':
        y_npi = max(y[:end])*0.9
    else:
        y_npi = max(higher_bound[:end])*0.9
    y_step = y_npi/15
    npi_xvals = [] #Save npi xvals to not plot over each npi
    for npi in NPI:
        try:
            xval = np.where(dates==np.datetime64(country_npi[npi].values[0]))[0][0]
        except:
            print(npi)
            continue
        ax1.axvline(xval, linestyle='--', linewidth=0.5, c= 'b')
        if xval in npi_xvals:
            ax1.scatter(xval, y_npi-y_step, s = 12, marker = NPI_markers[npi], color = NPI_colors[npi])
        else:
            ax1.scatter(xval, y_npi, s = 12, marker = NPI_markers[npi], color = NPI_colors[npi])
        npi_xvals.append(xval)


    #Plot formatting
    #ax1
    #ax1.legend(loc='lower left', frameon=False, markerscale=2)
    ax1.set_ylabel(ylabel)
    if country=='United_Kingdom':
        country = 'United Kingdom'
    ax1.set_title(country)
    #ax1.set_ylim([0,max(higher_bound[:end])])
    xticks=np.arange(end-1,0,-14)
    ax1.set_xticks(xticks)
    try:
        ax1.set_xticklabels(selected_short_dates[xticks],rotation='vertical')
    except:
        pdb.set_trace()
    #Plot a dashed line at Rt=1
    if ylabel=='Rt':
        ax1.hlines(1,0,max(xticks),linestyles='dashed',linewidth=1)

    ax1.spines['top'].set_visible(False)
    fig.tight_layout()
    fig.savefig(outname, format = 'png',dpi=300 )
    plt.close()



#####MAIN#####
#Set font size
matplotlib.rcParams.update({'font.size': 7})
args = parser.parse_args()
datadir = args.datadir[0]
results_dir = args.results_dir[0]
countries = args.countries[0].split(',')
days_to_simulate=args.days_to_simulate[0] #Number of days to model. Increase for further forecast
end_date=args.end_date[0]
short_dates = pd.read_csv(args.short_dates[0])
#Make sure the np dates are in the correct format
short_dates['np_date'] = pd.to_datetime(short_dates['np_date'], format='%Y/%m/%d')
outdir = args.outdir[0]


#Read data
stan_data = read_and_format_data(datadir, countries, days_to_simulate, end_date)

#Visualize
visualize_results(outdir, datadir, results_dir, countries, stan_data, days_to_simulate, short_dates)
