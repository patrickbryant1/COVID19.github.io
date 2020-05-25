#! /usr/bin/env python3
# -*- coding: utf-8 -*-


import argparse
import sys
import os
import glob
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from scipy.signal import savgol_filter
from scipy.stats import pearsonr
import pdb



#Arguments for argparse module:
parser = argparse.ArgumentParser(description = '''Generate signals for mobility data and R estimates, then correlate time delay.''')

parser.add_argument('--R_estimates', nargs=1, type= str, default=sys.stdin, help = 'Path to dir with R estimates per country.')
parser.add_argument('--epidemic_data', nargs=1, type= str, default=sys.stdin, help = 'Path to eidemic data (csv).')
parser.add_argument('--mobility_data', nargs=1, type= str, default=sys.stdin, help = 'Google mobility data (csv).')
parser.add_argument('--outdir', nargs=1, type= str, default=sys.stdin, help = 'Path to outdir.')

###FUNCTIONS###
def construct_signals(R_estimates, epidemic_data, mobility_data, outdir, above_t, outname, days_to_include):
        '''Read in and format all data needed for the signal correlation analysis
        '''

        #Convert epidemic data to datetime
        epidemic_data['dateRep'] = pd.to_datetime(epidemic_data['dateRep'], format='%d/%m/%Y')
        #Rename date to date
        epidemic_data = epidemic_data.rename(columns={'dateRep':'date'})
        #Convert mobility data to datetime
        mobility_data['date'] = pd.to_datetime(mobility_data['date'], format='%Y/%m/%d')
        #Get epidemic data due to last mobility date, 2020-05-09
        epidemic_data = epidemic_data[epidemic_data['date']<=max(mobility_data['date'])]
        #Mobility key conversions
        key_conversions = {'United_States_of_America':'United_States'}

        #Covariate names
        covariate_names = ['retail_and_recreation_percent_change_from_baseline',
                           'grocery_and_pharmacy_percent_change_from_baseline',
                           'transit_stations_percent_change_from_baseline',
                           'workplaces_percent_change_from_baseline',
                           'residential_percent_change_from_baseline']

        #Save fetched countries for montage script
        fetched_countries = []
        #Save correlations for overlay
        C_mob_delay_all = []
        C_R_delay_all = []
        #Save start dates for epidemic data
        start_dates = []
        #days before 80 % mark
        days_before_80 = []
        #days after 80 % mark
        days_after_80 = []
        #Get unique countries
        countries = epidemic_data['countriesAndTerritories'].unique()
        for country in countries:
            try:
                country_R = pd.read_csv(R_estimates+country+'_R_estimate.csv')
            except:
                print('Cant read '+country+'_R_estimate.csv' )
                continue
            #Fix datetime
            country_R['date'] = pd.to_datetime(country_R['date'], format='%d/%m/%Y')
            #Get R estimates due to last mobility date, 2020-05-09
            country_R = country_R[country_R['date']<=max(mobility_data['date'])]
            #Select R values below 5
            country_R = country_R[country_R['Median(R)']<=5]
            #Get country epidemic data
            country_epidemic_data = epidemic_data[epidemic_data['countriesAndTerritories']==country]
            #Sort on date
            country_epidemic_data = country_epidemic_data.sort_values(by='date')
            #Reset index
            country_epidemic_data = country_epidemic_data.reset_index()
            #Get data for day >= t_c, where t_c is the day where 80 % of the max death count has been reached
            death_t = max(country_epidemic_data['deaths'])*0.8
            signal_start = min(country_epidemic_data[country_epidemic_data['deaths']>=death_t].index)
            start_date = country_epidemic_data.loc[signal_start,'date']
            if above_t == True:
                country_epidemic_data = country_epidemic_data.loc[signal_start:]
                #Merge dfs
                country_signal_data = country_epidemic_data.merge(country_R, left_on = 'date', right_on ='date', how = 'left')
            else:
                #Merge dfs
                country_signal_data = country_R.merge(country_epidemic_data, left_on = 'date', right_on ='date', how = 'left')

            #Check enough data is present
            if len(country_signal_data)<days_to_include:
                print(country, len(country_signal_data))
                continue

            #Mobility data from Google
            if country in key_conversions.keys():
                mob_key = key_conversions[country]
            else:
                mob_key = ' '.join(country.split('_'))

            country_mobility_data = mobility_data[mobility_data['country_region']==mob_key]
            #Get whole country - no subregion
            country_mobility_data =  country_mobility_data[country_mobility_data['sub_region_1'].isna()]
            country_mobility_data = country_mobility_data[country_mobility_data['date']<=max(country_signal_data['date'])]
            if len(country_mobility_data)<2:
                print('No mobility data for', country)
                continue
            #Merge
            #Merge to the shortest one
            if len(country_signal_data)>len(country_mobility_data):
                country_signal_data = country_mobility_data.merge(country_signal_data, left_on = 'date', right_on ='date', how = 'left')
            else:
                country_signal_data = country_signal_data.merge(country_mobility_data, left_on = 'date', right_on ='date', how = 'left')

            #Smooth
            country_signal_data['Median(R)'] = savgol_filter(country_signal_data['Median(R)'], 7,3)
            country_signal_data['retail_and_recreation_percent_change_from_baseline'] = savgol_filter(country_signal_data['retail_and_recreation_percent_change_from_baseline'], 7,3)
            country_signal_data['grocery_and_pharmacy_percent_change_from_baseline'] = savgol_filter(country_signal_data['grocery_and_pharmacy_percent_change_from_baseline'], 7,3)
            country_signal_data['transit_stations_percent_change_from_baseline'] = savgol_filter(country_signal_data['transit_stations_percent_change_from_baseline'], 7,3)
            country_signal_data['workplaces_percent_change_from_baseline'] = savgol_filter(country_signal_data['workplaces_percent_change_from_baseline'], 7,3)
            country_signal_data['residential_percent_change_from_baseline'] = savgol_filter(country_signal_data['residential_percent_change_from_baseline'], 7,3)

            #Look at the smoothing
            #compare_smoothing(country_signal_data, outdir)

            #Check that enough days are present
            if len(country_signal_data)<days_to_include+2: #at least 2 extra days for corr
                print(country, 'contains only', len(country_signal_data), 'days of data')
                continue

            #Make an array
            signal_array = np.zeros((6,len(country_signal_data)))
            signal_array[0,:]=country_signal_data['Median(R)']
            signal_array[1,:]=country_signal_data['retail_and_recreation_percent_change_from_baseline']
            signal_array[2,:]=country_signal_data['grocery_and_pharmacy_percent_change_from_baseline']
            signal_array[3,:]=country_signal_data['transit_stations_percent_change_from_baseline']
            signal_array[4,:]=country_signal_data['workplaces_percent_change_from_baseline']
            signal_array[5,:]=country_signal_data['residential_percent_change_from_baseline']

            #Check NaNs
            if len(signal_array[np.isnan(signal_array)])>1:
                print(country, 'contains NaNs')
                #pdb.set_trace()
                continue
            else:
                start_dates.append(start_date) #Save start date
            #Reset index
            country_signal_data = country_signal_data.reset_index()

            if above_t == False:
                #Append number of days before and after 80% threshold
                try:
                    signal_start = min(country_signal_data[country_signal_data['deaths']>=death_t].index)
                    days_before_80.append(signal_start)
                    days_after_80.append(len(country_signal_data)-signal_start)
                except:
                    print(country, 'has too little data')
                    continue

            #Get pearsonr for different time delays in mobility response
            C_mob_delay, C_R_delay = corr_signals(signal_array)

            C_mob_delay_all.append(C_mob_delay)#Save
            C_R_delay_all.append(C_R_delay)
            #Plot per country
            #plot_corr(C_mob_delay, C_R_delay, outdir, country, 'Pearson R')
            #For montage script
            fetched_countries.append(country)
            #Sanity check - see origin of all corr >0.5
            sanity_check(C_mob_delay[:,:days_to_include], C_R_delay[:,:days_to_include], signal_array, outdir, country)
            #Plot R and mobility
            plot_R_mobility(country_signal_data, country, outdir)
        #Plot start dates
        plot_start_dates(start_dates, outdir)
        #Plot all countries in overlap per mobility category
        plot_corr_all_countries(C_mob_delay_all, C_R_delay_all, 'Pearson R', outdir, days_to_include, fetched_countries, outname)

        #Write montage script
        #write_montage(fetched_countries, outdir)
