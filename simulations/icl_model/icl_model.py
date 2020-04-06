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

        #Infection to onset
        ito_shape, ito_scale = conv_gamma_params(5.1, 0.86)
        ito = gamma(a=ito_shape, scale = ito_scale) #a=shape
        #Onset to death
        otd_shape, otd_scale = conv_gamma_params(18.8, 0.45)
        otd = gamma(a=otd_shape, scale = otd_scale) #a=shape
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
        to have the same date as the lockdown.
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


def read_and_format_data(datadir):
        '''Read in and format all data needed for the model
        '''

        countries = ["Denmark", "Italy", "Germany", "Spain", "United_Kingdom",
                        "France", "Norway", "Belgium", "Austria", "Sweden", "Switzerland"]

        #Get epidemic data
        epidemic_data = pd.read_csv(datadir+'epidemic_data.csv')
        #Convert to datetime
        epidemic_data['DateRep'] = pd.to_datetime(epidemic_data['DateRep'])
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
        stan_data = {'M':len(countries),'N':[],'p':len(covariates.columns)-1,
                                'x':np.arange(1,N2+1),
                 'y':[],'covariate1':[],'covariate2':[],'covariate3':[],
                                 'covariate4':[],'covariate5':[],'covariate6':[],
                                 'deaths':[],'f':[],
                 'N0':6,'cases':[],'LENGTHSCALE':7,
                                 'SI':serial_interval[1:N2],
                 'EpidemicStart': []} # N0 = 6 to make it consistent with Rayleigh


        #Get data by country
        for country in countries:
                #Get fatality rate
                cfr = cfr_by_country[cfr_by_country['Region, subregion, country or area *']==country]['weighted_fatality'].values[0]
                #Get country epidemic data
                country_epidemic_data = epidemic_data[epidemic_data['Countries.and.territories']==country]
                dates = country_epidemic_data['DateRep']
                decimal_dates = country_epidemic_data['t']
                index = np.array(country_epidemic_data[country_epidemic_data['Cases']>0].index)
                #Get all dates with at least 10 deaths
                cum_deaths = country_epidemic_data['Deaths'].cumsum()
                death_index = np.array(cum_deaths[cum_deaths>=10])
                di30 = death_index-30
                #Add epidemic start to stan data
                stan_data['EpidemicStart'].append(death_index+1-di30)

                #Add 1 for when each NPI (covariate) has been active
                country_cov = covariates[covariates['Country']==country]
                for covariate in ['schools_universities', 'public_events', 'lockdown',
                'social_distancing_encouraged', 'self_isolating_if_ill', 'any_intervention']:
                        cov_start = pd.to_datetime(country_cov[covariate].values[0]) #Get start of NPI
                        country_epidemic_data.loc[country_epidemic_data.index,covariate] = 0
                        country_epidemic_data.loc[country_epidemic_data['DateRep']>=cov_start, covariate]=1
                pdb.set_trace()



def simulate(outdir):
        '''Simulate using stan: Efficient MCMC exploration according to Bayesian posterior distribution
        for parameter estimation.
        '''

        serial = serial_interval_distribution() #Distribution
        itd = infection_to_death()




#####MAIN#####
args = parser.parse_args()
datadir = args.datadir[0]
outdir = args.outdir[0]
#Read data
read_and_format_data(datadir)
#Simulate
simulate(outdir)
