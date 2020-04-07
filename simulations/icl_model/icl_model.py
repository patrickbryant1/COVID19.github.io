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


#matplotlib.rcParams.update({'font.size': 20})

#Arguments for argparse module:
parser = argparse.ArgumentParser(description = '''Simulate according to the ICL response team''')

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
        #In R
        #x1 = rgammaAlt(5e6,mean1,cv1) # infection-to-onset ----> do all people who are infected get to onset?
        #x2 = rgammaAlt(5e6,mean2,cv2) # onset-to-death
        #From https://cran.r-project.org/web/packages/EnvStats/EnvStats.pdf
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

def fix_covariates(covariates):
        '''Change dates so all covariates that happen after the lockdown
        to have the same date as the lockdown. Also add the covariate "any intervention"
        '''
        NPI = ['schools_universities',  'public_events',
        'social_distancing_encouraged', 'self_isolating_if_ill']
        #Add covariate for first intervention
        covariates['any_intervention'] = ''

        for i in range(len(covariates)):
                row = covariates.iloc[i]
                lockdown = row['lockdown']
                first_inter = '2021-04-01'
                for n in NPI:
                        if row[n] < first_inter:
                                first_inter = row[n]
                        if row[n] > lockdown:
                                covariates.at[i,n] = lockdown

                covariates.at[i,'any_intervention'] = first_inter
        return covariates

def ortho_poly_fit(x, degree = 1):
    n = degree + 1
    x = np.asarray(x).flatten()
    if(degree >= len(np.unique(x))):
            stop("'degree' must be less than number of unique points")
    xbar = np.mean(x)
    x = x - xbar
    X = np.fliplr(np.vander(x, n))
    q,r = np.linalg.qr(X)

    z = np.diag(np.diag(r))
    raw = np.dot(q, z)

    norm2 = np.sum(raw**2, axis=0)
    alpha = (np.sum((raw**2)*np.reshape(x,(-1,1)), axis=0)/norm2 + xbar)[:degree]
    Z = raw / np.sqrt(norm2)
    return Z, norm2, alpha

def read_and_format_data(datadir):
        '''Read in and format all data needed for the model
        '''

        countries = ["Denmark", "Italy", "Germany", "Spain", "France", "Norway", "Belgium", "Austria", "Sweden", "Switzerland"]

        #Get epidemic data
        epidemic_data = pd.read_csv(datadir+'epidemic_data.csv')
        #Convert to datetime
        epidemic_data['DateRep'] = pd.to_datetime(epidemic_data['DateRep'], format='%d/%m/%Y')
        ## get CFR
        cfr_by_country = pd.read_csv(datadir+"weighted_fatality.csv")
        #SI
        serial_interval = pd.read_csv(datadir+"serial_interval.csv")
        #NPI and their implementation dates
        covariates = pd.read_csv(datadir+'interventions_only.csv')
        #Change dates
        covariates = fix_covariates(covariates)

        #Create stan data
        N2=75 #Increase for further forecast
        x = ortho_poly_fit(np.arange(1,N2+1),2) #orthogonal fit of number of days
        stan_data = {'M':len(countries), #number of countries
                    'N0':6, #number of days for which to impute infections
                    'N':[], #days of observed data for country m. each entry must be <= N2
                    'N2':N2,
                    'x':np.arange(1,N2+1),
                    #'x1':x[0][:,1],#index of days
                    #'x2':x[0][:,2],#index of days
                    'cases':np.zeros((N2,len(countries)), dtype=int),
                    'deaths':np.zeros((N2,len(countries)), dtype=int),
                    'f':np.zeros((N2,len(countries))),
                    'schools_universities':np.zeros((N2,len(countries)), dtype=int),
                    'self_isolating_if_ill':np.zeros((N2,len(countries)), dtype=int),
                    'public_events':np.zeros((N2,len(countries)), dtype=int),
                    'any_intervention':np.zeros((N2,len(countries)), dtype=int),
                    'lockdown':np.zeros((N2,len(countries)), dtype=int),
                    'social_distancing_encouraged':np.zeros((N2,len(countries)), dtype=int),
                    'EpidemicStart': [],
                    'SI':serial_interval.loc[0:N2-1]['fit'].values,
                    #'p':7, #stan setting?
                    'y':[] #index cases
                    }

        #Infection to death distribution
        itd = infection_to_death()
        #Covariate names
        covariate_names = ['schools_universities', 'self_isolating_if_ill','public_events', 'any_intervention', 'lockdown', 'social_distancing_encouraged']
        #Get data by country
        for c in range(len(countries)):
                country = countries[c]
                #Get fatality rate
                cfr = cfr_by_country[cfr_by_country['Region, subregion, country or area *']==country]['weighted_fatality'].values[0]

                #Get country epidemic data
                country_epidemic_data = epidemic_data[epidemic_data['Countries.and.territories']==country]
                dates = country_epidemic_data['DateRep']
                decimal_dates = country_epidemic_data['t']
                index = np.array(country_epidemic_data[country_epidemic_data['Cases']>0].index)
                #Get all dates with at least 10 deaths
                cum_deaths = country_epidemic_data['Deaths'].cumsum()
                death_index = cum_deaths[cum_deaths>=10].index[0]
                di30 = death_index-30
                #Add epidemic start to stan data
                stan_data['EpidemicStart'].append(death_index+1-di30) #30 days before 10 deaths
                #Get part of country_epidemic_data 30 days before day with at least 10 deaths
                country_epidemic_data = country_epidemic_data.loc[di30:]
                #Add 1 for when each NPI (covariate) has been active
                country_cov = covariates[covariates['Country']==country]
                for covariate in covariate_names:
                        cov_start = pd.to_datetime(country_cov[covariate].values[0]) #Get start of NPI
                        country_epidemic_data.loc[country_epidemic_data.index,covariate] = 0
                        country_epidemic_data.loc[country_epidemic_data['DateRep']>=cov_start, covariate]=1


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
                cases[:N]=np.array(country_epidemic_data['Cases'])
                stan_data['cases'][:,c]=cases
                stan_data['y'].append(int(cases[0])) # just the index case!#only the index case
                #Number of deaths
                deaths = np.zeros(N2)
                deaths -=1 #Assign -1 for all forcast days
                deaths[:N]=np.array(country_epidemic_data['Deaths'])
                stan_data['deaths'][:,c]=deaths

                #Covariates - assign the same shape as others (N2)
                for name in covariate_names:
                    cov_i = np.zeros(N2)
                    cov_i[:N] = np.array(country_epidemic_data[name])
                    #Add covariate info to forecast
                    cov_i[N:N2]=cov_i[N-1]
                    stan_data[name][:,c] = cov_i

        #Rename covariates to match stan model
        for i in range(len(covariate_names)):
            stan_data['covariate'+str(i+1)] = stan_data.pop(covariate_names[i])

        return stan_data



def simulate(stan_data):
        '''Simulate using stan: Efficient MCMC exploration according to Bayesian posterior distribution
        for parameter estimation.
        '''

        sm =  pystan.StanModel(file='base.stan')
        #fit = sm.sampling(data=stan_data, iter=40, warmup=20,chains=2) #n_jobs = number of parallel processes - number of chains
        fit = sm.sampling(m,data=stan_data,iter=200,warmup=100,chains=4,thin=4,control = list(adapt_delta = 0.90, max_treedepth = 10))
        pdb.set_trace()


#####MAIN#####
args = parser.parse_args()
datadir = args.datadir[0]
outdir = args.outdir[0]
#Read data
stan_data = read_and_format_data(datadir)

#Simulate
simulate(stan_data)