def plot_R_mobility(country_signal_data, country, outdir):
    '''Plot mobility and R
    '''
    fig, ax1 = plt.subplots(figsize=(9/2.54, 9/2.54))
    x=np.arange(len(country_signal_data))
    ax1.plot(x, country_signal_data['Median(R)'], color = 'b', linewidth=2)
    ax2 = ax1.twinx()
    ax2.plot(x,country_signal_data['retail_and_recreation_percent_change_from_baseline'], alpha=0.5, color='tab:red', linewidth = 1.0)
    ax2.plot(x,country_signal_data['grocery_and_pharmacy_percent_change_from_baseline'], alpha=0.5, color='tab:purple', linewidth = 1.0)
    ax2.plot(x,country_signal_data['transit_stations_percent_change_from_baseline'], alpha=0.5, color='tab:pink', linewidth = 1.0)
    ax2.plot(x,country_signal_data['workplaces_percent_change_from_baseline'], alpha=0.5, color='tab:olive', linewidth = 1.0)
    ax2.plot(x,country_signal_data['residential_percent_change_from_baseline'], alpha=0.5, color='tab:cyan', linewidth = 1.0)
    xticks=np.arange(0,len(country_signal_data),7)
    ax1.set_xticks(xticks)
    ax1.set_xticklabels(np.array(country_signal_data['date'], dtype='datetime64[D]')[xticks], rotation='vertical')
    ax1.set_title(country)
    ax1.set_ylabel('Median R')
    ax2.set_ylabel('Mobility change')
    fig.tight_layout()
    fig.savefig(outdir+'sanity_check/'+country+'R_and_mobility.png',  format='png')


