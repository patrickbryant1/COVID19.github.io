#! /usr/bin/env python3
# -*- coding: utf-8 -*-


import argparse
import sys
import os
import re
import glob
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from scipy.stats import gamma
import numpy as np
import seaborn as sns
import pystan
import arviz as az

import pdb



#Arguments for argparse module:
parser = argparse.ArgumentParser(description = '''Simulate using google mobility data and most of the ICL response team model''')

parser.add_argument('--datadir', nargs=1, type= str, default=sys.stdin, help = 'Path to outdir.')
parser.add_argument('--outdir', nargs=1, type= str, default=sys.stdin, help = 'Path to outdir.')

###FUNCTIONS###

###DISTRIBUTIONS###
def conv_gamma_params(mean,std):
        '''Returns converted shape and scale params
        shape (α) = 1/std^2
        scale (β) = mean/shape
        '''
        shape = 1/(std*std)
        scale = mean/shape

        return shape,scale

def infection_to_death():
        '''Simulate the time from infection to death: Infection --> Onset --> Death'''
        #Infection to death: sum of ito and otd
        itd_shape, itd_scale = conv_gamma_params((5.1+18.8), (0.45))
        itd = gamma(a=itd_shape, scale = itd_scale) #a=shape
        return itd

def serial_interval_distribution():
        '''Models the the time between when a person gets infected and when
        they subsequently infect another other people
        '''
        serial_shape, serial_scale = conv_gamma_params(6.5,0.62)
        serial = gamma(a=serial_shape, scale = serial_scale) #a=shape

        return serial

def read_stupid_csv(csvfile):
    '''Read and format all mobility data
    '''
    extracted_lines = []
    print(csvfile)
    with open(csvfile) as file:
        ln = 0
        for line in file:
            if ln == 0:
                line = line.split()
                extracted_lines.append(line[0]+','+line[1]+','+line[2]+'\n')
                ln+=1
            else:
                extracted_lines.append(line)
    #write
    with open(csvfile, 'w') as file:
        for line in extracted_lines:
            file.write(line)
    return None

