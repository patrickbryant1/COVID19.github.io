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
from scipy.stats import gamma, pearsonr
import numpy as np
import seaborn as sns
import datetime

import pdb



#Arguments for argparse module:
parser = argparse.ArgumentParser(description = '''Visuaize results from model using google mobility data for all US states''')

parser.add_argument('--indir', nargs=1, type= str, default=sys.stdin, help = 'Path to directory with results.')
parser.add_argument('--complete_df', nargs=1, type= str, default=sys.stdin, help = 'Dataframe with all state data used for modelling.')
parser.add_argument('--lockdown_df', nargs=1, type= str, default=sys.stdin, help = 'Dataframe with continued lockdown results.')
parser.add_argument('--early_lockdown_df', nargs=1, type= str, default=sys.stdin, help = 'Dataframe with earlier and continued lockdown results.')
parser.add_argument('--epiestim_df', nargs=1, type= str, default=sys.stdin, help = 'Dataframe with epiestim results.')
parser.add_argument('--case_df', nargs=1, type= str, default=sys.stdin, help = 'Dataframe with cases per day.')
parser.add_argument('--short_dates', nargs=1, type= str, default=sys.stdin, help = 'Short date format for plotting (csv).')
parser.add_argument('--outdir', nargs=1, type= str, default=sys.stdin, help = 'Path to outdir.')

def plot_R_posterior(data, state, outdir):
    fig, ax = plt.subplots(figsize=(3/2.54, 3/2.54))
    sns.distplot(data) #The first 2000 samplings are warmup
    ax.set_title(state)
    ax.set_xlabel('R0')
    #ax.set_xlim([1.5,5.5])
    #ax.axvline(x=2.79, ymin=0, ymax=2, linestyle='--',linewidth=1)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    fig.tight_layout()
    fig.savefig(outdir+'plots/posterior/R_'+state+'.png', format = 'png',dpi=300 )
    plt.close()

