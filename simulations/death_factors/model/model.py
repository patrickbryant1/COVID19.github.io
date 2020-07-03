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
import pdb

from scipy.stats import pearsonr
from sklearn.linear_model import ElasticNet, LinearRegression, Ridge, Lars, Lasso, BayesianRidge, ARDRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import KFold


#Arguments for argparse module:
parser = argparse.ArgumentParser(description = '''Analyze the effect of population differences on county death tolls using an elastic net regression model. ''')
parser.add_argument('--data', nargs=1, type= str, default=sys.stdin, help = 'Path to all formatted data per county).')
parser.add_argument('--sig_feature_corr', nargs=1, type= str, default=sys.stdin, help = 'Path to significant features.')
parser.add_argument('--outdir', nargs=1, type= str, default=sys.stdin, help = 'Path to outdir.')

def visualize_output(cols,coefs,outdir,id):
    '''Plot coef vals
    '''

    coef_df = pd.DataFrame()
    coef_df['Feature'] = cols
    coef_df['Coefficient'] = np.array(coefs)
    coef_df=coef_df.sort_values(by='Coefficient',ascending=False)

    fig, ax = plt.subplots(figsize=(18/2.54,100/2.54))
    sns.barplot(x="Coefficient", y="Feature", data=coef_df)
    #ax.set_ylim([min(coefs),max(coefs)])
    fig.tight_layout()
    fig.show()
    fig.savefig(outdir+id+'_all_enet_coefs.png', format='png')
    plt.close()

    #Plot top 10 coefs
    coef_df = coef_df.reset_index()
    top10 = coef_df.loc[0:9]
    bottom10 = coef_df.loc[len(coef_df)-10:len(coef_df)]
    if id == 'RandomForestRegressor':
        bottom10 = coef_df.loc[10:19]
    top_bottom = pd.concat([top10,bottom10])
    fig, ax = plt.subplots(figsize=(18/2.54,18/2.54))
    sns.barplot(x="Coefficient", y="Feature", data=top_bottom)
    ax.set_title(id)
    fig.tight_layout()
    fig.savefig(outdir+id+'_top_bottom10_enet_coefs.png', format='png')
    plt.close()

def fit_enet(X_train, X_test,y_train, y_test,cols,split,metrics,outdir):
    '''Fit an enet model to data
    '''
    alpha = [0.8,1.0]
    l1_ratio = [0.25,0.5,0.75]
    tol = [0.001,0.0001]
    for a in alpha:
        for l1 in l1_ratio:
            for t in tol:
                #Fit
                regr = ElasticNet(random_state=0,alpha=a, l1_ratio=l1, fit_intercept=True,
                normalize=False, precompute=False, max_iter=1000, copy_X=True, tol=t,
                warm_start=True, positive=False, selection='cyclic')

                regr.fit(X_train,y_train)
                #visualize_output(cols, regr.coef_ ,outdir,'ElasticNet_'+str(split))
                #Predict
                pred = regr.predict(X_test)
                err=np.average(np.absolute(pred-y_test))
                R,p=pearsonr(pred,y_test)
                #Save metrics
                metrics['alpha'].append(a)
                metrics['l1_ratio'].append(l1)
                metrics['tol'].append(t)
                metrics['Average error'].append(np.round(err,2))
                metrics['Pearson R'].append(np.round(R,2))

    return metrics

def rf_reg(X_train, X_test,y_train, y_test,cols,split,metrics,outdir):
    '''Fit a RandomForestRegressor
    '''
    n_estimators = [50,100,200]
    min_samples_split = [2,5]
    min_samples_leaf = [1,2]
    for ne in n_estimators:
        for mss in min_samples_split:
            for msl in min_samples_leaf:
                #Fit with params
                regr = RandomForestRegressor(n_estimators=ne, criterion='mse', max_depth=None, min_samples_split=mss,
                min_samples_leaf=msl, min_weight_fraction_leaf=0.0, max_features='auto', max_leaf_nodes=None,
                min_impurity_decrease=0.0, min_impurity_split=None, bootstrap=True, oob_score=False, n_jobs=-1,
                random_state=None, verbose=0, warm_start=True, ccp_alpha=0.0, max_samples=None)

                regr.fit(X_train,y_train)
                #visualize_output(cols, regr.feature_importances_ ,outdir,'RandomForestRegressor_'+str(split))
                #Predict
                pred = regr.predict(X_test)
                err=np.average(np.absolute(pred-y_test))
                R,p=pearsonr(pred,y_test)
                #Save metrics
                metrics['n_estimators'].append(ne)
                metrics['min_samples_split'].append(mss)
                metrics['min_samples_leaf'].append(msl)
                metrics['Average error'].append(np.round(err,2))
                metrics['Pearson R'].append(np.round(R,2))
    return metrics


