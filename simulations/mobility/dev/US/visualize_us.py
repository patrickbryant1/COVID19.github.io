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
import datetime


import pdb



#Arguments for argparse module:
parser = argparse.ArgumentParser(description = '''Visuaize results from model using google mobility data for all US states''')

parser.add_argument('--indir', nargs=1, type= str, default=sys.stdin, help = 'Path to directory with results.')
parser.add_argument('--complete_df', nargs=1, type= str, default=sys.stdin, help = 'Dataframe with all state data used for modelling.')
parser.add_argument('--lockdown_df', nargs=1, type= str, default=sys.stdin, help = 'Dataframe with continued lockdown results.')
parser.add_argument('--short_dates', nargs=1, type= str, default=sys.stdin, help = 'Short date format for plotting (csv).')
parser.add_argument('--outdir', nargs=1, type= str, default=sys.stdin, help = 'Path to outdir.')



def visualize_results(complete_df, lockdown_df, indir, short_dates, outdir):
    '''Visualize results
    '''

    #Read in data
    #For models fit using MCMC, also included in the summary are the
    #Monte Carlo standard error (se_mean), the effective sample size (n_eff),
    #and the R-hat statistic (Rhat).
    summary = pd.read_csv(indir+'summary.csv')
    alphas = np.load(indir+'alpha.npy', allow_pickle=True)
    phi = np.load(indir+'phi.npy', allow_pickle=True)
    #Plot rhat
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.hist(summary['Rhat'])
    ax.set_ylabel('Count')
    ax.set_xlabel("Rhat")
    fig.savefig(outdir+'plots/rhat.png', format='png', dpi=300)
    plt.close()

    #Plot values from each iteration as r function mcmc_parcoord
    covariate_names = ['retail_and_recreation_percent_change_from_baseline',
   'grocery_and_pharmacy_percent_change_from_baseline',
   'transit_stations_percent_change_from_baseline',
   'workplaces_percent_change_from_baseline']
    mcmc_parcoord(np.concatenate([alphas,np.expand_dims(phi,axis=1)], axis=1), covariate_names+['phi'], outdir)

    #Plot alpha (Rt = R0*exp(sum{mob_change*alpha1-6}))
    fig, ax = plt.subplots(figsize=(9/2.54, 9/2.54))
    alpha_colors = {0:'tab:red',1:'tab:purple',2:'tab:pink', 3:'tab:olive', 4:'tab:cyan'}
    for i in range(1,6):
        alpha = summary[summary['Unnamed: 0']=='alpha['+str(i)+']']
        alpha_m = 1-np.exp(-100*alpha['mean'].values[0])
        alpha_2_5 = 1-np.exp(-100*alpha['2.5%'].values[0])
        alpha_25 = 1-np.exp(-100*alpha['25%'].values[0])
        alpha_75 = 1-np.exp(-100*alpha['75%'].values[0])
        alpha_97_5 = 1-np.exp(-100*alpha['97.5%'].values[0])
        ax.plot([i-0.25,i+0.25],[alpha_m,alpha_m],color = alpha_colors[i-1])
        ax.plot([i]*2,[alpha_2_5,alpha_97_5],  marker = '_',color = alpha_colors[i-1])
        rect = Rectangle((i-0.25,alpha_25),0.5,alpha_75-alpha_25,linewidth=1, color = alpha_colors[i-1], alpha = 0.3)
        ax.add_patch(rect)
    ax.set_ylim([0,1])
    ax.set_ylabel('Fractional reduction in R0')
    ax.set_xticks([1,2,3,4,5])
    ax.set_xticklabels(['retail and recreation', 'grocery and pharmacy', 'transit stations','workplace', 'residential'],rotation='vertical')
    plt.tight_layout()
    fig.savefig(outdir+'plots/alphas.png', format='png', dpi=300)
    plt.close()

    #Plot per state
    states = complete_df['region'].unique()
    # montage_file = open(outdir+'/plots/montage.sh','w')
    # montage_file.write('montage ')
    for i in range(1,len(states)+1):

        state= states[i-1]
        #Get att data for state i
        state_data = complete_df[complete_df['region']==state]
        observed_deaths = state_data['deaths']
        days = len(state_data)#Number of days for state i
        #Lockdown data
        state_lockdown = lockdown_df[lockdown_df['state']==state]
        state_lockdown = state_lockdown.reset_index()
        #Extract modeling results
        means = {'prediction':np.zeros((days)),'E_deaths':np.zeros((days)), 'Rt':np.zeros((days))}
        lower_bound = {'prediction':np.zeros((days)),'E_deaths':np.zeros((days)), 'Rt':np.zeros((days))} #Estimated 2.5 %
        higher_bound = {'prediction':np.zeros((days)),'E_deaths':np.zeros((days)), 'Rt':np.zeros((days))} #Estimated 97.5 % - together 95 % CI
        lower_bound25 = {'prediction':np.zeros((days)),'E_deaths':np.zeros((days)), 'Rt':np.zeros((days))} #Estimated 25%
        higher_bound75 = {'prediction':np.zeros((days)),'E_deaths':np.zeros((days)), 'Rt':np.zeros((days))} #Estimated 55 % - together 75 % CI
        #Get means and 95 % CI for cases (prediction), deaths and Rt for all time steps
        for j in range(1,days+1):
            for var in ['prediction', 'E_deaths','Rt']:
                    var_ij = summary[summary['Unnamed: 0']==var+'['+str(j)+','+str(i)+']']
                    means[var][j-1]=var_ij['mean'].values[0]
                    lower_bound[var][j-1]=var_ij['2.5%'].values[0]
                    higher_bound[var][j-1]=var_ij['97.5%'].values[0]
                    lower_bound25[var][j-1]=var_ij['25%'].values[0]
                    higher_bound75[var][j-1]=var_ij['75%'].values[0]

        #Plot cases
        #Per day
        plot_shade_ci(days, state_data,state_lockdown, 'cases', means['prediction'],lower_bound['prediction'],
        higher_bound['prediction'], lower_bound25['prediction'], higher_bound75['prediction'], 'Cases per day',
        outdir+'plots/'+state+'_cases.png', short_dates)

        #Plot Deaths
        #Per day
        plot_shade_ci(days,state_data,state_lockdown,'deaths',means['E_deaths'], lower_bound['E_deaths'], higher_bound['E_deaths'],
        lower_bound25['E_deaths'], higher_bound75['E_deaths'], 'Deaths per day',
        outdir+'plots/'+state+'_deaths.png', short_dates)
        #Plot R
        plot_shade_ci(days,state_data,state_lockdown,'Rt',means['Rt'], lower_bound['Rt'], higher_bound['Rt'], lower_bound25['Rt'],
        higher_bound75['Rt'],'Rt',outdir+'plots/'+state+'_Rt.png', short_dates)

        #Print deaths at end point vs deaths at end point if continued lockdown
        print(state+','+str(np.round(np.array(state_data['deaths'])[-1],0))+','+str(np.round(means['E_deaths'][-1],0))+','+str(np.round(np.array(state_lockdown['mean_deaths'])[-1],0)))
    #     #Print for montage
    #     montage_file.write(state+'_cases.png '+state+'_deaths.png '+state+'_Rt.png ')
    #
    #     if i%9==0:
    #         montage_file.write(' -tile 3x9 -geometry +2+2 all_states'+str(i)+'.png\nmontage ')
    # montage_file.write(' -tile 3x9 -geometry +2+2 all_states'+str(i)+'.png')
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

