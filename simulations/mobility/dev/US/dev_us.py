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
parser = argparse.ArgumentParser(description = '''Simulate using google mobility data and most of the ICL response team model''')

parser.add_argument('--us_deaths', nargs=1, type= str, default=sys.stdin, help = 'Path to death data.')
parser.add_argument('--mobility_data', nargs=1, type= str, default=sys.stdin, help = 'Path to mobility data.')
parser.add_argument('--stan_model', nargs=1, type= str, default=sys.stdin, help = 'Stan model.')
parser.add_argument('--days_to_simulate', nargs=1, type= int, default=sys.stdin, help = 'Number of days to simulate.')
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
        itd_shape, itd_scale = conv_gamma_params((5.1+17.8), (0.45))
        itd = gamma(a=itd_shape, scale = itd_scale) #a=shape
        return itd

def serial_interval_distribution(N2):
        '''Models the the time between when a person gets infected and when
        they subsequently infect another other people
        '''
        serial_shape, serial_scale = conv_gamma_params(4.7,2.9)
        serial = gamma(a=serial_shape, scale = serial_scale) #a=shape

        return serial.pdf(np.arange(1,N2+1))

def read_and_format_data(us_deaths, mobility_data, N2):
        '''Read in and format all data needed for the model
        N2 = number of days to model
        '''
        #Convert to datetime
        mobility_data['date']=pd.to_datetime(mobility_data['date'], format='%Y/%m/%d')
        #Select US
        mobility_data = mobility_data[mobility_data['country_region']=="United States"]
        #Look at the US states
        subregions = mobility_data['sub_region_1'].unique()[1:] #The first subregion is nan (no subregion)
        #SI
        serial_interval = serial_interval_distribution(N2) #pd.read_csv(datadir+"serial_interval.csv")

        #Create stan data
        stan_data = {'M':len(subregions), #number of countries
                    'N0':6, #number of days for which to impute infections
                    'N':[], #days of observed data for country m. each entry must be <= N2
                    'N2':N2, #number of days to model
                    'x':np.arange(1,N2+1),
                    'deaths':np.zeros((N2,len(subregions)), dtype=int),
                    'f':np.zeros((N2,len(subregions))),
                    'retail_and_recreation_percent_change_from_baseline':np.zeros((N2,len(subregions))),
                    'grocery_and_pharmacy_percent_change_from_baseline':np.zeros((N2,len(subregions))),
                    'transit_stations_percent_change_from_baseline':np.zeros((N2,len(subregions))),
                    'workplaces_percent_change_from_baseline':np.zeros((N2,len(subregions))),
                    'residential_percent_change_from_baseline':np.zeros((N2,len(subregions))),
                    'parks_percent_change_from_baseline':np.zeros((N2,len(subregions))),
                    'EpidemicStart': [],
                    'SI':serial_interval[0:N2]
                    }
        #Infection to death distribution
        itd = infection_to_death()

        #Covariate names
        covariate_names = ['retail_and_recreation_percent_change_from_baseline',
       'grocery_and_pharmacy_percent_change_from_baseline',
       'transit_stations_percent_change_from_baseline',
       'workplaces_percent_change_from_baseline',
       'residential_percent_change_from_baseline',
       'parks_percent_change_from_baseline']
        #Fatality rate - fixed
        cfr = 0.01

        #Get hazard rates for all days in country data
        #This can be done only once now that the cfr is constant
        h = np.zeros(N2) #N2 = N+forecast
        f = np.cumsum(itd.pdf(np.arange(1,len(h)+1,0.5))) #Cumulative probability to die for each day
        #Adjust f to reach max 1 - the half steps makes this different
        f = f/2
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

        #Save all extracted data
        complete_df = pd.DataFrame()
        #Get data by state
        for c in range(len(subregions)):
            #Assign fraction dead
            stan_data['f'][:,c]=f
            region =subregions[c]

            #Get region epidemic data
            regional_deaths = us_deaths[us_deaths['Province_State']== region]
            cols = regional_deaths.columns
            #Calculate back per day - now cumulative
            deaths_per_day = []
            dates = cols[12:]
            #First deaths
            deaths_per_day.append(np.sum(regional_deaths[dates[0]]))
            for d in range(1,len(dates)):#The first 12 columns are not deaths
                deaths_per_day.append(np.sum(regional_deaths[dates[d]])-np.sum(regional_deaths[dates[d-1]]))
            #Create dataframe
            regional_epidemic_data = pd.DataFrame()
            regional_epidemic_data['date']=dates

            #Convert to datetime
            regional_epidemic_data['date'] = pd.to_datetime(regional_epidemic_data['date'], format='%m/%d/%y')
            regional_epidemic_data['deaths']=deaths_per_day

            #Sort on date
            regional_epidemic_data = regional_epidemic_data.sort_values(by='date')
            #Regional mobility data
            region_mob_data = mobility_data[mobility_data['sub_region_1']==region]
            region_mob_data = region_mob_data[region_mob_data['sub_region_2'].isna()]
            #Merge epidemic data with mobility data
            regional_epidemic_data = regional_epidemic_data.merge(region_mob_data, left_on = 'date', right_on ='date', how = 'right')

            #Get all dates with at least 10 deaths
            cum_deaths = regional_epidemic_data['deaths'].cumsum()
            death_index = cum_deaths[cum_deaths>=10].index[0]
            di30 = death_index-30
            #Add epidemic start to stan data
            stan_data['EpidemicStart'].append(death_index+1-di30) #30 days before 10 deaths
            #Get part of country_epidemic_data 30 days before day with at least 10 deaths
            regional_epidemic_data = regional_epidemic_data.loc[di30:]
            #Reset index
            regional_epidemic_data = regional_epidemic_data.reset_index()
            #Print region and number of days
            print(region, len(regional_epidemic_data), min(regional_epidemic_data['date']),max(regional_epidemic_data['date']))

            #Get dates for plotting
            if region == 'New York':
                plot_dates = np.array(regional_epidemic_data['date'], dtype='datetime64[D]')
	        #Add number of days per country
            N = len(regional_epidemic_data)
            stan_data['N'].append(N)
            forecast = N2 - N
            if forecast <0: #If the number of predicted days are less than the number available
                N2 = N
                forecast = 0
                print('Forecast error!')
                pdb.set_trace()

            #Number of deaths
            deaths = np.array(regional_epidemic_data['deaths'])
            sm_deaths = np.zeros(N2)
            sm_deaths -=1 #Assign -1 for all forcast days
            #Smooth deaths
            #Do a 7day sliding window to get more even death predictions
            for i in range(7,len(regional_epidemic_data)+1):
                sm_deaths[i-1]=np.average(deaths[i-7:i])
            sm_deaths[0:6] = sm_deaths[6]
            stan_data['deaths'][:,c]=sm_deaths
            #Add to df
            regional_epidemic_data['deaths']=sm_deaths[:len(regional_epidemic_data)]
            #Covariates (mobility data from Google) - assign the same shape as others (N2)
            #Construct a 1-week sliding average to smooth the mobility data
            for name in covariate_names:
                mob_i = np.array(regional_epidemic_data[name])
                y = np.zeros(len(regional_epidemic_data))
                for i in range(7,len(mob_i)+1):
                    #Check that there are no NaNs
                    if np.isnan(mob_i[i-7:i]).any():
                        #If there are NaNs, loop through and replace with value from prev date
                        for i_nan in range(i-7,i):
                            if np.isnan(mob_i[i_nan]):
                                mob_i[i_nan]=mob_i[i_nan-1]
                    y[i-1]=np.average(mob_i[i-7:i])#Assign average
                y[0:6] = y[6]#Assign first week
                regional_epidemic_data[name]=y


            #Add covariate data
            for name in covariate_names:
                cov_i = np.zeros(N2)
                cov_i[:N] = np.array(regional_epidemic_data[name])
                #Add covariate info to forecast
                cov_i[N:N2]=cov_i[N-1]
                stan_data[name][:,c] = cov_i

            #Append data to final df
            regional_epidemic_data['region']=region
            complete_df = complete_df.append(regional_epidemic_data, ignore_index=True)
        #Rename covariates to match stan model
        for i in range(len(covariate_names)):
            stan_data['covariate'+str(i+1)] = stan_data.pop(covariate_names[i])

        return stan_data,complete_df