def read_and_format_data(datadir, countries):
        '''Read in and format all data needed for the model
        '''

        #Get epidemic data
        epidemic_data = pd.read_csv(datadir+'ecdc_20200411.csv')
        #Convert to datetime
        epidemic_data['dateRep'] = pd.to_datetime(epidemic_data['dateRep'], format='%d/%m/%Y')
        ## get CFR
        cfr_by_country = pd.read_csv(datadir+"weighted_fatality.csv")
        #SI
        serial_interval = pd.read_csv(datadir+"serial_interval.csv")

        #Create stan data
        N2=81 #Increase for further forecast
        dates_by_country = {} #Save for later plotting purposes
        deaths_by_country = {}
        cases_by_country = {}
        stan_data = {'M':len(countries), #number of countries
                    'N0':6, #number of days for which to impute infections
                    'N':[], #days of observed data for country m. each entry must be <= N2
                    'N2':N2,
                    'x':np.arange(1,N2+1),
                    'cases':np.zeros((N2,len(countries)), dtype=int),
                    'deaths':np.zeros((N2,len(countries)), dtype=int),
                    'f':np.zeros((N2,len(countries))),
                    # 'retail':np.zeros((N2,len(countries))),
                    # 'grocery':np.zeros((N2,len(countries))),
                    # 'transit':np.zeros((N2,len(countries))),
                    # 'work':np.zeros((N2,len(countries))),
                    'residential':np.zeros((N2,len(countries))),
                    'EpidemicStart': [],
                    'SI':serial_interval.loc[0:N2-1]['fit'].values,
                    'y':[] #index cases
                    }

        #Infection to death distribution
        itd = infection_to_death()
        #Covariate names
        #covariate_names = ['retail_and_recreation','grocery_and_pharmacy','transit_stations','workplace','residential']
        #covariate_names = ['retail','grocery','transit','work','residential']
        covariate_names = ['residential']
        #Get data by country
        for c in range(len(countries)):
                country = countries[c]
                #Get fatality rate
                cfr = cfr_by_country[cfr_by_country['Region, subregion, country or area *']==country]['weighted_fatality'].values[0]

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
                #Add epidemic start to stan data
                stan_data['EpidemicStart'].append(death_index+1-di30) #30 days before 10 deaths
                #Get part of country_epidemic_data 30 days before day with at least 10 deaths
                country_epidemic_data = country_epidemic_data.loc[di30:]
                #Reset index
                country_epidemic_data = country_epidemic_data.reset_index()

                print(country, len(country_epidemic_data))
                #Save dates
                dates_by_country[country] = country_epidemic_data['dateRep']
                #Save deaths
                deaths_by_country[country] = country_epidemic_data['deaths']
                #Save cases
                cases_by_country[country] = country_epidemic_data['cases']

                #Hazard estimation
                N = len(country_epidemic_data)
                stan_data['N'].append(N)
                forecast = N2 - N
                if forecast <0: #If the number of predicted days are less than the number available
                    N2 = N
                    forecast = 0
                    print('Forecast error!')
                    pdb.set_trace()


                #Get hazard rates for all days in country data
                h = np.zeros(N2) #N2 = N+forecast
                f = np.cumsum(itd.pdf(np.arange(1,len(h)+1,0.5))) #Cumulative probability to die for each day
                for i in range(1,len(h)):
                    #for each day t, the death prob is the area btw [t-0.5, t+0.5]
                    #divided by the survival fraction (1-the previous death fraction), (fatality ratio*death prob at t-0.5)
                    #This will be the percent increase compared to the previous end interval
                    h[i] = (cfr*(f[i*2+1]-f[i*2-1]))/(1-cfr*f[i*2-1])

                #The number of deaths today is the sum of the past infections weighted by their probability of death,
                #where the probability of death depends on the number of days since infection.
                s = np.zeros(N2)
                s[0] = 1
                for i in range(1,len(s)):
                    #h is the percent increase in death
                    #s is thus the relative survival fraction
                    #The cumulative survival fraction will be the previous
                    #times the survival probability
                    #These will be used to track how large a fraction is left after each day
                    #In the end all of this will amount to the adjusted death fraction
                    s[i] = s[i-1]*(1-h[i-1]) #Survival fraction

                #Multiplying s and h yields fraction dead of fraction survived
                f = s*h #This will be fed to the Stan Model
                stan_data['f'][:,c]=f

                #Number of cases
                cases = np.zeros(N2)
                cases -=1 #Assign -1 for all forcast days
                cases[:N]=np.array(country_epidemic_data['cases'])
                stan_data['cases'][:,c]=cases
                stan_data['y'].append(int(cases[0])) # just the index case!#only the index case
                #Number of deaths
                deaths = np.zeros(N2)
                deaths -=1 #Assign -1 for all forcast days
                deaths[:N]=np.array(country_epidemic_data['deaths'])
                stan_data['deaths'][:,c]=deaths

                #Covariates - assign the same shape as others (N2)
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
                    cov_i = np.zeros(N2)
                    cov_i[:N] = np.array(country_epidemic_data[name])
                    #Add covariate info to forecast
                    cov_i[N:N2]=cov_i[N-1]
                    stan_data[name][:,c] = cov_i

        #Rename covariates to match stan model
        for i in range(len(covariate_names)):
            stan_data['covariate'+str(i+1)] = stan_data.pop(covariate_names[i])

        return stan_data, covariate_names, dates_by_country, deaths_by_country, cases_by_country, N2



def simulate(stan_data, outdir):
        '''Simulate using stan: Efficient MCMC exploration according to Bayesian posterior distribution
        for parameter estimation.
        '''

        sm =  pystan.StanModel(file='mobility_residential.stan')
        #fit = sm.sampling(data=stan_data, iter=10, warmup=5,chains=2) #n_jobs = number of parallel processes - number of chains
        fit = sm.sampling(data=stan_data,iter=4000,warmup=2000,chains=8,thin=4, control={'adapt_delta': 0.95, 'max_treedepth': 10})
        #Save summary
        #print ("FIT:",fit)
        s = fit.summary()
        summary = pd.DataFrame(s['summary'], columns=s['summary_colnames'], index=s['summary_rownames'])
        print ("Saving: ",outdir+'summary.csv')
        summary.to_csv(outdir+'summary.csv')

        #Save fit - each parameter as np array
        out = fit.extract()
        for key in [*out.keys()]:
            fit_param = out[key]
            #print("Output:",outdir+key+'.npy')
            np.save(outdir+key+'.npy', fit_param)
        return out