def vis_enet_opt(df, outdir):
    '''Visualize the optimization
    '''

    fig, ax1 = plt.subplots(figsize=(18/2.54,9/2.54))
    ax2 = ax1.twinx()
    alpha = df['alpha'].unique()
    l1 = df['l1_ratio'].unique()
    tol = df['tol'].unique()
    xticks = ['alpha:\nl1_ratio:\ntol:']
    combo = 1
    for a in alpha:
        a_df = df[df['alpha']==a]
        for l in l1:
            a_l_df = a_df[a_df['l1_ratio']==l]
            for t in tol:
                a_l_t_df = a_l_df[a_l_df['tol']==t]
                #Pearson R
                ax1.errorbar(combo,np.average(a_l_t_df['Pearson R']), yerr=np.std(a_l_t_df['Pearson R']),color='cornflowerblue')
                ax1.scatter(combo,np.average(a_l_t_df['Pearson R']),color='b',marker='x')
                #Average error
                ax2.errorbar(combo+0.2,np.average(a_l_t_df['Average error']),yerr=np.std(a_l_t_df['Average error']), color='mediumseagreen')
                ax2.scatter(combo+0.2,np.average(a_l_t_df['Average error']), color='g',marker='x')
                xticks.append(str(a)+'\n'+str(l)+'\n'+str(t))
                combo+=1

    ax1.set_ylabel('Pearson R',color='b')
    ax1.set_ylim([0.4,0.7])
    ax2.set_ylabel('Average error',color='g')
    ax2.set_ylim([14,19])
    ax1.set_xticks(np.arange(0,13))
    ax2.set_xticks(np.arange(0,13))
    ax1.set_xticklabels(xticks)
    plt.title('Elastic Net Regression')
    fig.tight_layout()
    #Hide axis and set colors
    ax1.spines['top'].set_visible(False)
    ax2.spines['top'].set_visible(False)
    ax2.spines['bottom'].set_color('grey')
    ax2.spines['left'].set_color('blue')
    ax1.spines['right'].set_color('green')
    ax2.spines['right'].set_color('green')
    for t in ax2.xaxis.get_ticklines(): t.set_color('grey')
    for t in ax2.yaxis.get_ticklines(): t.set_color('grey')
    fig.savefig(outdir+'enet_opt.png', format='png')
    plt.close()

def vis_rf_opt(df, outdir):
    '''Visualize the optimization
    '''

    fig, ax1 = plt.subplots(figsize=(18/2.54,9/2.54))
    ax2 = ax1.twinx()
    n_est= df['n_estimators'].unique()
    mss = df['min_samples_split'].unique()
    msl = df['min_samples_leaf'].unique()
    xticks = ['n_est:\nmin_split:\nmin_leaf:']
    combo = 1
    for n in n_est:
        n_df = df[df['n_estimators']==n]
        for m in mss:
            n_m_df = n_df[n_df['min_samples_split']==m]
            for ml in msl:
                n_m_ml_df = n_m_df[n_m_df['min_samples_leaf']==ml]
                #Pearson R
                ax1.errorbar(combo,np.average(n_m_ml_df['Pearson R']), yerr=np.std(n_m_ml_df['Pearson R']),color='cornflowerblue')
                ax1.scatter(combo,np.average(n_m_ml_df['Pearson R']),color='b',marker='x')
                #Average error
                ax2.errorbar(combo+0.2,np.average(n_m_ml_df['Average error']),yerr=np.std(n_m_ml_df['Average error']), color='mediumseagreen')
                ax2.scatter(combo+0.2,np.average(n_m_ml_df['Average error']), color='g',marker='x')
                xticks.append(str(n)+'\n'+str(m)+'\n'+str(ml))
                combo+=1

    ax1.set_ylabel('Pearson R',color='b')
    ax1.set_ylim([0.4,0.7])
    ax2.set_ylabel('Average error',color='g')
    ax2.set_ylim([14,19])
    ax1.set_xticks(np.arange(0,13))
    ax2.set_xticks(np.arange(0,13))
    ax1.set_xticklabels(xticks)
    plt.title('Random Forest Regression')
    fig.tight_layout()
    #Hide axis and set colors
    ax1.spines['top'].set_visible(False)
    ax2.spines['top'].set_visible(False)
    ax2.spines['bottom'].set_color('grey')
    ax2.spines['left'].set_color('blue')
    ax1.spines['right'].set_color('green')
    ax2.spines['right'].set_color('green')
    for t in ax2.xaxis.get_ticklines(): t.set_color('grey')
    for t in ax2.yaxis.get_ticklines(): t.set_color('grey')
    fig.savefig(outdir+'rf_opt.png', format='png')
    plt.close()

#####MAIN#####
matplotlib.rcParams.update({'font.size': 7})
args = parser.parse_args()
data = pd.read_csv(args.data[0])
print('Before NaN removal', len(data))
#Remove NaNs
data = data.dropna()
print('After NaN removal', len(data))
sig_feature_corr = pd.read_csv(args.sig_feature_corr[0])
outdir = args.outdir[0]
X = np.array(data[sig_feature_corr['Feature']])
y = np.array(data['Death rate per individual'])*100000
cols=np.array(sig_feature_corr['Feature'])
try:
    enet_df = pd.read_csv('enet_df.csv')
    rf_df = pd.read_csv('rf_df.csv')
except:
    #Cross validation
    kf = KFold(n_splits=5,random_state=42, shuffle=True)
    enet_metrics = {'alpha':[],'l1_ratio':[],'tol':[],'Average error':[],'Pearson R':[]}
    rf_metrics = {'n_estimators':[],'min_samples_split':[],'min_samples_leaf':[],'Average error':[],'Pearson R':[]}
    i=1
    for train_index, test_index in kf.split(X):
        X_train, X_test = X[train_index], X[test_index]
        y_train, y_test = y[train_index], y[test_index]
        enet_metrics = fit_enet(X_train, X_test,y_train, y_test,cols,i,enet_metrics,outdir)
        rf_metrics = rf_reg(X_train, X_test,y_train, y_test,cols,i,rf_metrics,outdir)
        i+=1

    #Construct metric dfs
    enet_df = pd.DataFrame()
    for key in enet_metrics:
        enet_df[key]=enet_metrics[key]
    enet_df.to_csv('enet_df.csv')
    rf_df = pd.DataFrame()
    for key in rf_metrics:
        rf_df[key]=rf_metrics[key]
    rf_df.to_csv('rf_df.csv')

#Visualize
#vis_enet_opt(enet_df, outdir)
vis_rf_opt(rf_df, outdir)