def plot_start_dates(start_dates, outdir):
    '''Plot date for start of included
    date per country
    '''
    fig, ax = plt.subplots(figsize=(12/2.54, 9/2.54))
    ax.hist(start_dates)
    ax.set_xlabel('Date for 80% of max deaths')
    fig.tight_layout()
    fig.savefig(outdir+'all/80_date_distribution.png',  format='png')
    plt.close()

def sanity_check(C_mob_delay, C_R_delay, signal_array, outdir, country):
    '''Sanity check - see origin of all corr >0.5
    '''
    pos_above_05 = np.where(C_mob_delay<=-0.5)
    fig, ax = plt.subplots(figsize=(9/2.54, 9/2.54))
    ncols=0 #Number of plotted curves
    for i in range(len(pos_above_05[0])):
        #plot R against mobility
        n = pos_above_05[0][i]
        m = pos_above_05[1][i]
        if m ==0:
            R_data = signal_array[0,:]
            mob_data = signal_array[n+1,:]
        else:
            R_data = signal_array[0,:-m]
            mob_data = signal_array[n+1,m:]
        if n==2 and m<=21 and m>=10:
            plt.plot(R_data,mob_data)
            plt.scatter(R_data,mob_data, label=m, s=5)
            ncols+=1

    ax.set_title(country)
    ax.set_xlabel('R')
    ax.set_ylabel('retail mobility')
    plt.legend(loc="lower left", mode = "expand", ncol = ncols)
    fig.tight_layout()
    fig.savefig(outdir+'sanity_check/'+country+'.png',  format='png')
    plt.close()

def corr_signals(signal_array):
    '''Analyze the correlation of the R values with the mobility data
    using different time delays (s)
    '''
    s_max = signal_array.shape[1]
    C_mob_delay = np.zeros((5,s_max-2)) #Save covariance btw signals for different delays in mobility
    C_R_delay = np.zeros((5,s_max-2)) #Save covariance btw signals for different delays in R
    #Loop through all s and calculate correlations
    for s in range(s_max-2): #s is the number of future days to correlate the mobility data over
        for m in range(1,6):#all mobility data
            if s == 0:
                c_mob = pearsonr(signal_array[0,:],signal_array[m,s:])[0]
                c_R = pearsonr(signal_array[m,:],signal_array[0,s:])[0]#pos 0 of the array contains the R values
            else:
                c_mob = pearsonr(signal_array[0,:-s],signal_array[m,s:])[0]
                c_R = pearsonr(signal_array[m,:-s],signal_array[0,s:])[0]
            #Assign correlation
            C_mob_delay[m-1,s]=c_mob
            C_R_delay[m-1,s]=c_R
    return C_mob_delay, C_R_delay


def plot_corr_all_countries(C_mob_delay_all, C_R_delay_all, ylabel, outdir, days_to_include, fetched_countries, outname):
    '''Plot all countries in overlay per mobility category
    '''

    keys = ['retail and recreation', 'grocery and pharmacy',
            'transit stations','workplaces','residential']
    colors = ['Reds','Purples','Oranges','Greens','Blues']


    #Mobility delay
    for i in range(5):
        all_countries_x = []
        all_countries_y = []
        plotted_countries = 0
        fig, ax = plt.subplots(figsize=(9/2.54, 9/2.54))
        for j in range(len(C_mob_delay_all)):
            if C_mob_delay_all[j].shape[1]<days_to_include:
                print(fetched_countries[j], 'has too little data')
                continue
            else:
                plotted_countries +=1
                #Save all country correltions with delays from 0 to days_to_include
                all_countries_x.extend(np.arange(days_to_include))
                all_countries_y.extend(C_mob_delay_all[j][i,:days_to_include])
                all_countries_x.extend(-np.arange(days_to_include)) #The R delay is the negative mobility delay
                all_countries_y.extend(C_R_delay_all[j][i,:days_to_include])
        sns.kdeplot(all_countries_x,all_countries_y, shade = True, cmap = colors[i])
        ax.set_title(keys[i])
        ax.set_xlabel('mobility time delay (days)')
        ax.set_ylabel(ylabel)
        ax.set_xlim([-days_to_include-2, days_to_include+2])
        fig.tight_layout()
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        fig.savefig(outdir+'all/'+keys[i]+outname,  format='png')
        plt.close()
        print('Plotting',plotted_countries, 'countries')