def visualize_results(complete_df, lockdown_df, early_lockdown_df, epiestim_df, indir, short_dates, outdir):
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
    #Plot alpha posteriors
    fig, ax = plt.subplots(figsize=(6/2.54, 4/2.54))
    alpha_colors = {0:'darkorange',1:'tab:purple',2:'magenta', 3:'tab:olive', 4:'tab:cyan'}
    alpha_names = {0:'retail and recreation',1:'grocery and pharmacy',2:'transit stations',3:'workplace',4:'residential'}

    for i in range(5):
        fig, ax = plt.subplots(figsize=(6/2.54, 4.5/2.54))
        alpha_red = 100*(1-np.exp(-100*alphas[2000:,i]))
        sns.distplot(alpha_red ,color=alpha_colors[i]) #The first 2000 samplings are warmup
        ax.set_title(alpha_names[i])
        ax.set_ylabel('Density')
        ax.set_xlabel("Relative % reduction in Rt")
        ax.axvline(x=np.median(alpha_red), ymin=0, ymax=20, linestyle='--',linewidth=1)
        print(alpha_names[i],np.round(np.median(alpha_red),2))
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        fig.tight_layout()
        fig.savefig(outdir+'plots/posterior/alpha_'+str(i)+'.png', format = 'png',dpi=300 )
        plt.close()


    #Plot per state
    states = complete_df['region'].unique()
    #R posteriors
    R_posteriors = np.load(indir+'mu.npy', allow_pickle=True)
    # montage_file = open(outdir+'/plots/montage.sh','w')
    # montage_file.write('montage ')
    #all death curves together
    figclose, axclose = plt.subplots(figsize=(12/2.54, 12/2.54))
    figopen, axopen = plt.subplots(figsize=(12/2.54, 12/2.54))
    #metrics
    metrics = pd.DataFrame(np.zeros((len(states),9)), columns=['state','observed deaths','mean deaths', 'lower deaths', 'higher deaths', 'mean cont. deaths', 'lower cont. deaths', 'higher cont. deaths', 'previous peak mean deaths'])
    #Save estimates
    complete_df['meanR_mobility'] = 0
    complete_df['0.025R_mobility'] = 0
    complete_df['0.975R_mobility'] = 0
    complete_df['mean_deaths_mobility'] = 0
    complete_df['mean_cases_mobility'] = 0
    for i in range(1,len(states)+1):

        state= states[i-1]
        #Plot R posterior
        plot_R_posterior(R_posteriors[2000:,i-1], state, outdir)
        #Get att data for state i
        state_data = complete_df[complete_df['region']==state]
        observed_deaths = state_data['deaths']
        days = len(state_data)#Number of days for state i
        #Lockdown data
        state_lockdown = lockdown_df[lockdown_df['state']==state]
        state_lockdown = state_lockdown.reset_index()
        #Early lockdown data
        state_early_lockdown = early_lockdown_df[early_lockdown_df['state']==state]
        state_early_lockdown = state_early_lockdown.reset_index()
        #Extract modeling results
        means = {'prediction':np.zeros((days)),'E_deaths':np.zeros((days)), 'Rt':np.zeros((days))}
        lower_bound = {'prediction':np.zeros((days)),'E_deaths':np.zeros((days)), 'Rt':np.zeros((days))} #Estimated 2.5 %
        higher_bound = {'prediction':np.zeros((days)),'E_deaths':np.zeros((days)), 'Rt':np.zeros((days))} #Estimated 97.5 % - together 95 % CI
        lower_bound25 = {'prediction':np.zeros((days)),'E_deaths':np.zeros((days)), 'Rt':np.zeros((days))} #Estimated 25%
        higher_bound75 = {'prediction':np.zeros((days)),'E_deaths':np.zeros((days)), 'Rt':np.zeros((days))} #Estimated 55 % - together 75 % CI
        #Get means and 95 % CI for cases (prediction), deaths and Rt for all time steps
        for j in range(1,days+1):
            for var in ['prediction', 'E_deaths','Rt']:
                try:
                    var_ij = summary[summary['Unnamed: 0']==var+'['+str(j)+','+str(i)+']']
                    means[var][j-1]=var_ij['mean'].values[0]
                    lower_bound[var][j-1]=var_ij['2.5%'].values[0]
                    higher_bound[var][j-1]=var_ij['97.5%'].values[0]
                    lower_bound25[var][j-1]=var_ij['25%'].values[0]
                    higher_bound75[var][j-1]=var_ij['75%'].values[0]
                except:
                    pdb.set_trace()

        #Add the R estimates to complete df
        complete_df.loc[complete_df['region']==state, 'meanR_mobility']=means['Rt']
        complete_df.loc[complete_df['region']==state, '0.025R_mobility']= lower_bound['Rt']
        complete_df.loc[complete_df['region']==state, '0.975R_mobility']= higher_bound['Rt']
        complete_df.loc[complete_df['region']==state, 'mean_deaths_mobility']=means['E_deaths']
        complete_df.loc[complete_df['region']==state, 'mean_cases_mobility']=means['prediction']

        #Plot cases
        #Per day
        plot_shade_ci(days, state_data,state_lockdown, state_early_lockdown, 'cases', means['prediction'],lower_bound['prediction'],
        higher_bound['prediction'], lower_bound25['prediction'], higher_bound75['prediction'], 'Cases per day',
        outdir+'plots/'+state+'_cases.png', short_dates)

        #Plot Deaths
        #Per day
        plot_shade_ci(days,state_data,state_lockdown, state_early_lockdown, 'deaths',means['E_deaths'], lower_bound['E_deaths'], higher_bound['E_deaths'],
        lower_bound25['E_deaths'], higher_bound75['E_deaths'], 'Deaths per day',
        outdir+'plots/'+state+'_deaths.png', short_dates)
        #Plot R
        plot_shade_ci(days,state_data,state_lockdown,state_early_lockdown, 'Rt',means['Rt'], lower_bound['Rt'], higher_bound['Rt'], lower_bound25['Rt'],
        higher_bound75['Rt'],'Rt',outdir+'plots/'+state+'_Rt.png', short_dates)

        #Save deaths at end point vs deaths at end point if continued lockdown
        metrics.loc[i-1,'state']=state
        metrics.loc[i-1,'observed deaths']=np.round(np.array(state_data['deaths'])[-1],0)
        metrics.loc[i-1,'mean deaths']=np.round(means['E_deaths'][-1],0)
        metrics.loc[i-1,'lower deaths']=np.round(lower_bound['E_deaths'][-1],0)
        metrics.loc[i-1,'higher deaths']=np.round(higher_bound['E_deaths'][-1],0)
        metrics.loc[i-1,'mean cont. deaths']=np.round(np.array(state_lockdown['mean_deaths'])[-1],0)
        metrics.loc[i-1,'lower cont. deaths']=np.round(np.array(state_lockdown['lower_deaths'])[-1],0)
        metrics.loc[i-1,'higher cont. deaths']=np.round(np.array(state_lockdown['higher_deaths'])[-1],0)
        metrics.loc[i-1,'previous peak mean deaths']=np.round(max(means['E_deaths'][:-30]),0)

    metrics.to_csv(outdir+'metrics.csv')
    return metrics, complete_df

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