def plot_shade_ci(days, state_data, state_lockdown, param, means, lower_bound, higher_bound, lower_bound25, higher_bound75, ylabel, outname, short_dates):
    '''Plot with shaded 95 % CI (plots both 1 and 2 std, where 2 = 95 % interval)
    '''
    dates = state_data['date']
    selected_short_dates = np.array(short_dates[short_dates['np_date'].isin(dates)]['short_date']) #Get short version of dates
    x = np.arange(days)#x-vals
    if len(dates) != len(selected_short_dates):
        pdb.set_trace()
    fig, ax1 = plt.subplots(figsize=(6/2.54, 4.5/2.54))

    #Plot observed dates
    if param=='deaths':
        ax1.bar(x,np.round(state_data[param],0), alpha = 0.5)
    #Plot simulation
    ax1.plot(x,means, alpha=0.5, linewidth = 2.0, color = 'b')
    ax1.fill_between(x, lower_bound, higher_bound, color='cornflowerblue', alpha=0.4)
    ax1.fill_between(x, lower_bound25, higher_bound75, color='cornflowerblue', alpha=0.6)

    #Plot continued lockdown
    exi = int(state_lockdown['extreme_index'].values[0])
    try:
        ax1.plot(x[exi:],state_lockdown.loc[exi:,'mean_'+param], alpha=0.5, linewidth = 2.0, color = 'g')
    except:
        pdb.set_trace()
    ax1.fill_between(x[exi:],state_lockdown.loc[exi:,'lower_'+param], state_lockdown.loc[exi:,'higher_'+param], color='seagreen', alpha=0.4)
    ax1.fill_between(x[exi:],state_lockdown.loc[exi:,'lower25_'+param], state_lockdown.loc[exi:,'higher75_'+param], color='seagreen', alpha=0.6)

    #Mobility
    mob_keys = {'retail_and_recreation_percent_change_from_baseline':'tab:red',
                'grocery_and_pharmacy_percent_change_from_baseline':'tab:purple',
                'transit_stations_percent_change_from_baseline':'tab:pink',
                'workplaces_percent_change_from_baseline':'tab:olive',
                'residential_percent_change_from_baseline':'tab:cyan'}
    #Plot mobility data
    #Use a twin of the other x axis
    ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis
    for key in mob_keys:
        ax2.plot(x,state_data[key], alpha=0.5, color=mob_keys[key], linewidth = 2.0)
    #Plot formatting
    #ax1
    ax1.set_ylabel(ylabel)
    ax1.set_title(state_data['region'].unique()[0])
    xticks=np.arange(len(x)-1,0,-14)
    ax1.set_xticks(xticks)
    try:
        ax1.set_xticklabels(selected_short_dates[xticks],rotation='vertical')
    except:
        pdb.set_trace()
    if ylabel=='Rt':
        ax1.set_ylim([0,max(higher_bound)+0.5])
        ax1.hlines(1,0,max(xticks),linestyles='dashed',linewidth=1)
    #ax2
    ax2.set_ylim([-80,40])
    ax2.set_yticks([-50,-25,0,25])
    #Hide
    ax1.spines['top'].set_visible(False)
    ax2.spines['top'].set_visible(False)
    #fig
    fig.tight_layout()
    fig.savefig(outname, format = 'png')

    plt.close()

