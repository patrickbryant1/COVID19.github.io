
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


def format_SE(datadir,end_date):
        #Get epidemic data
        epidemic_data = pd.read_csv(datadir+'FHM-2020-05-01.csv')
        epidemic_data['date'] = pd.to_datetime(epidemic_data['date'], format='%Y-%m-%d')
        #epidemic_data=epidemic_data.rename(columns={"country":"countriesAndTerritories"})                 
        epidemic_data=epidemic_data.rename(columns={"new_confirmed_cases":"cases"})                 
        epidemic_data=epidemic_data.rename(columns={"new_deaths":"deaths"})                 
        #Select all data up to end_date
        epidemic_data = epidemic_data[epidemic_data['date']<=end_date]
        #Mobility data
        mobility_data = pd.read_csv(datadir+'SE_Mobility_Report.csv')
        # We need to map the regions
        translations={
                "Blekinge County":"Blekinge",
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
        mobility_data['date'] = pd.to_datetime(mobility_data['date'], format='%Y-%m-%d')
        cfr_by_country = pd.read_csv(datadir+"weighted_fatality_SE.csv")
        cfr_by_country.replace(translations, inplace=True)
        return epidemic_data,mobility_data,cfr_by_country

def format_US(datadir,end_date):
        #Get epidemic data
        epidemic_data = pd.read_csv(datadir+'JHS-provinces-2020-05-05.csv')
        epidemic_data['date'] = pd.to_datetime(epidemic_data['date'], format='%Y-%m-%d')
        #epidemic_data=epidemic_data.rename(columns={"country":"countriesAndTerritories"})                 
        epidemic_data=epidemic_data.rename(columns={"new_confirmed_cases":"cases"})                 
        epidemic_data=epidemic_data.rename(columns={"new_deaths":"deaths"})                 
        #Select all data up to end_date
        epidemic_data = epidemic_data[epidemic_data['date']<=end_date]
        #Mobility data
        mobility_data = pd.read_csv(datadir+'US_Mobility_Report.csv')
        # We need to map the regions
        translations={
'America-Alabama':'Alabama',
'America-Alaska':'Alaska',
'America-American_Samoa':'American_Samoa',
'America-Arizona':'Arizona',
'America-Arkansas':'Arkansas',
'America-California':'California',
'America-Chicago':'Chicago',
'America-Colorado':'Colorado',
'America-Connecticut':'Connecticut',
'America-Delaware':'Delaware',
'America-District_of_Columbia':'District_of_Columbia',
'America-Florida':'Florida',
'America-Georgia':'Georgia',
'America-Guam':'Guam',
'America-Hawaii':'Hawaii',
'America-Idaho':'Idaho',
'America-Illinois':'Illinois',
'America-Indiana':'Indiana',
'America-Iowa':'Iowa',
'America-Kansas':'Kansas',
'America-Kentucky':'Kentucky',
'America-Louisiana':'Louisiana',
'America-Maine':'Maine',
'America-Maryland':'Maryland',
'America-Massachusetts':'Massachusetts',
'America-Michigan':'Michigan',
'America-Minnesota':'Minnesota',
'America-Mississippi':'Mississippi',
'America-Missouri':'Missouri',
'America-Montana':'Montana',
'America-Nebraska':'Nebraska',
'America-Nevada':'Nevada',
'America-New_Hampshire':'New_Hampshire',
'America-New_Jersey':'New_Jersey',
'America-New_Mexico':'New_Mexico',
'America-New_York':'New_York',
'America-North_Carolina':'North_Carolina',
'America-North_Dakota':'North_Dakota',
'America-Northern_Mariana_Islands':'Northern_Mariana_Islands',
'America-Ohio':'Ohio',
'America-Oklahoma':'Oklahoma',
'America-Oregon':'Oregon',
'America-Pennsylvania':'Pennsylvania',
'America-Puerto_Rico':'Puerto_Rico',
'America-Recovered':'Recovered',
'America-Rhode_Island':'Rhode_Island',
'America-South_Carolina':'South_Carolina',
'America-South_Dakota':'South_Dakota',
'America-Tennessee':'Tennessee',
'America-Texas':'Texas',
'America-USA':'USA',
'America-Utah':'Utah',
'America-Vermont':'Vermont',
'America-Virginia':'Virginia',
'America-Virgin_Islands':'Virgin_Islands',
'America-Washington':'Washington',
'America-West_Virginia':'West_Virginia',
'America-Wisconsin':'Wisconsin',
'America-Wuhan_Evacuee':'Wuhan_Evacuee',
'America-Wyoming':'Wyoming',
'America-Washington,_D.C.':'Washington_D.C.',
'Alabama':'Alabama',
'Alaska':'Alaska',
'American Samoa':'American_Samoa',
'Arizona':'Arizona',
'Arkansas':'Arkansas',
'California':'California',
'Chicago':'Chicago',
'Colorado':'Colorado',
'Connecticut':'Connecticut',
'Delaware':'Delaware',
'District of Columbia':'District_of_Columbia',
'Florida':'Florida',
'Georgia':'Georgia',
'Guam':'Guam',
'Hawaii':'Hawaii',
'Idaho':'Idaho',
'Illinois':'Illinois',
'Indiana':'Indiana',
'Iowa':'Iowa',
'Kansas':'Kansas',
'Kentucky':'Kentucky',
'Louisiana':'Louisiana',
'Maine':'Maine',
'Maryland':'Maryland',
'Massachusetts':'Massachusetts',
'Michigan':'Michigan',
'Minnesota':'Minnesota',
'Mississippi':'Mississippi',
'Missouri':'Missouri',
'Montana':'Montana',
'Nebraska':'Nebraska',
'Nevada':'Nevada',
'New Hampshire':'New_Hampshire',
'New Jersey':'New_Jersey',
'New Mexico':'New_Mexico',
'New York':'New_York',
'North Carolina':'North_Carolina',
'North Dakota':'North_Dakota',
'Northern Mariana Islands':'Northern_Mariana_Islands',
'Ohio':'Ohio',
'Oklahoma':'Oklahoma',
'Oregon':'Oregon',
'Pennsylvania':'Pennsylvania',
'Puerto Rico':'Puerto_Rico',
'Recovered':'Recovered',
'Rhode Island':'Rhode_Island',
'South Carolina':'South_Carolina',
'South Dakota':'South_Dakota',
'Tennessee':'Tennessee',
'Texas':'Texas',
'USA':'USA',
'Utah':'Utah',
'Vermont':'Vermont',
'Virginia':'Virginia',
'Virgin Islands':'Virgin_Islands',
'Washington':'Washington',
'West Virginia':'West_Virginia',
'Wisconsin':'Wisconsin',
'Wuhan Evacuee':'Wuhan_Evacuee',
'Wyoming':'Wyoming',
'Washington, D.C.':'Washington,_D.C.'
                }

        mobility_data.replace(translations, inplace=True)
        mobility_data=mobility_data.rename(columns={"country":"Maincountry"})                 
        #mobility_data=mobility_data.rename(columns={"sub_region_1":"country"})                 

        
        epidemic_data.replace(translations, inplace=True)
        mobility_data['date'] = pd.to_datetime(mobility_data['date'], format='%Y-%m-%d')

        cfr_by_country = pd.read_csv(datadir+"weighted_fatality_US.csv")
        cfr_by_country.replace(translations, inplace=True)
        
        #print (mobility_data[mobility_data["sub_region_1"]=="Alabama"])
        #print (epidemic_data[epidemic_data["sub_region_1"]=="Alabama"])
        #print (mobility_data[mobility_data["sub_region_1"]=="New_York"])
        #print (epidemic_data[epidemic_data["sub_region_1"]=="New_York"])

        
        #sys.exit()
        return epidemic_data,mobility_data,cfr_by_country

def read_and_format_data(datadir, countries, N2, end_date,model):
        '''Read in and format all data needed for the model
        N2 = number of days to model
        '''
        if model== "SE":
                epidemic_data,mobility_data,cfr_by_country=format_SE(datadir,end_date)
        elif model == "US":
                epidemic_data,mobility_data,cfr_by_country=format_US(datadir,end_date)
        else:
                sys.exit()
                
        # get CFR
        #SI
        serial_interval = serial_interval_distribution(N2) #pd.read_csv(datadir+"serial_interval.csv")

        #Create stan data
        #N2=84 #Increase for further forecast
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
                    'retail_and_recreation_percent_change_from_baseline':np.zeros((N2,len(countries))),
                    'grocery_and_pharmacy_percent_change_from_baseline':np.zeros((N2,len(countries))),
                    'transit_stations_percent_change_from_baseline':np.zeros((N2,len(countries))),
                    'workplaces_percent_change_from_baseline':np.zeros((N2,len(countries))),
                    'residential_percent_change_from_baseline':np.zeros((N2,len(countries))),
                    'EpidemicStart': [],
                    'SI':serial_interval[0:N2],
                    'y':[] #index cases
                    }
        print (stan_data)
        #Infection to death distribution
        itd = infection_to_death()
        #Covariate names
        covariate_names = ['retail_and_recreation_percent_change_from_baseline',
       'grocery_and_pharmacy_percent_change_from_baseline',
       'transit_stations_percent_change_from_baseline',
       'workplaces_percent_change_from_baseline',
       'residential_percent_change_from_baseline']
        #Get data by country
        for c in range(len(countries)):
                country = countries[c]
                #Get fatality rate
                print(country)
                cfr = cfr_by_country[cfr_by_country['Region, subregion, country or area *']==country]['weighted_fatality'].values[0]

                #Get country epidemic data
                #epidemic_data=epidemic_data.rename(columns={"country":"countriesAndTerritories"})
                country_epidemic_data = epidemic_data[epidemic_data['country']==country]
                #Sort on date
                country_epidemic_data = country_epidemic_data.sort_values(by='date')
                #Reset index
                country_epidemic_data = country_epidemic_data.reset_index()

                #Get all dates with at least 10 deaths
                cum_deaths = country_epidemic_data['deaths'].cumsum()
                print (cum_deaths)
                death_index = cum_deaths[cum_deaths>=10].index[0]
                di30 = death_index-30
                #Add epidemic start to stan data
                stan_data['EpidemicStart'].append(death_index+1-di30) #30 days before 10 deaths
                #Get part of country_epidemic_data 30 days before day with at least 10 deaths
                country_epidemic_data = country_epidemic_data.loc[di30:]
                #Reset index
                country_epidemic_data = country_epidemic_data.reset_index()

                #Save dates
                dates_by_country[country] = country_epidemic_data['date']
                #Save deaths
                deaths_by_country[country] = country_epidemic_data['deaths']
                #Save cases
                cases_by_country[country] = country_epidemic_data['cases']

                #Hazard estimation
                N = len(country_epidemic_data)
                stan_data['N'].append(N)
                forecast = N2 - N

                #print ("TEST",country,N2,N)
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

                #print ("Country",country)
                #Covariates - assign the same shape as others (N2)
                #Mobility data from Google
                #country_cov_data = mobility_data[mobility_data['country_region']==country]
                country_cov_data = mobility_data[mobility_data['sub_region_1']==country]
                #Get whole country - no subregion
                #country_cov_data =  country_cov_data[country_cov_data['sub_region_1'].isna()]
                #Get matching dates
                
                #print("Dates:",country_cov_data['date'],country_epidemic_data['date'])
                country_cov_data = country_cov_data[country_cov_data['date'].isin(country_epidemic_data['date'])]
                #print ("Found",country_cov_data)
                end_date = max(country_cov_data['date']) #Last date for mobility data
                for name in covariate_names:
                    country_epidemic_data.loc[country_epidemic_data.index,name] = 0 #Set all to 0
                    for d in range(len(country_epidemic_data)): #loop through all country data
                        row_d = country_epidemic_data.loc[d]
                        date_d = row_d['date'] #Extract date
                        try:
                            change_d = np.round(float(country_cov_data[country_cov_data['date']==date_d][name].values[0])/100, 2) #Match mobility change on date
                            if not np.isnan(change_d):
                                country_epidemic_data.loc[d,name] = change_d #Add to right date in country data
                        except:
                            continue #Date too far ahead


                    #Add the latest available mobility data to all remaining days (including the forecast days)
                    country_epidemic_data.loc[country_epidemic_data['date']>=end_date, name]=change_d
                    cov_i = np.zeros(N2)
                    cov_i[:N] = np.array(country_epidemic_data[name])
                    #Add covariate info to forecast
                    cov_i[N:N2]=cov_i[N-1]
                    stan_data[name][:,c] = cov_i

        #Rename covariates to match stan model
        for i in range(len(covariate_names)):
            stan_data['covariate'+str(i+1)] = stan_data.pop(covariate_names[i])
        return stan_data

def serial_interval_distribution(N2):
        '''Models the the time between when a person gets infected and when
        they subsequently infect another other people
        '''
        serial_shape, serial_scale = conv_gamma_params(6.5,0.62)
        serial = gamma(a=serial_shape, scale = serial_scale) #a=shape

        return serial.pdf(np.arange(1,N2+1))

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

