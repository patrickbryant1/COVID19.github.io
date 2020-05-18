#! /usr/bin/env python3
# -*- encoding: utf-8 -*-


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

parser.add_argument('--datadir', nargs=1, type= str, default=sys.stdin, help = 'Path to outdir.')
parser.add_argument('--countries', nargs=1, type= str, default=sys.stdin, help = 'Countries to model (csv).')
parser.add_argument('--subregions', nargs=1, type= str, default=sys.stdin, help = 'Subregions to model (csv).')
parser.add_argument('--population_data', nargs=1, type= str, default=sys.stdin, help = 'Subregion population (csv).')
parser.add_argument('--epidemic_data', nargs=1, type= str, default=sys.stdin, help = 'Subregion epidemic data (csv).')
parser.add_argument('--stan_model', nargs=1, type= str, default=sys.stdin, help = 'Stan model.')
parser.add_argument('--days_to_simulate', nargs=1, type= int, default=sys.stdin, help = 'Number of days to simulate.')
parser.add_argument('--end_date', nargs=1, type= str, default=sys.stdin, help = 'Up to which date to include data.')
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

def serial_interval_distribution(N2):
        '''Models the the time between when a person gets infected and when
        they subsequently infect another other people
        '''
        serial_shape, serial_scale = conv_gamma_params(6.5,0.62)
        serial = gamma(a=serial_shape, scale = serial_scale) #a=shape

        return serial.pdf(np.arange(1,N2+1))

def se_transl(mobility_data, epidemic_data, population_data):
    '''Ensure the county names are the same across dfs
    '''
    translations={"Blekinge County":"Blekinge",
    "Dalarna County":"Dalarna",
    "Gavleborg County":"Gävleborg",
    "Gotland County":"Gotland",
    "Halland County":"Halland",
    "Jamtland County":"JämtlandHärjedalen",
    "Jämtland Härjedalen":"JämtlandHärjedalen",
    "Jonkoping County":"Jönköping",
    "Kalmar County":"Kalmar",
    "Kronoberg County":"Kronoberg",
    "Norrbotten County":"Norrbotten",
    "Örebro County":"Örebro",
    "Östergötland County":"Östergötland",
    "Skåne County":"Skåne",
    "Södermanland County":"Sörmland",
    "Stockholm County":"Stockholm",
    "Uppsala County":"Uppsala",
    "Varmland County":"Värmland",
    "Västerbotten County":"Västerbotten",
    "Västernorrland County":"Västernorrland",
    "Västmanland County":"Västmanland",
    "Västra Götaland County":"VästraGötaland",
    "Västra Götaland":"VästraGötaland"}

    mobility_data.replace(translations, inplace=True)
    epidemic_data.replace(translations, inplace=True)
    population_data.replace(translations, inplace=True)
    return mobility_data, epidemic_data, population_data

