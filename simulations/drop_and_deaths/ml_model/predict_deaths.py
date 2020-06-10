#! /usr/bin/env python3
# -*- coding: utf-8 -*-


import argparse
import sys
import os
import glob
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
import seaborn as sns
from scipy.stats import pearsonr
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import KFold
import pdb



#Arguments for argparse module:
parser = argparse.ArgumentParser(description = '''Predic the number of deaths ahead of time using a RF regressor.
                                                A nonlinear model is necessary due to the irregularity of the
                                                mobility effect. Historical data is used to take the previous
                                                epidemic development into account, which is not possible with
                                                e.g. MCMC simulations. ''')
parser.add_argument('--epidemic_data', nargs=1, type= str, default=sys.stdin, help = 'Path to eidemic data (csv).')
parser.add_argument('--mobility_data', nargs=1, type= str, default=sys.stdin, help = 'Google mobility data (csv).')
parser.add_argument('--outdir', nargs=1, type= str, default=sys.stdin, help = 'Path to outdir.')

###FUNCTIONS###
def format_data(epidemic_data, mobility_data, outdir):
        '''Read in and format all data needed for the analysis
        '''

        #Convert epidemic data to datetime
        epidemic_data['dateRep'] = pd.to_datetime(epidemic_data['dateRep'], format='%d/%m/%Y')
        #Rename date to date
        epidemic_data = epidemic_data.rename(columns={'dateRep':'date'})
        #Convert mobility data to datetime
        mobility_data['date'] = pd.to_datetime(mobility_data['date'], format='%Y/%m/%d')
        #Mobility key conversions
        key_conversions = {'United_States_of_America':'United States'}

        mobility_keys = {'retail_and_recreation_percent_change_from_baseline':[],
                           'grocery_and_pharmacy_percent_change_from_baseline':[],
                           'transit_stations_percent_change_from_baseline':[],
                           'workplaces_percent_change_from_baseline':[],
                           'residential_percent_change_from_baseline':[]}

        #Save fetched countries, death per million historically and for the predictions and mobility data
        extracted_data = pd.DataFrame()
        #Get unique countries
        countries = epidemic_data['countriesAndTerritories'].unique()
        for country in countries:
            #Get country epidemic data
            country_epidemic_data = epidemic_data[epidemic_data['countriesAndTerritories']==country]
            #Sort on date
            country_epidemic_data = country_epidemic_data.sort_values(by='date')
            #Reset index
            country_epidemic_data = country_epidemic_data.reset_index()


            country_deaths = np.array(country_epidemic_data['deaths'])
            #Ensure no negative corrections are present. Set these to the values of the previous date
            for i in range(len(country_deaths)):
                if country_deaths[i]<0:
                    country_deaths[i] = country_deaths[i-1]


            country_cases = np.array(country_epidemic_data['cases'])
            #Ensure no negative corrections are present. Set these to the values of the previous date
            for i in range(len(country_cases)):
                if country_cases[i]<0:
                    country_cases[i] = country_cases[i-1]

            #Mobility data from Google
            if country in key_conversions.keys():
                mob_key = key_conversions[country]
            else:
                mob_key = ' '.join(country.split('_'))

            country_mobility_data = mobility_data[mobility_data['country_region']==mob_key]
            #Get whole country - no subregion
            country_mobility_data = country_mobility_data[country_mobility_data['sub_region_1'].isna()]
            if len(country_mobility_data)<2:
                print('No mobility data for', country)
                continue
            #reset index
            country_mobility_data = country_mobility_data.reset_index()
            #Get start and end dates
            mobility_start = country_mobility_data['date'][0]
            mobility_end = max(country_mobility_data['date'])

            #Smooth deaths
            sm_deaths = np.zeros(len(country_epidemic_data))
            for i in range(7,len(country_epidemic_data)+1):
                sm_deaths[i-1]=np.average(country_deaths[i-7:i])
            sm_deaths[0:6] = sm_deaths[6]
            country_epidemic_data['smoothed_deaths']=sm_deaths

            #Smooth cases
            sm_cases = np.zeros(len(country_epidemic_data))
            for i in range(7,len(country_epidemic_data)+1):
                sm_cases[i-1]=np.average(country_cases[i-7:i])
            sm_cases[0:6] = sm_cases[6]
            country_epidemic_data['smoothed_cases']=sm_cases

            #Get population in millions
            country_pop = country_epidemic_data['popData2018'].values[0]/1000000
            #Calculate deaths per million and add to df
            country_epidemic_data['death_per_million'] =sm_deaths/country_pop

            #Construct a 1-week sliding average to smooth the mobility data
            for mob_key in mobility_keys:
                data = np.array(country_mobility_data[mob_key])
                y = np.zeros(len(country_mobility_data))
                for i in range(7,len(data)+1):
                    #Check that there are no NaNs
                    if np.isnan(data[i-7:i]).any():
                        #If there are NaNs, loop through and replace with value from prev date
                        for i_nan in range(i-7,i):
                            if np.isnan(data[i_nan]):
                                data[i_nan]=data[i_nan-1]
                    y[i-1]=np.average(data[i-7:i])
                y[0:6] = y[6]
                country_mobility_data[mob_key]=y
            #Merge epidemic data with mobility data
            country_epidemic_data = country_epidemic_data.merge(country_mobility_data, left_on = 'date', right_on ='date', how = 'left')

            #Get all data after the mobility start
            country_epidemic_data = country_epidemic_data[country_epidemic_data['date']>=mobility_start]

            #Save data
            extracted_data = pd.concat([extracted_data, country_epidemic_data])
        extracted_data.to_csv('extracted_data.csv')
        print('Number of fetched countries:',len(extracted_data['countriesAndTerritories'].unique()))

        return extracted_data