def plot_shade_ci(days, state_data, state_lockdown, state_early_lockdown, param, means, lower_bound, higher_bound, lower_bound25, higher_bound75, ylabel, outname, short_dates):
    '''Plot with shaded 95 % CI (plots both 1 and 2 std, where 2 = 95 % interval)
    '''
    dates = state_data['date']
    pdb.set_trace()
    selected_short_dates = np.array(short_dates[short_dates['np_date'].isin(dates)]['short_date']) #Get short version of dates
    x = np.arange(days)#x-vals
    if len(dates) != len(selected_short_dates):
        pdb.set_trace()
    fig, ax1 = plt.subplots(figsize=(6/2.54, 4.5/2.54))

    #Plot observed dates
    if param=='deaths':
        ax1.bar(x,np.round(state_data[param],0), alpha = 0.5)


    #Plot continued lockdown
    exi = int(state_lockdown['extreme_index'].values[0])
    try:
        ax1.plot(x[exi:],state_lockdown.loc[exi:,'mean_'+param], alpha=0.5, linewidth = 2.0, color = 'g')
    except:
        pdb.set_trace()
    ax1.fill_between(x[exi:],state_lockdown.loc[exi:,'lower_'+param], state_lockdown.loc[exi:,'higher_'+param], color='seagreen', alpha=0.4)
    ax1.fill_between(x[exi:],state_lockdown.loc[exi:,'lower25_'+param], state_lockdown.loc[exi:,'higher75_'+param], color='seagreen', alpha=0.6)

    # #Plot earlier continued lockdown
    # exi = int(state_early_lockdown['extreme_index'].values[0])
    # try:
    #     ax1.plot(x,state_early_lockdown.loc[:,'mean_'+param], alpha=0.5, linewidth = 2.0, color = 'grey')
    # except:
    #     pdb.set_trace()
    # ax1.fill_between(x,state_early_lockdown.loc[:,'lower_'+param], state_early_lockdown.loc[:,'higher_'+param], color='grey', alpha=0.4)
    # ax1.fill_between(x,state_early_lockdown.loc[:,'lower25_'+param], state_early_lockdown.loc[:,'higher75_'+param], color='grey', alpha=0.6)

    #Plot simulation
    ax1.plot(x,means, alpha=0.5, linewidth = 2.0, color = 'b')
    ax1.fill_between(x, lower_bound, higher_bound, color='cornflowerblue', alpha=0.4)
    ax1.fill_between(x, lower_bound25, higher_bound75, color='cornflowerblue', alpha=0.6)

    #Mobility
    mob_keys = {'retail_and_recreation_percent_change_from_baseline':'darkorange',
                'grocery_and_pharmacy_percent_change_from_baseline':'tab:purple',
                'transit_stations_percent_change_from_baseline':'magenta',
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
    #Close plot
    plt.close(fig)

def plot_markers():
    '''Plot the marker explanations
    '''
    #Mobility
    covariate_colors = {'retail and recreation':'darkorange','grocery and pharmacy':'tab:purple', 'transit stations':'magenta','workplace':'tab:olive','residential':'tab:cyan'}
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
    mob_keys = {'retail_and_recreation_percent_change_from_baseline':'darkorange',
                'grocery_and_pharmacy_percent_change_from_baseline':'tab:purple',
                'transit_stations_percent_change_from_baseline':'magenta',
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
            xticks=[ 0, 14, 28, 42, 56, 70, 84, 98,112, 126, 140, 154, 168, 184]
            dates = dates[xticks]
            selected_short_dates = np.array(short_dates[short_dates['np_date'].isin(dates)]['short_date']) #Get short version of dates
            ax.set_xticks(dates)
            ax.set_xticklabels(selected_short_dates,rotation='vertical')
            #plt.xticks(rotation='vertical')
            #Hide
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            fig.tight_layout()
            if plot_lockdown == True:
                fig.savefig(outdir+str(i)+'_extreme.png', format = 'png')
            else:
                fig.savefig(outdir+str(i)+'.png', format = 'png')
            i+=1
            plt.close()

def print_CI(metrics):
    '''Print table of mean and 95 % CIs for % of previous peak at end for
    NPI continuation vs reality
    '''
    print('State;Modeled deaths with NPI lifting;Fraction of previous peak with NPI lifting;Modeled deaths with continued NPIs;Fraction of previous peak with continued NPIs')
    for i in range(len(metrics)):
        row_i = metrics.loc[i]
        #Opening
        php_open_mean = str(np.round(100*row_i['mean deaths']/row_i['previous peak mean deaths'],1))
        php_open_lower = str(np.round(100*row_i['lower deaths']/row_i['previous peak mean deaths'],1))
        php_open_higher = str(np.round(100*row_i['higher deaths']/row_i['previous peak mean deaths'],1))
        #Continued lockdown
        php_cl_mean = str(np.round(100*row_i['mean cont. deaths']/row_i['previous peak mean deaths'],1))
        php_cl_lower = str(np.round(100*row_i['lower cont. deaths']/row_i['previous peak mean deaths'],1))
        php_cl_higher = str(np.round(100*row_i['higher cont. deaths']/row_i['previous peak mean deaths'],1))

        print(row_i['state']+';'+str(row_i['mean deaths'])+' ['+str(row_i['lower deaths'])+','+str(row_i['higher deaths'])+']'+';'+php_open_mean+' % ['+php_open_lower+','+php_open_higher+'];'+str(row_i['mean cont. deaths'])+' ['+str(row_i['lower cont. deaths'])+','+str(row_i['higher cont. deaths'])+']'+';'+php_cl_mean+' % ['+php_cl_lower+','+php_cl_higher+']')

def plot_R_comparison(state_data, short_dates, state, outdir):
    '''Plot the coparison btw R estimates of the obility model and EpiEstim
    '''

    #Compare R from the mobility model and EpiEstim
    fig, ax = plt.subplots(figsize=(4.5/2.54, 4.5/2.54))
    ax.plot(np.arange(len(state_data)),state_data['Mean(R)'],color='b',label='EpiEstim')
    ax.fill_between(np.arange(len(state_data)),state_data['Quantile.0.025(R)'], state_data['Quantile.0.975(R)'], color='cornflowerblue', alpha=0.4)
    #Mobility R
    ax.plot(np.arange(len(state_data)),state_data['meanR_mobility'],color='g',label='Mobility')
    ax.fill_between(np.arange(len(state_data)),state_data['0.025R_mobility'], state_data['0.975R_mobility'], color='forestgreen', alpha=0.4)
    #Correlation
    R,p = pearsonr(state_data['Mean(R)'],state_data['meanR_mobility'])
    #error
    er = np.average(np.absolute(np.array(state_data['Mean(R)']-state_data['meanR_mobility'])))
    ax.set_title(state+'\nPCC='+str(np.round(R,2))+'\nav.error='+str(np.round(er,2)))
    ax.set_ylabel('Rt')
    selected_short_dates = np.array(short_dates[short_dates['np_date'].isin(np.array(state_data['date']))]['short_date'])
    xticks=np.arange(len(selected_short_dates)-1,0,-14)
    ax.set_xticks(xticks)
    ax.set_xticklabels(selected_short_dates[xticks],rotation='vertical')
    plt.legend()
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    fig.tight_layout()
    fig.savefig(outdir+'/plots/R_comparison/'+state+'.png', format = 'png', dpi=300)
    plt.close()
    print(state,',', max(state_data['meanR_mobility']),',',max(state_data['Mean(R)']),',',min(state_data['meanR_mobility']),',',min(state_data['Mean(R)']))
    return None

def epiestim_vs_mob(complete_df, epiestim_df, case_df, short_dates):
    '''Analyze the relationship btw mobility change and R change
    '''
    matplotlib.rcParams.update({'font.size': 6})
    #Plot per state
    states = complete_df['region'].unique()

    mob_keys = {'retail_and_recreation_percent_change_from_baseline':'Reds',
                'grocery_and_pharmacy_percent_change_from_baseline':'Purples',
                'transit_stations_percent_change_from_baseline':'spring_r',
                'workplaces_percent_change_from_baseline':'YlGn',
                'residential_percent_change_from_baseline':'Blues',
                }

    xlims = {'retail_and_recreation_percent_change_from_baseline':[-60,-30],
                'grocery_and_pharmacy_percent_change_from_baseline':[-30,10],
                'transit_stations_percent_change_from_baseline':[-70,-30],
                'workplaces_percent_change_from_baseline':[-60,-30],
                'residential_percent_change_from_baseline':[10,20]}
    titles =  {1:'Retail & recreation',2:'Grocery & pharmacy', 3:'Transit stations',4:'Workplace',5:'Residential',6:'Parks'}
    i=0
    for key in mob_keys:
        all_x = []
        all_y = []
        close_x = []
        open_x = []
        close_y = []
        open_y = []

        figR, axR = plt.subplots(figsize=(12/2.54, 12/2.54))
        for state in states:
            if state == 'District of Columbia':
                continue
            state_data = complete_df[complete_df['region']==state]
            #Compare with the epiestim df
            #epiestim_state = epiestim_df[epiestim_df['country']=='US-'+state.replace(" ", "_")]
            epiestim_state = epiestim_df[epiestim_df['state']==state]
            #Cases per state
            case_state = case_df[case_df['region']==state]
            #Join on date
            state_data = state_data.merge(epiestim_state, left_on='date', right_on='date', how = 'left')
            state_data = state_data.merge(case_state, left_on='date', right_on='date', how = 'left')

            state_data = state_data[state_data['Median(R)']<6] #'Median(R)'
            #Plot R from epiestim vs the R from the mobility model
            plot_R_comparison(state_data,  short_dates, state, outdir)

            #Plot R from EpiEstim
            axR.plot(state_data['date'], state_data['Median(R)'], color = 'b', alpha = 0.5)
            state_data = state_data[state_data['date']<'2020-06-06']

            #Get cases last week and normalize with total
            cases_last_week = np.zeros(len(state_data))
            for j in range(7,len(state_data)):
                state_total_cases = np.sum(state_data.loc[:j-1,'cases'])
                if state_total_cases == 0:
                    cases_last_week[j-1]=0
                else:
                    cases_last_week[j-1]=np.sum(state_data.loc[j-7:j-1,'cases'])/state_total_cases


            state_data['cases_last_week']=cases_last_week
            close_data = state_data[state_data['date']<'2020-04-25']
            open_data = state_data[state_data['date']>='2020-04-25']



            #Get all data together
            all_x.extend(np.array(state_data[key]))
            all_y.extend(np.array(state_data['Median(R)']))
            #Get close and open data
            close_x.extend(np.array(close_data[key]))
            close_y.extend(np.array(close_data['Median(R)']))
            #close_y.extend(np.array(close_data['cases'])/max(state_data['cases']))
            #close_y.extend(np.gradient(np.array(close_data['cases'])/max(state_data['cases'])))
            #close_y.extend(np.array(close_data['cases_last_week']))
            open_x.extend(np.array(open_data[key]))
            open_y.extend(np.array(open_data['Median(R)']))
            #open_y.extend(np.array(open_data['cases'])/max(state_data['cases']))
            #open_y.extend(np.gradient(np.array(open_data['cases'])/max(state_data['cases'])))
            #open_y.extend(np.array(open_data['cases_last_week']))

        #Plot formatting
        #EpiEstim R
        #Dates
        start = min(complete_df['date'])
        end = max(complete_df['date'])
        dates=np.arange(start,end+datetime.timedelta(days=1), dtype='datetime64[D]')
        xticks=[ 0, 14, 28, 42, 56, 70, 84, 98,112, 126, 140, 154, 168, 184]
        dates = dates[xticks]
        selected_short_dates = np.array(short_dates[short_dates['np_date'].isin(dates)]['short_date']) #Get short version of dates
        axR.set_xticks(dates)
        axR.set_xticklabels(selected_short_dates,rotation='vertical')
        axR.set_ylabel('EpiEstim R')
        #Hide
        axR.spines['top'].set_visible(False)
        axR.spines['right'].set_visible(False)
        figR.tight_layout()
        figR.savefig(outdir+'epiR.png', format = 'png')
        i+=1


        #Close and Open
        def get_average(x,y,s):
            '''Computes the average relationship
            btw x and y with intervals of s
            '''
            xmin = min(x) #x is the mobility data
            xmax = max(x) #and will be used for the intervals
            xav = [] #Save averages
            yav = []
            vals = np.arange(xmax, xmin-s,-s)
            for i in range(len(vals)-1):
                int_x = np.where((x<=vals[i]) & (x>vals[i+1]))
                xav.append(np.median(x[int_x]))
                yav.append(np.median(y[int_x]))

            return xav, yav

        figall, axall = plt.subplots(figsize=(3.6/2.54, 3.6/2.54))
        all_R=np.round(np.corrcoef(all_x,all_y)[0,1],2)
        xav, yav = get_average(np.array(all_x), np.array(all_y), 5)
        sns.kdeplot(all_x,all_y, cmap=mob_keys[key])
        axall.plot(xav,yav,color='grey', linewidth=1)
        axall.set_xlabel('Mobility change')
        axall.set_ylabel('EpiEstim R')
        axall.set_title(titles[i]+'\nR='+str(np.average(all_R)))
        axall.set_yticks([1,2,3,4,5,6])
        axall.set_ylim([0.5,6])
        #Hide
        axall.spines['top'].set_visible(False)
        axall.spines['right'].set_visible(False)
        if key != 'residential_percent_change_from_baseline':
            axall.invert_xaxis() #Invert axis
        figall.tight_layout()
        figall.savefig(outdir+key+'_all_curves.png', format = 'png')

        #Close
        figclose, axclose = plt.subplots(figsize=(3.6/2.54, 3.6/2.54))
        close_R=np.round(np.corrcoef(close_x,close_y)[0,1],2)
        xav, yav = get_average(np.array(close_x), np.array(close_y), 5)
        sns.kdeplot(close_x,close_y, cmap=mob_keys[key])
        axclose.plot(xav,yav,color='grey', linewidth=1)
        axclose.set_xlabel('Mobility change')
        axclose.set_ylabel('EpiEstim R')
        axclose.set_title(titles[i]+'\nPCC='+str(np.average(close_R)))
        axclose.set_yticks([1,2,3,4,5,6])
        axclose.set_ylim([0.5,6])
        #Hide
        axclose.spines['top'].set_visible(False)
        axclose.spines['right'].set_visible(False)
        if key != 'residential_percent_change_from_baseline':
            axclose.invert_xaxis() #Invert axis
        figclose.tight_layout()
        figclose.savefig(outdir+key+'_all_close_curves.png', format = 'png')

        #Open
        figopen, axopen = plt.subplots(figsize=(3.6/2.54, 3.6/2.54))
        xav, yav = get_average(np.array(open_x), np.array(open_y), 5)
        sns.kdeplot(open_x,open_y, cmap=mob_keys[key])
        axopen.plot(xav,yav,color='grey', linewidth=1)
        axopen.set_xlabel('Mobility change')
        axopen.set_ylabel('EpiEstim R')
        open_R=np.round(np.corrcoef(open_x,open_y)[0,1],2)
        axopen.set_title(titles[i]+'\nPCC='+str(np.average(open_R)))
        axopen.set_ylim([0.5,1.5])
        axopen.set_yticks([0.5,1,1.5])
        #Hide
        axopen.spines['top'].set_visible(False)
        axopen.spines['right'].set_visible(False)
        if key == 'residential_percent_change_from_baseline':
            axopen.invert_xaxis() #Invert axis
        figopen.tight_layout()
        figopen.savefig(outdir+key+'_all_open_curves.png', format = 'png')



#####MAIN#####
#Set font size
matplotlib.rcParams.update({'font.size': 7})
args = parser.parse_args()
indir = args.indir[0]
complete_df = pd.read_csv(args.complete_df[0])
epiestim_df = pd.read_csv(args.epiestim_df[0])
case_df = pd.read_csv(args.case_df[0])
#Convert to datetime
complete_df['date']=pd.to_datetime(complete_df['date'], format='%Y/%m/%d')
epiestim_df['date']=pd.to_datetime(epiestim_df['date'], format='%Y/%m/%d')
case_df['date']=pd.to_datetime(case_df['date'], format='%Y/%m/%d')
lockdown_df = pd.read_csv(args.lockdown_df[0])
early_lockdown_df = pd.read_csv(args.early_lockdown_df[0])
short_dates = pd.read_csv(args.short_dates[0])

#Make sure the np dates are in the correct format
short_dates['np_date'] = pd.to_datetime(short_dates['np_date'], format='%Y/%m/%d')
outdir = args.outdir[0]
#Visualize the mobility data
#visualize_mobility(complete_df, lockdown_df, short_dates, outdir)
#Plot the markers
#plot_markers()
#Visualize
metrics, complete_df = visualize_results(complete_df, lockdown_df, early_lockdown_df, epiestim_df, indir, short_dates, outdir)
#Save df
complete_df.to_csv('../modeling_results/complete_df.csv')
#Print metrics as table with CIs
print_CI(metrics)
#Analyze mobility and R relstionhip
epiestim_vs_mob(complete_df, epiestim_df, case_df, short_dates)