def simulate(stan_data, stan_model, outdir):
        '''Simulate using stan: Efficient MCMC exploration according to Bayesian posterior distribution
        for parameter estimation.
        '''

        sm =  pystan.StanModel(file=stan_model)
        fit = sm.sampling(data=stan_data,iter=4000,warmup=2000,chains=8,thin=4, control={'adapt_delta': 0.98, 'max_treedepth': 20})
        #Save summary
        s = fit.summary()
        summary = pd.DataFrame(s['summary'], columns=s['summary_colnames'], index=s['summary_rownames'])
        summary.to_csv(outdir+'summary.csv')

        #Save fit - each parameter as np array
        out = fit.extract()
        for key in [*out.keys()]:
            fit_param = out[key]
            np.save(outdir+key+'.npy', fit_param)
        return out

#####MAIN#####
args = parser.parse_args()
us_deaths = pd.read_csv(args.us_deaths[0])
mobility_data = pd.read_csv(args.mobility_data[0])
stan_model = args.stan_model[0]
days_to_simulate = args.days_to_simulate[0]
outdir = args.outdir[0]
#Read data
stan_data,complete_df = read_and_format_data(us_deaths, mobility_data, days_to_simulate)
#Save complete df
complete_df.to_csv('complete_df.csv')
#Simulate
out = simulate(stan_data, stan_model, outdir)
