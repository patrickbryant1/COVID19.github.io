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
parser = argparse.ArgumentParser(description = '''Visuaize results from model using google mobility data and most of the ICL response team model''')

parser.add_argument('--datadir', nargs=1, type= str, default=sys.stdin, help = 'Path to outdir.')
parser.add_argument('--countries', nargs=1, type= str, default=sys.stdin, help = 'Countries to model (csv).')
parser.add_argument('--days_to_simulate', nargs=1, type= int, default=sys.stdin, help = 'Number of days to simulate.')
parser.add_argument('--end_date', nargs=1, type= str, default=sys.stdin, help = 'Up to which date to include data.')
parser.add_argument('--short_dates', nargs=1, type= str, default=sys.stdin, help = 'Short date format for plotting (csv).')
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
        stan_data = {'dates_by_country':np.zeros((days_to_simulate,len(countries)), dtype='datetime64[D]'),
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
                country_cov_data = mobility_data[mobility_data['country_region']==country]
                if country == 'United_Kingdom': #Different assignments for UK
                    country_cov_data = mobility_data[mobility_data['country_region']=='United Kingdom']
                #Get whole country - no subregion
                country_cov_data =  country_cov_data[country_cov_data['sub_region_1'].isna()]
                #Get matching dates
                country_cov_data = country_cov_data[country_cov_data['date'].isin(country_epidemic_data['dateRep'])]
                end_date = max(country_cov_data['date']) #Last date for mobility data
                for name in covariate_names:
                    country_epidemic_data.loc[country_epidemic_data.index,name] = 0 #Set all to 0
                    for d in range(len(country_epidemic_data)): #loop through all country data
                        row_d = country_epidemic_data.loc[d]
                        date_d = row_d['dateRep'] #Extract date
                        try:
                            change_d = np.round(float(country_cov_data[country_cov_data['date']==date_d][name].values[0])/100, 2) #Match mobility change on date
                            if not np.isnan(change_d):
                                country_epidemic_data.loc[d,name] = change_d #Add to right date in country data
                        except:
                            continue #Date too far ahead


                    #Add the latest available mobility data to all remaining days (including the forecast days)
                    country_epidemic_data.loc[country_epidemic_data['dateRep']>=end_date, name]=change_d
                    cov_i = np.zeros(days_to_simulate)
                    cov_i[:N] = np.array(country_epidemic_data[name])
                    #Add covariate info to forecast
                    cov_i[N:days_to_simulate]=cov_i[N-1]
                    stan_data[name][:,c] = cov_i

        return stan_data

def plot_posterior(matrix, countries, param):
    '''Visualize the posterior distributions of different parameters
    '''
    for i in range(matrix.shape[1]):
        fig, ax = plt.subplots(figsize=(3/2.54, 3/2.54))
        sns.distplot(matrix[2000:,i]) #The first 2000 samplings are warmup
        ax.set_title(countries[i])
        ax.set_xlabel(param)
        ax.set_xlim([1.5,5.5])
        ax.axvline(x=2.79, ymin=0, ymax=2, linestyle='--',linewidth=1)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        fig.tight_layout()
        fig.savefig(outdir+'plots/posterior/'+param+'_'+countries[i]+'.png', format = 'png')
        plt.close()


def visualize_results(outdir, countries, stan_data, days_to_simulate, short_dates):
    '''Visualize results
    '''
    #Investigate parameter posterior distributions
    param = 'mu'
    param_matrix = np.load(outdir+'mu.npy', allow_pickle=True)
    plot_posterior(param_matrix, countries, 'mean R0')

    #Read in data
    #For models fit using MCMC, also included in the summary are the
    #Monte Carlo standard error (se_mean), the effective sample size (n_eff),
    #and the R-hat statistic (Rhat).
    summary = pd.read_csv(outdir+'summary.csv')
    alphas = np.load(outdir+'alpha.npy', allow_pickle=True)
    phi = np.load(outdir+'phi.npy', allow_pickle=True)
    days = np.arange(0,days_to_simulate) #Days to simulate
    #Plot rhat
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.hist(summary['Rhat'])
    ax.set_ylabel('Count')
    ax.set_xlabel("Rhat")
    fig.savefig(outdir+'plots/rhat.png', format='png', dpi=300)
    plt.close()

    #Plot values from each iteration as r function mcmc_parcoord
    mcmc_parcoord(np.concatenate([alphas,np.expand_dims(phi,axis=1)], axis=1), covariate_names+['phi'], outdir)

    #Plot alpha posteriors
    fig, ax = plt.subplots(figsize=(6/2.54, 4/2.54))
    alpha_colors = {0:'tab:red',1:'tab:purple',2:'tab:pink', 3:'tab:olive', 4:'tab:cyan'}
    alpha_names = {0:'retail and recreation',1:'grocery and pharmacy',2:'transit stations',3:'workplace',4:'residential'}

    for i in range(5):
        fig, ax = plt.subplots(figsize=(6/2.54, 4.5/2.54))
        sns.distplot(alphas[2000:,i],color=alpha_colors[i]) #The first 2000 samplings are warmup
        ax.set_title(alpha_names[i])
        ax.set_ylabel('Density')
        ax.set_xlabel('Value')
        ax.axvline(x=np.median(alphas[2000:,i]), ymin=0, ymax=20, linestyle='--',linewidth=1)
        print(np.round(np.median(alphas[2000:,i]),2))
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        fig.tight_layout()
        fig.savefig(outdir+'plots/posterior/alpha_'+alpha_names[i]+'.png', format = 'png')
        plt.close()

    #plot per country
    #Read in intervention dates
    intervention_df = pd.read_csv(datadir+'interventions_only.csv')
    result_file = open(outdir+'plots/summary_means.csv', 'w')
    result_file.write('Country,Epidemic Start,R0 at start,R0 29 Mar,R0 Apr 19\n') #Write headers
    for i in range(1,len(countries)+1):
        country= countries[i-1]
        country_npi = intervention_df[intervention_df['Country']==country]
        #Get att stan data for country i
        dates = stan_data['dates_by_country'][:,i-1]
        observed_country_deaths = stan_data['deaths_by_country'][:,i-1]
        observed_country_cases = stan_data['cases_by_country'][:,i-1]
        end = int(stan_data['days_by_country'][i-1])-21 #3 week forecast #End of data for country i
        country_retail = stan_data['retail_and_recreation_percent_change_from_baseline'][:,i-1]
        country_grocery= stan_data['grocery_and_pharmacy_percent_change_from_baseline'][:,i-1]
        country_transit = stan_data['transit_stations_percent_change_from_baseline'][:,i-1]
        country_work = stan_data['workplaces_percent_change_from_baseline'][:,i-1]
        country_residential = stan_data['residential_percent_change_from_baseline'][:,i-1]
        #Print final mobility value
        print(country,country_grocery[end-1])

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
        outdir+'plots/'+country+'_cases.png',country_npi, country_retail, country_grocery, country_transit, country_work, country_residential, short_dates)
        #Cumulative
        plot_shade_ci(country,days, end, dates[0], np.cumsum(means['prediction']), np.cumsum(observed_country_cases),np.cumsum(lower_bound['prediction']),
        np.cumsum(higher_bound['prediction']), np.cumsum(lower_bound25['prediction']), np.cumsum(higher_bound75['prediction']),
        'Cumulative cases',outdir+'plots/'+country+'_cumulative_cases.png',country_npi, country_retail, country_grocery, country_transit, country_work, country_residential, short_dates)
        #Plot Deaths
        #Per day
        plot_shade_ci(country,days, end,dates[0],means['E_deaths'],observed_country_deaths, lower_bound['E_deaths'], higher_bound['E_deaths'],
        lower_bound25['E_deaths'], higher_bound75['E_deaths'], 'Deaths per day',
        outdir+'plots/'+country+'_deaths.png',country_npi, country_retail, country_grocery, country_transit, country_work, country_residential, short_dates)
        #Cumulative
        plot_shade_ci(country,days, end,dates[0],np.cumsum(means['E_deaths']),np.cumsum(observed_country_deaths), np.cumsum(lower_bound['E_deaths']), np.cumsum(higher_bound['E_deaths']),
        np.cumsum(lower_bound25['E_deaths']), np.cumsum(higher_bound75['E_deaths']), 'Cumulative deaths',
        outdir+'plots/'+country+'_cumulative_deaths.png',country_npi, country_retail, country_grocery, country_transit, country_work, country_residential, short_dates)
        #Plot R
        plot_shade_ci(country,days,end,dates[0],means['Rt'],'', lower_bound['Rt'], higher_bound['Rt'], lower_bound25['Rt'],
        higher_bound75['Rt'],'Rt',outdir+'plots/'+country+'_Rt.png',country_npi,
        country_retail, country_grocery, country_transit, country_work, country_residential, short_dates)

        #Print R mean at beginning and end of model
        try:
            result_file.write(country+','+str(dates[0])+','+str(np.round(means['Rt'][0],2))+','+str(np.round(means['Rt'][end],2))+','+str(np.round(means['Rt'][end+20],2))+'\n')#Print for table
        except:
            pdb.set_trace()
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