def read_and_format_data(datadir, countries, subregions, population_data, epidemic_data, N2, end_date):
        '''Read in and format all data needed for the model
        N2 = number of days to model
        '''

        #Get epidemic data
        epidemic_data['dateRep'] = pd.to_datetime(epidemic_data['date'], format='%Y/%m/%d')
        #Select all data up to end_date
        epidemic_data = epidemic_data[epidemic_data['dateRep']<=end_date]
        #Mobility data
        mobility_data = pd.read_csv(datadir+'Global_Mobility_Report.csv')
        #Convert to datetime
        mobility_data['date']=pd.to_datetime(mobility_data['date'], format='%Y/%m/%d')
        #Get per country
        mobility_data = mobility_data[mobility_data['country_region']==countries[0]]
        #Fix varying names
        mobility_data, epidemic_data, population_data = se_transl(mobility_data, epidemic_data, population_data)
        # get CFR
        cfr_by_country = pd.read_csv(datadir+"weighted_fatality.csv")
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
                    'EpidemicStart': [],
                    'SI':serial_interval[0:N2],
                    'y':[], #index cases
                    'population_size':[] #Size of population
                    }
        #Infection to death distribution
        itd = infection_to_death()

        #Diamond princess fatality rates per age group
        #dp_cfr = [0,0.002,0.002,0.002,0.004,0.013,0.036,0.08,0.148] #age groups: 0-9,10-19,20-29,30-39,40-49,50-59,60-69,70-79,80+

        #Covariate names
        covariate_names = ['retail_and_recreation_percent_change_from_baseline',
                           'grocery_and_pharmacy_percent_change_from_baseline',
                           'transit_stations_percent_change_from_baseline',
                           'workplaces_percent_change_from_baseline',
                           'residential_percent_change_from_baseline']

        country = countries[0]
        #Get fatality rate
        cfr = cfr_by_country[cfr_by_country['Region, subregion, country or area *']==country]['weighted_fatality'].values[0]


        #Get data by country
        for c in range(len(subregions)):
                subregion = subregions[c]
                subregion =' '.join(subregion.split('_'))
                #Get country epidemic data
                county_epidemic_data = epidemic_data[epidemic_data['country']==subregion.split('County')[0].strip()]
                #Sort on date
                county_epidemic_data = county_epidemic_data.sort_values(by='date')
                #Reset index
                county_epidemic_data = county_epidemic_data.reset_index()

                #Make check that at least 10 deaths have been observed
                #Get all dates with at least 10 deaths
                cum_deaths = county_epidemic_data['new_deaths'].cumsum()
                if max(cum_deaths)<10:
                    print(subregion, 'Cumulative deaths:',max(cum_deaths))
                    continue

                #Add population size
                try:
                    stan_data['population_size'].append(int(population_data[population_data['County']==subregion]['Population'].values[0]))
                except:
                    pdb.set_trace()
                death_index = cum_deaths[cum_deaths>=10].index[0]
                di30 = death_index-30
                #Add epidemic start to stan data
                stan_data['EpidemicStart'].append(death_index+1-di30) #30 days before 10 deaths
                #Get part of county_epidemic_data 30 days before day with at least 10 deaths
                county_epidemic_data = county_epidemic_data.loc[di30:]
                #Reset index
                county_epidemic_data = county_epidemic_data.reset_index()

                print(subregion, len(county_epidemic_data))

                #Hazard estimation
                N = len(county_epidemic_data)

		         #Add number of days per country
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
                #Number of deaths
                deaths = np.zeros(N2)
                deaths -=1 #Assign -1 for all forcast days
                deaths[:N]=np.array(county_epidemic_data['new_deaths'])
                #Do a 7day sliding window to get more even death predictions
                deaths_7 = np.zeros(N2)
                deaths_7 -=1
                deaths_7[0:7] = np.sum(deaths[0:7])/7
                for i in range(7,N):
                    deaths_7[i] = np.sum(deaths[i-6:i+1])/7


                stan_data['deaths'][:,c]=deaths_7

                #Covariates - assign the same shape as others (N2)
                #Mobility data from Google
                county_cov_data = mobility_data[mobility_data['sub_region_1']==subregion]
                #Get whole county - no county subregion
                county_cov_data =  county_cov_data[county_cov_data['sub_region_2'].isna()]
                #Get matching dates
                county_cov_data = county_cov_data[county_cov_data['date'].isin(county_epidemic_data['date'])]
                try:
                    end_date = max(county_cov_data['date']) #Last date for mobility data
                except:
                    pdb.set_trace()
                for name in covariate_names:
                    county_epidemic_data.loc[county_epidemic_data.index,name] = 0 #Set all to 0
                    for d in range(len(county_epidemic_data)): #loop through all country data
                        row_d = county_epidemic_data.loc[d]
                        date_d = row_d['dateRep'] #Extract date
                        try:
                            change_d = np.round(float(county_cov_data[county_cov_data['date']==date_d][name].values[0])/100, 2) #Match mobility change on date
                            if not np.isnan(change_d):
                                county_epidemic_data.loc[d,name] = change_d #Add to right date in country data
                        except:
                            continue #Date too far ahead


                    #Add the latest available mobility data to all remaining days (including the forecast days)
                    county_epidemic_data.loc[county_epidemic_data['dateRep']>=end_date, name]=change_d
                    cov_i = np.zeros(N2)
                    cov_7 = np.zeros(N2)
                    cov_i[:N] = np.array(county_epidemic_data[name])
                    #Do a 7-day sliding window for smoothing
                    cov_7[0:7]=np.sum(cov_i[0:7])/7
                    for m in range(7,N):
                        cov_7[m]=np.sum(cov_i[m-6:m+1])/7

                    #Add covariate info to forecast
                    cov_7[N:N2]=cov_7[N-1]
                    stan_data[name][:,c] = cov_7

        #Rename covariates to match stan model
        for i in range(len(covariate_names)):
            stan_data['covariate'+str(i+1)] = stan_data.pop(covariate_names[i])

        return stan_data



def simulate(stan_data, stan_model, outdir):
        '''Simulate using stan: Efficient MCMC exploration according to Bayesian posterior distribution
        for parameter estimation.
        '''

        sm =  pystan.StanModel(file=stan_model)
        fit = sm.sampling(data=stan_data,iter=4000,warmup=2000,chains=8,thin=4, control={'adapt_delta': 0.92, 'max_treedepth': 20})
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
datadir = args.datadir[0]
countries = args.countries[0].split(',')
#subregions = args.subregions[0].split(',')
subregions=['Dalarna','Gävleborg','Halland','JämtlandHärjedalen','Jönköping','Kalmar','Kronoberg','Norrbotten','Skåne','Stockholm','Sörmland','Uppsala','Värmland','Västerbotten','Västernorrland','Västmanland','VästraGötaland','Örebro','Östergötland']
population_data = pd.read_csv(args.population_data[0])
epidemic_data = pd.read_csv(args.epidemic_data[0])
stan_model = args.stan_model[0]
days_to_simulate = args.days_to_simulate[0]
end_date = np.datetime64(args.end_date[0])
outdir = args.outdir[0]

#Read data
stan_data = read_and_format_data(datadir, countries, subregions, population_data, epidemic_data, days_to_simulate, end_date)
pdb.set_trace()
#Simulate
out = simulate(stan_data, stan_model, outdir)
