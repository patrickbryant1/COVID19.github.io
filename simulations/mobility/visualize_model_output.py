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
parser = argparse.ArgumentParser(description = '''Visuaize results from model using google mobility data and most of the ICL response team model''')

parser.add_argument('--datadir', nargs=1, type= str, default=sys.stdin, help = 'Path to outdir.')
parser.add_argument('--countries', nargs=1, type= str, default=sys.stdin, help = 'Countries to model (csv).')
parser.add_argument('--days_to_simulate', nargs=1, type= int, default=sys.stdin, help = 'Number of days to simulate.')
parser.add_argument('--outdir', nargs=1, type= str, default=sys.stdin, help = 'Path to outdir.')

def read_and_format_data(datadir, countries, days_to_simulate):
        '''Read in and format all data needed for the model
        '''

        #Get epidemic data
        epidemic_data = pd.read_csv(datadir+'ecdc_20200412.csv')
        #Convert to datetime
        epidemic_data['dateRep'] = pd.to_datetime(epidemic_data['dateRep'], format='%d/%m/%Y')
        ## get CFR
        cfr_by_country = pd.read_csv(datadir+"weighted_fatality.csv")
        #SI
        serial_interval = pd.read_csv(datadir+"serial_interval.csv")

        #Model data - to be used for plotting
        stan_data = {'dates_by_country':np.zeros((days_to_simulate,len(countries)), dtype='datetime64[D]'),
                    'deaths_by_country':np.zeros((days_to_simulate,len(countries))),
                    'cases_by_country':np.zeros((days_to_simulate,len(countries))),
                    'days_by_country':np.zeros(len(countries)),
                    'retail':np.zeros((days_to_simulate,len(countries))),
                    'grocery':np.zeros((days_to_simulate,len(countries))),
                    'transit':np.zeros((days_to_simulate,len(countries))),
                    'work':np.zeros((days_to_simulate,len(countries))),
                    'residential':np.zeros((days_to_simulate,len(countries))),
                    }


        #Covariate names
        covariate_names = ['retail','grocery','transit','work','residential']
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
                stan_data['days_by_country'][c]=N
                forecast = days_to_simulate - N
                if forecast <0: #If the number of predicted days are less than the number available
                    days_to_simulate = N
                    forecast = 0
                    print('Forecast error!')
                    pdb.set_trace()

                #Save dates
                stan_data['dates_by_country'][:N,c] = np.array(country_epidemic_data['dateRep'], dtype='datetime64[D]')
                #Save deaths
                stan_data['deaths_by_country'][:N,c] = country_epidemic_data['deaths']
                #Save cases
                stan_data['cases_by_country'][:N,c] = country_epidemic_data['cases']

                #Covariates - assign the same shape as others (days_to_simulate)
                #Mobility data from Google
                geoId = country_epidemic_data['geoId'].values[0]
                for name in covariate_names:
                    country_cov_name = pd.read_csv(datadir+'europe/'+geoId+'-'+name+'.csv')
                    country_cov_name['Date'] = pd.to_datetime(country_cov_name['Date'])
                    country_epidemic_data.loc[country_epidemic_data.index,name] = 0 #Set all to 0
                    end_date = max(country_cov_name['Date']) #Last date for mobility data
                    for d in range(len(country_epidemic_data)): #loop through all country data
                        row_d = country_epidemic_data.loc[d]
                        date_d = row_d['dateRep'] #Extract date
                        try:
                            change_d = np.round(float(country_cov_name[country_cov_name['Date']==date_d]['Change'].values[0])/100, 2) #Match mobility change on date
                            if not np.isnan(change_d):
                                country_epidemic_data.loc[d,name] = change_d #Add to right date in country data
                        except:
                            continue

                    #Add the latest available mobility data to all remaining days (including the forecast days)
                    country_epidemic_data.loc[country_epidemic_data['dateRep']>=end_date, name]=change_d
                    cov_i = np.zeros(days_to_simulate)
                    cov_i[:N] = np.array(country_epidemic_data[name])
                    #Add covariate info to forecast
                    cov_i[N:days_to_simulate]=cov_i[N-1]
                    stan_data[name][:,c] = cov_i

        return stan_data