def plot_shade_ci(country,x,end,start_date,y, observed_y, lower_bound, higher_bound,lower_bound25, higher_bound75,ylabel,outname,country_npi, country_retail, country_grocery, country_transit, country_work, country_residential, short_dates):
    '''Plot with shaded 95 % CI (plots both 1 and 2 std, where 2 = 95 % interval)
    '''
    dates = np.arange(start_date,np.datetime64('2020-04-20')) #Get dates - increase for longer foreacast
    selected_short_dates = np.array(short_dates[short_dates['np_date'].isin(dates)]['short_date']) #Get short version of dates
    if len(dates) != len(selected_short_dates):
        pdb.set_trace()
    forecast = end+21
    fig, ax1 = plt.subplots(figsize=(6/2.54, 4.5/2.54))
    #Plot observed dates
    if len(observed_y)>1:
        ax1.bar(x[:forecast],observed_y[:forecast], alpha = 0.5) #3 week forecast
    ax1.plot(x[:end],y[:end], alpha=0.5, color='b', label='Simulation', linewidth = 2.0)
    ax1.fill_between(x[:end], lower_bound[:end], higher_bound[:end], color='cornflowerblue', alpha=0.4)
    ax1.fill_between(x[:end], lower_bound25[:end], higher_bound75[:end], color='cornflowerblue', alpha=0.6)

    #Plot predicted dates
    ax1.plot(x[end:forecast],y[end:forecast], alpha=0.5, color='g', label='Forecast', linewidth = 2.0)
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
    if ylabel == 'Rt':
        y_npi = max(y[:forecast])*0.9
    else:
        y_npi = max(higher_bound[:forecast])*0.9
    y_step = y_npi/15
    npi_xvals = [] #Save npi xvals to not plot over each npi
    for npi in NPI:
        if country_npi[npi].values[0] == '0': #If nan
            continue
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
    ax2.plot(x[:end],country_retail[:end], alpha=0.5, color='tab:red', linewidth = 2.0)
    ax2.plot(x[:end],country_grocery[:end], alpha=0.5, color='tab:purple', linewidth = 2.0)
    ax2.plot(x[:end],country_transit[:end], alpha=0.5, color='tab:pink', linewidth = 2.0)
    ax2.plot(x[:end],country_work[:end], alpha=0.5, color='tab:olive', linewidth = 2.0)
    ax2.plot(x[:end],country_residential[:end], alpha=0.5, color='tab:cyan', linewidth = 2.0)

    #Plot formatting
    #ax1
    #ax1.legend(loc='lower left', frameon=False, markerscale=2)
    ax1.set_ylabel(ylabel)
    if country=='United_Kingdom':
        country = 'United Kingdom'
    ax1.set_title(country)
    ax1.set_ylim([0,max(higher_bound[:forecast])])
    xticks=np.arange(forecast-1,0,-14)
    ax1.set_xticks(xticks)
    ax1.set_xticklabels(selected_short_dates[xticks],rotation='vertical')
    #Plot a dashed line at Rt=1
    if ylabel=='Rt':
        ax1.hlines(1,0,max(xticks),linestyles='dashed',linewidth=1)
        ax1.set_ylim([0,max(y[:forecast])])
    #ax1.set_yticks(np.arange(0,max(higher_bound[:forecast]),))
    #ax2
    #ax2.set_ylabel('Relative change')
    ax2.set_ylim([-1,0.4])
    ax2.set_yticks([-1,-0.5,0,0.4])
    ax1.spines['top'].set_visible(False)
    ax2.spines['top'].set_visible(False)
    fig.tight_layout()
    fig.savefig(outname, format = 'png')
    plt.close()