def plot_corr(C_mob_delay, C_R_delay, outdir, country, ylabel):
    '''Plot the covariance btw the R values
    and different time delays (s)
    '''
    keys = ['retail and recreation', 'grocery and pharmacy',
            'transit stations','workplaces','residential']
    colors = ['tab:red','tab:purple','tab:pink','tab:olive','tab:cyan']

    #Mobility delay
    fig, ax = plt.subplots(figsize=(6/2.54, 6/2.54))
    for i in range(5):
        ax.plot(range(C_mob_delay.shape[1]),C_mob_delay[i,:], label=keys[i], color = colors[i], linewidth = 1.0)
    ax.set_title(country)
    ax.set_xlabel('mobility time delay (days)')
    ax.set_ylim([-1,1])
    #ax.set_xlim([0,40])
    ax.set_ylabel(ylabel)
    fig.tight_layout()
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    fig.savefig(outdir+country+'_mobility_delay.png',  format='png')
    plt.close()
    #R delay
    fig, ax = plt.subplots(figsize=(6/2.54, 6/2.54))
    for i in range(5):
        ax.plot(range(C_R_delay.shape[1]),C_R_delay[i,:], label=keys[i], color = colors[i], linewidth = 1.0)
    ax.set_title(country)
    ax.set_xlabel('R0 time delay (days)')
    ax.set_ylim([-1,1])
    #ax.set_xlim([0,40])
    ax.set_ylabel(ylabel)
    fig.tight_layout()
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    fig.savefig(outdir+country+'_R_delay.png',  format='png')
    plt.show()
    plt.close()

def write_montage(fetched_countries, outdir):
    '''Write script for montage
    '''
    with open(outdir+'/sanity_check/montage.sh', 'w') as file:
        file.write('OUTDIR=/home/patrick/COVID19.github.io/docs/assets\n')
        fig_num=1
        for i in range(0,len(fetched_countries)-9,9):
            file.write('    montage '+'.png '.join(fetched_countries[i:i+9])+'.png -tile 3x3 -geometry +2+2 /countries_'+str(fig_num)+'.png\n')
            fig_num+=1


def compare_smoothing(country_signal_data, outdir):
    '''Compare different kinds of smoothing
    '''
    keys = ['Median(R)', 'retail_and_recreation_percent_change_from_baseline',
    'grocery_and_pharmacy_percent_change_from_baseline',
    'transit_stations_percent_change_from_baseline',
    'workplaces_percent_change_from_baseline',
    'residential_percent_change_from_baseline']

    for key in keys:
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.plot(range(len(country_signal_data)),country_signal_data[key], label='No smoothing')
        #savgol
        savgol_smoothing = savgol_filter(country_signal_data[key], 7,3)
        ax.plot(range(len(country_signal_data)),savgol_smoothing, label='Savgol smoothing')
        ax.set_title(key)
        plt.legend()
        fig.savefig(outdir+'smoothing/'+key+'.png',  format='png', dpi=300)


#####MAIN#####
#Set font size
matplotlib.rcParams.update({'font.size': 9})
args = parser.parse_args()
R_estimates = args.R_estimates[0]
epidemic_data = pd.read_csv(args.epidemic_data[0])
mobility_data = pd.read_csv(args.mobility_data[0])
outdir = args.outdir[0]

#Construct signals
#above_t = False #get data above threshold or not
#outname='_mobility_delay_all_whole_epi.png'
#days_to_include=28
#construct_signals(R_estimates, epidemic_data, mobility_data, outdir, above_t, outname, days_to_include)
#print('Whole plotted')
above_t = True #get data above threshold or not
outname='_mobility_delay_all_above_80.png'
days_to_include=21
construct_signals(R_estimates, epidemic_data, mobility_data, outdir, above_t, outname, days_to_include)
print('Above 80 plotted')