def visualize_results(outdir, countries, stan_data, days_to_simulate):
    '''Visualize results
    '''
    #params = ['mu', 'alpha', 'kappa', 'y', 'phi', 'tau', 'convolution', 'prediction',
    #'E_deaths', 'Rt', 'lp0', 'lp1', 'convolution0', 'prediction0', 'E_deaths0', 'lp__']
    #lp0[i,m] = neg_binomial_2_log_lpmf(deaths[i,m] | E_deaths[i,m],phi);
    #lp1[i,m] = neg_binomial_2_log_lpmf(deaths[i,m] | E_deaths0[i,m],phi);
    #'prediction0', 'E_deaths0' = w/o mobility changes

    #Read in data
    #For models fit using MCMC, also included in the summary are the
    #Monte Carlo standard error (se_mean), the effective sample size (n_eff),
    #and the R-hat statistic (Rhat).
    summary = pd.read_csv(outdir+'summary.csv')
    cases = np.load(outdir+'prediction.npy', allow_pickle=True)
    deaths = np.load(outdir+'E_deaths.npy', allow_pickle=True)
    Rt =  np.load(outdir+'Rt.npy', allow_pickle=True)
    alphas = np.load(outdir+'alpha.npy', allow_pickle=True)
    phi = np.load(outdir+'phi.npy', allow_pickle=True)
    days = np.arange(0,days_to_simulate) #Days to simulate
    #Plot rhat
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.hist(summary['Rhat'])
    ax.set_ylabel('Count')
    ax.set_xlabel("Rhat")
    fig.savefig(outdir+'plots/rhat.png', format='png')
    plt.close()

    #Plot values from each iteration as r function mcmc_parcoord
    covariate_names = ['','retail and recreation','grocery and pharmacy', 'transit stations','workplace','residential']
    mcmc_parcoord(np.concatenate([alphas,np.expand_dims(phi,axis=1)], axis=1), covariate_names+['phi'], outdir)

    #Plot alpha (Rt = R0*-exp(sum{mob_change*alpha1-6}))

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
    intervention_df = pd.read_csv(datadir+'interventions_only.csv')
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

def mcmc_parcoord(cat_array, xtick_labels, outdir):
    '''Plot parameters for each iteration next to each other as in the R fucntion mcmc_parcoord
    '''
    xtick_labels.insert(0,'')
    fig, ax = plt.subplots(figsize=(8, 8))
    for i in range(2000,cat_array.shape[0]): #loop through all iterations
            ax.plot(np.arange(cat_array.shape[1]), cat_array[i,:], color = 'k', alpha = 0.1)
    ax.plot(np.arange(cat_array.shape[1]), np.median(cat_array, axis = 0), color = 'r', alpha = 1)
    ax.set_xticklabels(xtick_labels,rotation='vertical')
    ax.set_ylim([-5,20])
    plt.tight_layout()
    fig.savefig(outdir+'plots/mcmc_parcoord.png', format = 'png')
    plt.close()

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
    for npi in NPI:
        xval = np.where(dates==np.datetime64(country_npi[npi].values[0]))[0][0]
        ax1.axvline(xval, linestyle='--', linewidth=0.5, c= 'b')
        if xval in npi_xvals:
            ax1.scatter(xval, y_npi-y_step, s = 12, marker = NPI_markers[npi], color = NPI_colors[npi])
        else:
            ax1.scatter(xval, y_npi, s = 12, marker = NPI_markers[npi], color = NPI_colors[npi])
        npi_xvals.append(xval)


    #Plot mobility data
    #Use a twin of the other x axis
    ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis
    ax2.plot(x[:end],country_retail[:end], alpha=0.5, color='tab:red', label='retail and recreation', linewidth = 1.0)
    ax2.plot(x[:end],country_grocery[:end], alpha=0.5, color='tab:purple', label='grocery and pharmacy', linewidth = 1.0)
    ax2.plot(x[:end],country_transit[:end], alpha=0.5, color='tab:pink', label='transit stations', linewidth = 1.0)
    ax2.plot(x[:end],country_work[:end], alpha=0.5, color='tab:olive', label='workplace', linewidth = 1.0)
    ax2.plot(x[:end],country_residential[:end], alpha=0.5, color='tab:cyan', label='residential', linewidth = 1.0)

    #Plot formatting
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
countries = args.countries[0].split(',')
days_to_simulate=args.days_to_simulate[0] #Number of days to model. Increase for further forecast
outdir = args.outdir[0]
#Read data
stan_data = read_and_format_data(datadir, countries, days_to_simulate)
#Visualize
visualize_results(outdir, countries, stan_data, days_to_simulate)

#Plot marker explanation
#NPIs
NPI = ['public_events', 'schools_universities',  'lockdown',
    'social_distancing_encouraged', 'self_isolating_if_ill']
NPI_labels = {'schools_universities':'schools and universities',  'public_events': 'public events', 'lockdown': 'lockdown',
    'social_distancing_encouraged':'social distancing encouraged', 'self_isolating_if_ill':'self isolating if ill'}
NPI_markers = {'schools_universities':'*',  'public_events': 'X', 'lockdown': 's',
    'social_distancing_encouraged':'p', 'self_isolating_if_ill':'d'}
NPI_colors = {'schools_universities':'k',  'public_events': 'blueviolet', 'lockdown': 'mediumvioletred',
    'social_distancing_encouraged':'maroon', 'self_isolating_if_ill':'darkolivegreen'}

fig, ax = plt.subplots(figsize=(4,2))
i=1
for npi in NPI:
    ax.scatter(1,i,marker=NPI_markers[npi], color = NPI_colors[npi])
    ax.text(1.001,i,NPI_labels[npi])
    i+=1
ax.set_xlim([0.999,1.02])
ax.axis('off')
fig.savefig(outdir+'plots/NPI_markers', format = 'png')