#####MAIN#####
#Set font size
matplotlib.rcParams.update({'font.size': 7})
args = parser.parse_args()
datadir = args.datadir[0]
countries = args.countries[0].split(',')
days_to_simulate=args.days_to_simulate[0] #Number of days to model. Increase for further forecast
end_date=args.end_date[0]
short_dates = pd.read_csv(args.short_dates[0])
#Make sure the np dates are in the correct format
short_dates['np_date'] = pd.to_datetime(short_dates['np_date'], format='%Y/%m/%d')
outdir = args.outdir[0]
#Covariate names
covariate_names = ['retail_and_recreation_percent_change_from_baseline',
'grocery_and_pharmacy_percent_change_from_baseline',
'transit_stations_percent_change_from_baseline',
'workplaces_percent_change_from_baseline',
'residential_percent_change_from_baseline']

#Read data
stan_data = read_and_format_data(datadir, countries, days_to_simulate, end_date, covariate_names)

#Visualize
visualize_results(outdir, countries, stan_data, days_to_simulate, short_dates)

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

fig, ax = plt.subplots(figsize=(6/2.54,2.25/2.54))
i=1
for npi in NPI:
    ax.scatter(1,i,marker=NPI_markers[npi], color = NPI_colors[npi])
    ax.text(1.001,i,NPI_labels[npi])
    i+=1