def construct_features(extracted_data):
    '''Construct features for ml model
    '''

    countries = extracted_data['countriesAndTerritories'].unique()
    num_countries = len(countries)
    all_index = np.arange(num_countries)
    #dpm_history = [] #Deaths per million 4 weeks before
    fetched_mobility = ['retail_and_recreation_percent_change_from_baseline',
                       'grocery_and_pharmacy_percent_change_from_baseline',
                       'transit_stations_percent_change_from_baseline',
                       'workplaces_percent_change_from_baseline',
                       'residential_percent_change_from_baseline']
    X = [] #Input features
    y = [] #Labels

    csi = [0] #Country split index in data for train
    fetched_countries = [] #The fetched countries
    train_countries = []
    valid_countries = []
    include_period = 21 #How many days to include data
    predict_lag = 21 #How many days ahead to predict
    for c in all_index:
        country = countries[c]
        country_data = extracted_data[extracted_data['countriesAndTerritories']==country]
        #Reset index
        country_data = country_data.reset_index()
        country_points=0 #Number of data points for country
        if (len(country_data)-predict_lag-include_period)<1:
            print('Not enough data for', country)
            continue
        #Go through all days
        for i in range(len(country_data)-predict_lag-include_period+1):
            country_points+=1 #Increase points
            x = []
            cum_measures = [] #Cumulative data - to capture the full history
            #Include data for the include period
            #Deaths and cases
            x.extend(np.array(country_data.loc[i:i+include_period-1, 'death_per_million']))
            cum_measures.append(np.sum(country_data.loc[i:i+include_period-1, 'death_per_million']))
            x.extend(np.array(country_data.loc[i:i+include_period-1, 'death_per_million']))
            cum_measures.append(np.sum(country_data.loc[i:i+include_period-1, 'death_per_million']))
            for key in fetched_mobility:
                curr_mob = np.array(country_data.loc[i:i+include_period-1, key])
                if np.isnan(curr_mob).any():
                    continue

                x.extend(np.array(country_data.loc[i:i+include_period-1, key]))
                cum_measures.append(np.sum(country_data.loc[i:i+include_period-1, key]))

            if len(cum_measures)<7:
                print(country)
                continue
            else:
                x.extend(cum_measures)
            #Add the number of epidemic days
            x.append(i+include_period)
            #Include data for the predict lag
            dpm_change = np.array(country_data.loc[i+include_period:i+include_period+predict_lag-1, 'death_per_million'])
            #Append to  data
            X.append(np.array(x))
            y.append(dpm_change)


        #Save country points and fetched countries
        csi.append(country_points)
        fetched_countries.append(country)
    print(len(y), 'data points')
    return np.array(X), np.array(y), np.array(csi), np.array(fetched_countries)