def visualize_results(outdir, countries, covariate_names, dates_by_country, deaths_by_country, cases_by_country, N2,interventions,in_names):
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
    days = np.arange(0,N2)
    #Plot rhat
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.hist(summary['Rhat'])
    ax.set_ylabel('Count')
    ax.set_xlabel("Rhat")
    fig.savefig(outdir+'plots/rhat.png', format='png')
    plt.close()

    #Plot values from each iteration as r function mcmc_parcoord
    mcmc_parcoord(np.concatenate([alphas,np.expand_dims(phi,axis=1)], axis=1), covariate_names+['phi'], outdir)

    #Plot alpha (Rt = R0*-exp(sum{mob_change*alpha1-6}))
    fig, ax = plt.subplots(figsize=(4, 4))
    for i in range(1,len(covariate_names)+1):
        alpha = summary[summary['Unnamed: 0']=='alpha['+str(i)+']']
        alpha_m = 1-np.exp(-alpha['mean'].values[0])
        alpha_2_5 = 1-np.exp(-alpha['2.5%'].values[0])
        alpha_97_5 = 1-np.exp(-alpha['97.5%'].values[0])
        ax.scatter(i,alpha_m)
        ax.plot([i]*2,[alpha_2_5,alpha_97_5])
    ax.set_ylim([0,1])
    ax.set_ylabel('Fractional reduction in R0')
    covariate_names.insert(0,'')
    ax.set_xticklabels(covariate_names,rotation='vertical')
    plt.tight_layout()
    fig.savefig(outdir+'plots/alphas.png', format='png')
    plt.close()


    #plot per country
    for i in range(0,len(countries)):
        country= countries[i]
        dates = dates_by_country[country]
        end = len(dates)#End of data
        dates = np.array(dates,  dtype='datetime64[D]')
        means = {'prediction':[],'E_deaths':[], 'Rt':[]}
        lower_bound = {'prediction':[],'E_deaths':[], 'Rt':[]} #Estimated 2.5 %
        higher_bound = {'prediction':[],'E_deaths':[], 'Rt':[]} #Estimated 97.5 % - together 95 % CI
        lower_bound25 = {'prediction':[],'E_deaths':[], 'Rt':[]} #Estimated 25%
        higher_bound75 = {'prediction':[],'E_deaths':[], 'Rt':[]} #Estimated 55 % - together 75 % CI
        #Get means and 95 % CI for cases (prediction), deaths and Rt for all time steps
        for j in range(0,N2):
            for var in ['prediction', 'E_deaths', 'Rt']:
                var_ij = summary[summary['Unnamed: 0']==var+'['+str(j+1)+','+str(i+1)+']']
                means[var].append(var_ij['mean'].values[0])
                lower_bound[var].append(var_ij['2.5%'].values[0])
                higher_bound[var].append(var_ij['97.5%'].values[0])
                lower_bound25[var].append(var_ij['25%'].values[0])
                higher_bound75[var].append(var_ij['75%'].values[0])

        # Add ineter data.. and scale it
        IV={}
        for key in in_names.keys():
            IV[in_names[key]]=[]
            for j in range(0,len(interventions[key])):
                IV[in_names[key]]+=[interventions[key][j][i]]
        #Plot cases
        observed_country_cases = cases_by_country[country]
        
        plot_shade_ci(days, end, dates[0], means['prediction'], observed_country_cases,lower_bound['prediction'], higher_bound['prediction'], lower_bound25['prediction'], higher_bound75['prediction'],IV, 'Cases per day',outdir+'plots/'+country+'_cases.png')

        #Plot Deaths
        observed_country_deaths = deaths_by_country[country]
        plot_shade_ci(days, end,dates[0],means['E_deaths'],observed_country_deaths, lower_bound['E_deaths'], higher_bound['E_deaths'], lower_bound25['E_deaths'], higher_bound75['E_deaths'],IV, 'Deaths per day',outdir+'plots/'+country+'_deaths.png')

        #Plot R
        plot_shade_ci(days,end,dates[0],means['Rt'],'', lower_bound['Rt'], higher_bound['Rt'], lower_bound25['Rt'], higher_bound75['Rt'],IV,'Rt',outdir+'plots/'+country+'_Rt.png')

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

