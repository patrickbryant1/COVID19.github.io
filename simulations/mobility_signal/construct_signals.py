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
def construct_signals(R_estimates, epidemic_data, mobility_data, outdir):
        '''Read in and format all data needed for the signal correlation analysis
        '''

        #Convert epidemic data to datetime
        epidemic_data['dateRep'] = pd.to_datetime(epidemic_data['dateRep'], format='%d/%m/%Y')
        #Convert mobility data to datetime
        mobility_data['date'] = pd.to_datetime(mobility_data['date'], format='%Y/%m/%d')
        #Get epidemic data due to last mobility date, 2020-05-09
        epidemic_data = epidemic_data[epidemic_data['dateRep']<=max(mobility_data['date'])]
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
            #Get country epidemic data
            country_epidemic_data = epidemic_data[epidemic_data['countriesAndTerritories']==country]
            #Sort on date
            country_epidemic_data = country_epidemic_data.sort_values(by='dateRep')
            #Reset index
            country_epidemic_data = country_epidemic_data.reset_index()
            #Get data for day >= t_c, where t_c is the day where 80 % of the max death count has been reached
            death_t = max(country_epidemic_data['deaths'])*0.8
            signal_start = min(country_epidemic_data[country_epidemic_data['deaths']>=death_t].index)
            country_epidemic_data = country_epidemic_data.loc[signal_start:]
            start_dates.append(country_epidemic_data.loc[signal_start,'dateRep'])
            #Merge dfs
            #country_signal_data = country_R.merge(country_epidemic_data, left_on = 'date', right_on ='dateRep', how = 'left')
            country_signal_data = country_epidemic_data.merge(country_R, left_on = 'dateRep', right_on ='date', how = 'left')

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
            country_signal_data = country_signal_data.merge(country_mobility_data, left_on = 'dateRep', right_on ='date', how = 'left')
            #if min(country_signal_data['date'])<min(country_mobility_data['date']):
            #    country_signal_data = country_mobility_data.merge(country_signal_data, left_on = 'date', right_on ='date', how = 'left')
            #else:
            #    country_signal_data = country_signal_data.merge(country_mobility_data, left_on = 'date', right_on ='date', how = 'left')
            #Construct signals
            country_signal_data['R_signal'] = 0
            country_signal_data['retail_signal'] = 0
            country_signal_data['grocery_signal'] = 0
            country_signal_data['transit_signal'] = 0
            country_signal_data['workplaces_signal'] = 0
            country_signal_data['residential_signal'] = 0
            #Look at the smoothing
            #compare_smoothing(country_signal_data, outdir)
            #Smooth
            if len(country_signal_data)<=7:
                print(country, len(country_signal_data))
                continue
            country_signal_data['Median(R)'] = savgol_filter(country_signal_data['Median(R)'], 7,3)
            country_signal_data['retail_and_recreation_percent_change_from_baseline'] = savgol_filter(country_signal_data['retail_and_recreation_percent_change_from_baseline'], 7,3)
            country_signal_data['grocery_and_pharmacy_percent_change_from_baseline'] = savgol_filter(country_signal_data['grocery_and_pharmacy_percent_change_from_baseline'], 7,3)
            country_signal_data['transit_stations_percent_change_from_baseline'] = savgol_filter(country_signal_data['transit_stations_percent_change_from_baseline'], 7,3)
            country_signal_data['workplaces_percent_change_from_baseline'] = savgol_filter(country_signal_data['workplaces_percent_change_from_baseline'], 7,3)
            country_signal_data['residential_percent_change_from_baseline'] = savgol_filter(country_signal_data['residential_percent_change_from_baseline'], 7,3)

            #Calculate signals
            for i in range(len(country_signal_data)-1): #loop through data to construct signal
                row_i = country_signal_data.loc[i]
                row_i_1 = country_signal_data.loc[i+1]
                country_signal_data.loc[i+1,'R_signal']=row_i_1['Median(R)']-row_i['Median(R)']
                country_signal_data.loc[i+1,'retail_signal']=row_i_1['retail_and_recreation_percent_change_from_baseline']-row_i['retail_and_recreation_percent_change_from_baseline']
                country_signal_data.loc[i+1,'grocery_signal']=row_i_1['grocery_and_pharmacy_percent_change_from_baseline']-row_i['grocery_and_pharmacy_percent_change_from_baseline']
                country_signal_data.loc[i+1,'transit_signal']=row_i_1['transit_stations_percent_change_from_baseline']-row_i['transit_stations_percent_change_from_baseline']
                country_signal_data.loc[i+1,'workplaces_signal']=row_i_1['workplaces_percent_change_from_baseline']-row_i['workplaces_percent_change_from_baseline']
                country_signal_data.loc[i+1,'residential_signal']=row_i_1['residential_percent_change_from_baseline']-row_i['residential_percent_change_from_baseline']
            #Make an array
            signal_array = np.zeros((6,len(country_signal_data)-1))
            # signal_array[0,:]=country_signal_data['R_signal'][1:]
            # signal_array[1,:]=country_signal_data['retail_signal'][1:]
            # signal_array[2,:]=country_signal_data['grocery_signal'][1:]
            # signal_array[3,:]=country_signal_data['transit_signal'][1:]
            # signal_array[4,:]=country_signal_data['workplaces_signal'][1:]
            # signal_array[5,:]=country_signal_data['residential_signal'][1:]
            signal_array[0,:]=country_signal_data['Median(R)'][1:]
            signal_array[1,:]=country_signal_data['retail_and_recreation_percent_change_from_baseline'][1:]
            signal_array[2,:]=country_signal_data['grocery_and_pharmacy_percent_change_from_baseline'][1:]
            signal_array[3,:]=country_signal_data['transit_stations_percent_change_from_baseline'][1:]
            signal_array[4,:]=country_signal_data['workplaces_percent_change_from_baseline'][1:]
            signal_array[5,:]=country_signal_data['residential_percent_change_from_baseline'][1:]

            #Check NaNs
            if len(signal_array[np.isnan(signal_array)])>1:
                print(country, 'contains NaNs')
                continue
            #Get pearsonr for different time delays in mobility response
            C_mob_delay, C_R_delay = corr_signals(signal_array)
            C_mob_delay_all.append(C_mob_delay)#Save
            C_R_delay_all.append(C_R_delay)
            #Plot
            #plot_corr(C_mob_delay, C_R_delay, outdir, country, 'Pearson R')
            #For montage script
            fetched_countries.append(country)
        pdb.set_trace()
        #Plot all countries in overlap per mobility category
        plot_corr_all_countries(C_mob_delay_all, C_R_delay_all, 'Pearson R', outdir)
        #Write montage script
        write_montage(fetched_countries, outdir)

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