def plot_markers():
    '''Plot the marker explanations
    '''
    #Mobility
    covariate_colors = {'retail and recreation':'tab:red','grocery and pharmacy':'tab:purple', 'transit stations':'tab:pink','workplace':'tab:olive','residential':'tab:cyan'}
    fig, ax = plt.subplots(figsize=(6/2.54,2.25/2.54))
    i=5
    for cov in covariate_colors:
        ax.plot([1,1.8],[i]*2, color = covariate_colors[cov], linewidth=4)
        ax.text(2.001,i,cov)
        i-=1
    ax.set_xlim([0.999,4])
    ax.axis('off')
    fig.savefig(outdir+'plots/mobility_markers.png', format = 'png')

    #Simulation and forecast
    fig, ax = plt.subplots(figsize=(6/2.54,2.25/2.54))
    ax.plot([1,1.8],[1.55]*2, color ='b', linewidth=8, alpha = 0.5)
    ax.text(2.001,1.543,'Observed deaths')
    ax.plot([1,1.8],[1.5]*2, color = 'b', linewidth=8)
    ax.text(2.001,1.493,'Lockdown Relief')
    ax.plot([1,1.8],[1.45]*2, color ='g', linewidth=8)
    ax.text(2.001,1.443,'Continued Lockdown')
    ax.set_xlim([0.999,3.02])
    ax.set_ylim([1.42,1.57])
    ax.axis('off')
    fig.savefig(outdir+'plots/sim_markers.png', format = 'png')

def visualize_mobility(complete_df, lockdown_df, short_dates, outdir):
    '''Visualize the mobility change per state
    '''

    titles =  {1:'Retail and recreation',2:'Grocery and pharmacy', 3:'Transit stations',4:'Workplace',5:'Residential',6:'Parks'}
    mob_keys = {'retail_and_recreation_percent_change_from_baseline':'tab:red',
                'grocery_and_pharmacy_percent_change_from_baseline':'tab:purple',
                'transit_stations_percent_change_from_baseline':'tab:pink',
                'workplaces_percent_change_from_baseline':'tab:olive',
                'residential_percent_change_from_baseline':'tab:cyan',
                'parks_percent_change_from_baseline':'tab:green'}
    states = complete_df['region'].unique()

    for plot_lockdown in [True, False]:
        i=1
        for key in mob_keys:
            fig, ax = plt.subplots(figsize=(7/2.54,7/2.54))
            for state in states:
                state_data = complete_df[complete_df['region']==state]
                #Reset index
                state_data = state_data.reset_index()
                if plot_lockdown == True:
                    #Plot continued lockdown
                    exi = int(lockdown_df[lockdown_df['state']==state]['extreme_index'].values[0])
                    lock_val = state_data.loc[exi,key]
                    state_data.loc[exi:,key]=lock_val
                ax.plot(state_data['date'],state_data[key],color=mob_keys[key])
            #Formatting
            ax.set_ylabel('Mobility change')
            ax.set_title(titles[i])
            #Dates
            start = min(complete_df['date'])
            end = max(complete_df['date'])
            dates=np.arange(start,end+datetime.timedelta(days=1), dtype='datetime64[D]')
            selected_short_dates = np.array(short_dates[short_dates['np_date'].isin(dates)]['short_date']) #Get short version of dates
            #xticks=np.arange(0,len(dates),14)
            #ax.set_xticklabels(selected_short_dates,rotation='vertical')
            plt.xticks(rotation='vertical')
            #Hide
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            fig.tight_layout()
            if plot_lockdown == True:
                fig.savefig(outdir+str(i)+'_extreme.png', format = 'png')
            else:
                fig.savefig(outdir+str(i)+'.png', format = 'png')
            i+=1


#####MAIN#####
#Set font size
matplotlib.rcParams.update({'font.size': 7})
args = parser.parse_args()
indir = args.indir[0]
complete_df = pd.read_csv(args.complete_df[0])
#Convert to datetime
complete_df['date']=pd.to_datetime(complete_df['date'], format='%Y/%m/%d')
lockdown_df = pd.read_csv(args.lockdown_df[0])
short_dates = pd.read_csv(args.short_dates[0])

#Make sure the np dates are in the correct format
short_dates['np_date'] = pd.to_datetime(short_dates['np_date'], format='%Y/%m/%d')
outdir = args.outdir[0]
#Visualize the mobility data
visualize_mobility(complete_df, lockdown_df, short_dates, outdir)
#Plot the markers
plot_markers()

pdb.set_trace()
#Visualize
visualize_results(complete_df, lockdown_df, indir, short_dates, outdir)