def CV_split(X,y,csi,fetched_countries):
    '''Split data to non-overlapping country splits
    '''
    num_countries = len(fetched_countries)
    all_index = np.arange(num_countries)
    csi = np.cumsum(csi) #Where the country splits are in the data
    #Save data
    X_train = {1:[],2:[],3:[],4:[],5:[]}
    y_train = {1:[],2:[],3:[],4:[],5:[]}
    csi_train = {1:[0],2:[0],3:[0],4:[0],5:[0]}
    train_countries = {1:[],2:[],3:[],4:[],5:[]}
    X_valid = {1:[],2:[],3:[],4:[],5:[]}
    y_valid = {1:[],2:[],3:[],4:[],5:[]}
    csi_valid = {1:[0],2:[0],3:[0],4:[0],5:[0]}
    valid_countries = {1:[],2:[],3:[],4:[],5:[]}
    #Split
    kf = KFold(n_splits=5,random_state=42, shuffle=True)
    split = 1
    for train_index, valid_index in kf.split(all_index):
        #Fetch all train points
        for ti in train_index:
            c1=csi[ti]
            c2=csi[ti+1]
            X_train[split].extend(X[c1:c2,:])
            y_train[split].extend(y[c1:c2,:])
            #Country splits in data
            csi_train[split].append(len(y_train))
            #Country names
            train_countries[split].append(fetched_countries[ti])
        #Fetch all valid points
        for vi in valid_index:
            c1=csi[vi]
            c2=csi[vi+1]
            X_valid[split].extend(X[c1:c2,:])
            y_valid[split].extend(y[c1:c2,:])
            #Country splits in data
            csi_valid[split].append(len(y_valid))
            #Country names
            valid_countries[split].append(fetched_countries[vi])
        #Increase split
        split+=1

    return X_train, y_train, csi_train, train_countries, X_valid, y_valid, csi_valid, valid_countries

def train(X_train,y_train, X_valid, y_valid, csi_train, csi_valid,countries,outdir):
    '''Fit rf regressor
    '''

    regr = RandomForestRegressor(random_state=0,n_estimators=100)
    print('Fitting model')
    regr.fit(X_train,y_train)
    pred = regr.predict(X_valid)
    R,p = pearsonr(pred[:,-1],y_valid[:,-1]) #The last day is the furthest ahead prediction
    print('Validation R:', np.round(R,2))
    print('Error:', np.average(np.absolute(pred[:,-1]-y_valid[:,-1])))
    fig, ax = plt.subplots(figsize=(9/2.54, 9/2.54))
    ax.scatter(pred[:,-1],y_valid[:,-1],s=3)
    ax.set_xlabel('Predicted deaths 3 weeks later')
    ax.set_ylabel('True deaths 3 weeks later')
    fig.tight_layout()
    fig.savefig(outdir+'true_vs_pred.png',  format='png')
    plt.close()
    #Visualize predictions by plotting
    visualize_pred(X_valid,pred[:,-1],y_valid[:,-1], csi_valid,countries,outdir)