def plot_shade_ci(x,end,start_date,y, observed_y, lower_bound, higher_bound,lower_bound25, higher_bound75,interventions,ylabel,outname):
    '''Plot with shaded 95 % CI (plots both 1 and 2 std, where 2 = 95 % interval)
    '''
    dates = np.arange(start_date,np.datetime64('2020-04-16')) #Get dates
    forecast = len(dates)
    fig, ax = plt.subplots(figsize=(4, 4))
    #Plot observed dates
    if len(observed_y)>1:
        ax.bar(x[:end],observed_y)
    ax.plot(x[:end],y[:end], alpha=0.5, color='b', label='so far', linewidth = 1.0)
    ax.fill_between(x[:end], lower_bound[:end], higher_bound[:end], color='cornflowerblue', alpha=0.4)
    ax.fill_between(x[:end], lower_bound25[:end], higher_bound75[:end], color='cornflowerblue', alpha=0.6)

    # Plot interventions
    ax2 = ax.twinx()  # instantiate a second axes that shares the same x-axis
    color = 'tab:red'
    ax2.set_ylabel('Intervention', color=color)  # we already handled the x-label with ax1
    for key in interventions.keys():
        ax2.plot(x[:end],interventions[key][:end], alpha=0.5,  label=key, linewidth = 1.0,linestyle="dotted") #,color='r',

    ax2.tick_params(axis='y', labelcolor=color)
    ax2.set_ylim([-1,1])
    ax2.legend(loc='upper left',fontsize=6)
    fig.tight_layout()  # otherwise the right y-label is slightly clipped
    title=re.sub(r'\..*','',re.sub(r'.*/','',outname))
    ax.set(title=title)
    #Plot predicted dates
    ax.plot(x[end:forecast],y[end:forecast], alpha=0.5, color='g', label='forecast', linewidth = 1.0)
    ax.fill_between(x[end-1:forecast], lower_bound[end-1:forecast] ,higher_bound[end-1:forecast], color='forestgreen', alpha=0.4)
    ax.fill_between(x[end-1:forecast], lower_bound25[end-1:forecast], higher_bound75[end-1:forecast], color='forestgreen', alpha=0.6)
    #Plot formatting
    ax.legend(loc='lower left',fontsize=6)
    ax.set_ylabel(ylabel)
    ax.set_ylim([0,max(higher_bound[:forecast])])
    xticks=np.arange(0,forecast+1,7)
    ax.set_xticks(xticks)
    ax.set_xticklabels(dates[xticks],rotation='vertical')
    plt.tight_layout()
    fig.savefig(outname, format = 'png')
    plt.close()

#####MAIN#####
args = parser.parse_args()
datadir = args.datadir[0]+"/"
outdir = args.outdir[0]+"/"
if not os.path.exists(outdir+"plots/"):
    print('Creating folder: '+outdir)
    os.system('mkdir -p ' + outdir+"/plots")

#Read data
countries = ["Denmark", "Italy", "Germany", "Spain", "United_Kingdom", "France", "Norway", "Belgium", "Austria", "Sweden", "Switzerland","Greece","Portugal","Netherlands"]
stan_data, covariate_names, dates_by_country, deaths_by_country, cases_by_country, N2 = read_and_format_data(datadir, countries)

#Simulate
#print ("TEST",outdir,stan_data)
# out = simulate(stan_data, outdir)
#Visualize

#in_names={'covariate1':'retail','covariate2':'grocery','covariate3':'transit','covariate4':'work','covariate5':'residential'}
in_names={'covariate1':'residential'}
visualize_results(outdir, countries, covariate_names, dates_by_country, deaths_by_country, cases_by_country, N2,stan_data,in_names)