def plot_corr_all_countries(C_mob_delay_all, C_R_delay_all, ylabel, outdir):
    '''Plot all countries in overlay per mobility category
    '''

    keys = ['retail and recreation', 'grocery and pharmacy',
            'transit stations','workplaces','residential']
    colors = ['Reds','Purples','Oranges','Greens','Blues']


    #Mobility delay
    plotted_countries = 0
    days_to_include = 21
    for i in range(5):
        all_countries_x = []
        all_countries_y = []
        fig, ax = plt.subplots(figsize=(6/2.54, 6/2.54))
        for j in range(len(C_mob_delay_all)):
            if C_mob_delay_all[j].shape[1]<days_to_include:
                continue
            else:
                plotted_countries +=1
                all_countries_x.extend(np.arange(days_to_include))
                all_countries_y.extend(C_mob_delay_all[j][i,:days_to_include])
                all_countries_x.extend(-np.arange(days_to_include))
                all_countries_y.extend(C_R_delay_all[j][i,:days_to_include])
            sns.kdeplot(all_countries_x,all_countries_y, shade = True, cmap = colors[i])
        ax.set_title(keys[i])
        ax.set_xlabel('mobility time delay (days)')
        ax.set_ylabel(ylabel)

        fig.tight_layout()
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        fig.savefig(outdir+'all/'+keys[i]+'_mobility_delay_all.png',  format='png')
        plt.close()
    print('Plotting',plotted_countries, 'countries')
    #R delay
    # for i in range(5):
    #     all_countries_x = []
    #     all_countries_y = []
    #     fig, ax = plt.subplots(figsize=(6/2.54, 6/2.54))
    #     for j in range(len(C_mob_delay_all)):
    #         all_countries_x.extend(np.arange(C_R_delay_all[j].shape[1]))
    #         all_countries_y.extend(C_R_delay_all[j][i,:])
    #     sns.kdeplot(all_countries_x,all_countries_y, shade = True, cmap = colors[i])
    #     ax.set_title(keys[i])
    #     ax.set_xlabel('R time delay (days)')
    #     ax.set_ylabel(ylabel)
    #
    #     fig.tight_layout()
    #     ax.spines['top'].set_visible(False)
    #     ax.spines['right'].set_visible(False)
    #     fig.savefig(outdir+'all/'+keys[i]+'_R_delay_all.png',  format='png')
    #     plt.close()



def write_montage(fetched_countries, outdir):
    '''Write script for montage
    '''
    with open(outdir+'montage.sh', 'w') as file:
        file.write('OUTDIR=/home/patrick/COVID19.github.io/docs/assets\n')
        file.write("for type in '_R_delay' '_mobility_delay'\n")
        file.write('  do\n')
        fig_num=1
        for i in range(0,len(fetched_countries)-9,9):
            file.write('    montage '+"$type'.png' ".join(fetched_countries[i:i+9])+"$type'.png' -tile 3x3 -geometry +2+2 $OUTDIR'/countries_"+str(fig_num)+"'$type'.png'\n")
            fig_num+=1
        file.write('done')

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
construct_signals(R_estimates, epidemic_data, mobility_data, outdir)

#Mobility markers
covariate_colors = {'retail and recreation':'tab:red','grocery and pharmacy':'tab:purple', 'transit stations':'tab:pink','workplace':'tab:olive','residential':'tab:cyan'}
fig, ax = plt.subplots(figsize=(6/2.54,2.25/2.54))
i=5
for cov in covariate_colors:
    ax.plot([1,1.8],[i]*2, color = covariate_colors[cov], linewidth=4)
    ax.text(2.001,i,cov)
    i-=1
ax.set_xlim([0.999,3.5])
ax.axis('off')
fig.savefig(outdir+'mobility_markers.png', format = 'png')