def visualize_pred(X_valid,pred,y_valid, csi_valid,countries,outdir):
    '''Plot the true and predicted epidemic curves
    '''
    ip=21 #include period
    pl=21 #predict lag
    csi_valid = np.cumsum(csi_valid)
    for i in range(len(csi_valid)-1):
        #Create figure
        fig, ax1 = plt.subplots(figsize=(9/2.54, 9/2.54))
        ax2 = ax1.twinx()
        #Death input
        country_death_inp = X_valid[csi_valid[i]:csi_valid[i+1],0]
        country_death_inp = np.concatenate([country_death_inp,X_valid[csi_valid[i+1]-1,1:ip]])
        #Case input
        country_case_inp = X_valid[csi_valid[i]:csi_valid[i+1],ip]
        country_case_inp = np.concatenate([country_case_inp,X_valid[csi_valid[i+1]-1,ip+1:ip*2]])
        #Retail
        retail_inp = X_valid[csi_valid[i]:csi_valid[i+1],ip*2]
        retail_inp = np.concatenate([retail_inp,X_valid[csi_valid[i+1]-1,ip*2+1:ip*3]])
        #Grocery
        grocery_inp = X_valid[csi_valid[i]:csi_valid[i+1],ip*3]
        grocery_inp = np.concatenate([grocery_inp,X_valid[csi_valid[i+1]-1,ip*3+1:ip*4]])
        #Transit
        transit_inp = X_valid[csi_valid[i]:csi_valid[i+1],ip*4]
        transit_inp = np.concatenate([transit_inp,X_valid[csi_valid[i+1]-1,ip*4+1:ip*5]])
        #Work
        work_inp = X_valid[csi_valid[i]:csi_valid[i+1],ip*5]
        work_inp = np.concatenate([work_inp,X_valid[csi_valid[i+1]-1,ip*5+1:ip*6]])
        #Residential
        res_inp = X_valid[csi_valid[i]:csi_valid[i+1],ip*6]
        res_inp = np.concatenate([res_inp,X_valid[csi_valid[i+1]-1,ip*6+1:ip*7]])
        #Predicted and true
        country_pred = pred[csi_valid[i]:csi_valid[i+1]]
        country_true = y_valid[csi_valid[i]:csi_valid[i+1]]
        #Plot
        #Input data
        #Deaths
        days = np.arange(len(country_true)+ip+pl)
        dpm_x = np.zeros(len(days))
        dpm_x[:len(country_death_inp)]=country_death_inp
        ax2.bar(days,dpm_x,color='b',alpha=0.3, label='Death input')
        #Mobility input
        days = np.arange(len(country_death_inp))
        mob = np.zeros(len(days))
        mob[:len(country_death_inp)]=retail_inp
        ax1.plot(days,mob,color='tab:red')
        mob[:len(country_death_inp)]=grocery_inp
        ax1.plot(days,mob,color='tab:purple')
        mob[:len(country_death_inp)]=transit_inp
        ax1.plot(days,mob,color='tab:pink')
        mob[:len(country_death_inp)]=work_inp
        ax1.plot(days,mob,color='tab:olive')
        mob[:len(country_death_inp)]=res_inp
        ax1.plot(days,mob,color='tab:cyan')
        #True
        days = np.arange(len(country_death_inp)+pl)
        dpm_true = np.zeros(len(days))
        try:
            dpm_true[-len(country_true):]=country_true
        except:
            pdb.set_trace()
        ax2.plot(days, dpm_true, color='g', alpha = 0.3, label='True')
        #Pred
        dpm_pred = np.zeros(len(days))
        dpm_pred[-len(country_true):]=country_pred
        ax2.bar(days, dpm_pred, color='r', alpha = 0.3, label='Pred')
        ax1.set_title(countries[i])
        fig.legend()
        fig.tight_layout()
        fig.savefig(outdir+countries[i]+'_pred.png',  format='png')
        plt.close()

#####MAIN#####
#Set random seed to ensure same random split every time
np.random.seed(seed=0)
#Set font size
matplotlib.rcParams.update({'font.size': 9})
args = parser.parse_args()
epidemic_data = pd.read_csv(args.epidemic_data[0])
mobility_data = pd.read_csv(args.mobility_data[0])
outdir = args.outdir[0]
#Extract data and smooth
extract = False
if extract == True:
    extracted_data= format_data(epidemic_data, mobility_data, outdir)
else:
    extracted_data = pd.read_csv('extracted_data.csv')
#Construct features
get_features = False
if get_features == True:
    X, y, csi, fetched_countries = construct_features(extracted_data)
    np.save('X.npy',X)
    np.save('y.npy',y)
    np.save('csi.npy',csi)
    np.save('fetched_countries.npy',fetched_countries)
else:
    X = np.load('X.npy',allow_pickle = True)
    y = np.load('y.npy',allow_pickle = True)
    csi = np.load('csi.npy',allow_pickle = True)
    fetched_countries = np.load('fetched_countries.npy',allow_pickle = True)

#Construct 5-fold CV
X_train, y_train, csi_train, train_countries, X_valid, y_valid, csi_valid, valid_countries = CV_split(X,y,csi,fetched_countries)
for split in range(1,6):
    #Train
    X_train_split = np.array(X_train[split])
    y_train_split = np.array(y_train[split])
    csi_train_split = csi_train[split]
    train_countries_split = train_countries[split]
    X_valid_split = np.array(X_valid[split])
    y_valid_split = np.array(y_valid[split])
    csi_valid_split = csi_valid[split]
    valid_countries_split = valid_countries[split]
    train(X_train_split,y_train_split, X_valid_split, y_valid_split, csi_train_split, csi_valid_split,valid_countries_split,outdir+'split'+str(split)+'/')