ax.set_ylim([0,6])
ax.set_xlim([0.999,1.02])
ax.axis('off')
fig.savefig(outdir+'plots/NPI_markers.png', format = 'png')

#Mobility
covariate_colors = {'retail and recreation':'tab:red','grocery and pharmacy':'tab:purple', 'transit stations':'tab:pink','workplace':'tab:olive','residential':'tab:cyan'}
fig, ax = plt.subplots(figsize=(6/2.54,2.25/2.54))
i=5
for cov in covariate_colors:
    ax.plot([1,1.8],[i]*2, color = covariate_colors[cov], linewidth=4)
    ax.text(2.001,i,cov)
    i-=1
ax.set_xlim([0.999,3.9])
ax.axis('off')
fig.savefig(outdir+'plots/mobility_markers.png', format = 'png')

#Simulation and forecast
fig, ax = plt.subplots(figsize=(6/2.54,2.25/2.54))
ax.plot([1,1.8],[1.5]*2, color = 'b', linewidth=8)
ax.text(2.001,1.5,'Simulation')
ax.plot([1,1.8],[1.45]*2, color ='g', linewidth=8)
ax.text(2.001,1.45,'Forecast')
ax.set_xlim([0.999,3.02])
ax.set_ylim([1.42,1.52])
ax.axis('off')
fig.savefig(outdir+'plots/foreacast_markers.png', format = 'png')
