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
    #Fit
    regr = ElasticNet(random_state=0,alpha=1.0, l1_ratio=0.5, fit_intercept=True,
    normalize=False, precompute=False, max_iter=1000, copy_X=True, tol=0.001,
    warm_start=True, positive=False, selection='cyclic')
    regr.fit(X_train,y_train)
    visualize_output(cols, regr.coef_ ,outdir,'ElasticNet_'+str(split))
    pred = regr.predict(X_test)
    err=np.average(np.absolute(pred-y_test))
    R,p=pearsonr(pred,y_test)
    fig, ax = plt.subplots(figsize=(6/2.54,6/2.54))
    plt.scatter(y_test,pred,s=2)
    plt.title('ElasticNet\nR='+str(np.round(R,2))+'|av.err.='+str(np.round(err,2)))
    ax.set_xlabel('True')
    ax.set_ylabel('Predicted')
    fig.tight_layout()
    fig.savefig(outdir+str(split)+'_enet_pred_vs_true_per100000.png', format='png')

    metrics['Model'].append('ElasticNet')
    metrics['Average error'].append(np.round(err,2))
    metrics['Pearson R'].append(np.round(R,2))
    return metrics

def rf_reg(X_train, X_test,y_train, y_test,cols,split,metrics,outdir):
    '''Fit a RandomForestRegressor
    '''
    regr = RandomForestRegressor(max_depth=2, random_state=0)
    regr.fit(X_train,y_train)
    visualize_output(cols, regr.feature_importances_ ,outdir,'RandomForestRegressor_'+str(split))
    pred = regr.predict(X_test)
    err=np.average(np.absolute(pred-y_test))
    R,p=pearsonr(pred,y_test)
    fig, ax = plt.subplots(figsize=(9/2.54,9/2.54))
    plt.scatter(y_test,pred,s=2)
    plt.title('RandomForestRegressor\nR='+str(np.round(R,2))+'|av.err.='+str(np.round(err,2)))
    ax.set_xlabel('True')
    ax.set_ylabel('Predicted')
    fig.tight_layout()
    fig.savefig(outdir+str(split)+'rf_pred_vs_true_per100000.png', format='png')

    metrics['Model'].append('RandomForestRegressor')
    metrics['Average error'].append(np.round(err,2))
    metrics['Pearson R'].append(np.round(R,2))

    return metrics
    
def fit_lreg(X,y,cols,outdir,id):
    '''Fit an enet model to data
    '''
    #Fit
    regr = LinearRegression()
    regr.fit(X,y)
    visualize_output(cols, regr.coef_ ,outdir,'LinearRegression')
    pred = regr.predict(X)
    err=np.average(np.absolute(pred-y))
    print('Average error:',np.round(err,2))
    R,p=pearsonr(pred,y)
    print('Pearson R:',np.round(R,2))
    fig, ax = plt.subplots(figsize=(9/2.54,9/2.54))
    plt.scatter(y,pred,s=2)
    plt.title('LinearRegression\nR='+str(np.round(R,2))+'|av.err.='+str(np.round(err,2)))
    ax.set_xlabel('True')
    ax.set_ylabel('Predicted')
    fig.tight_layout()
    fig.savefig(outdir+'lreg_pred_vs_true_per100000.png', format='png')


def fit_ridge(X,y,cols,outdir,id):
    '''Fit an enet model to data
    '''
    #Fit
    regr = Ridge()
    regr.fit(X,y)
    visualize_output(cols, regr.coef_ ,outdir,'RidgeRegression')
    pred = regr.predict(X)
    err=np.average(np.absolute(pred-y))
    print('Average error:',np.round(err,2))
    R,p=pearsonr(pred,y)
    print('Pearson R:',np.round(R,2))
    fig, ax = plt.subplots(figsize=(9/2.54,9/2.54))
    plt.scatter(y,pred,s=2)
    plt.title('RidgeRegression\n|R='+str(np.round(R,2))+'|av.err.='+str(np.round(err,2)))
    ax.set_xlabel('True')
    ax.set_ylabel('Predicted')
    fig.tight_layout()
    fig.savefig(outdir+'ridge_pred_vs_true_per100000.png', format='png')

def fit_lasso(X,y,cols,outdir,id):
    '''Fit an enet model to data
    '''
    #Fit
    regr = Lasso()
    regr.fit(X,y)
    visualize_output(cols, regr.coef_ ,outdir,'LassoRegression')
    pred = regr.predict(X)
    err=np.average(np.absolute(pred-y))
    print('Average error:',np.round(err,2))
    R,p=pearsonr(pred,y)
    print('Pearson R:',np.round(R,2))
    fig, ax = plt.subplots(figsize=(9/2.54,9/2.54))
    plt.scatter(y,pred,s=2)
    plt.title('LassoRegression\n|R='+str(np.round(R,2))+'|av.err.='+str(np.round(err,2)))
    ax.set_xlabel('True')
    ax.set_ylabel('Predicted')
    fig.tight_layout()
    fig.savefig(outdir+'lasso_pred_vs_true_per100000.png', format='png')

def fit_BayesianRidge(X,y,cols,outdir,id):
    '''Fit an enet model to data
    '''
    #Fit
    regr = BayesianRidge()
    regr.fit(X,y)
    visualize_output(cols, regr.coef_ ,outdir,'BayesianRidge')
    pred = regr.predict(X)
    err=np.average(np.absolute(pred-y))
    print('Average error:',np.round(err,2))
    R,p=pearsonr(pred,y)
    print('Pearson R:',np.round(R,2))
    fig, ax = plt.subplots(figsize=(9/2.54,9/2.54))
    plt.scatter(y,pred,s=2)
    plt.title('BayesianRidge\nR='+str(np.round(R,2))+'|av.err.='+str(np.round(err,2)))
    ax.set_xlabel('True')
    ax.set_ylabel('Predicted')
    fig.tight_layout()
    fig.savefig(outdir+'BayesianRidge_pred_vs_true_per100000.png', format='png')


#####MAIN#####
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
#Cross validation
kf = KFold(n_splits=5,random_state=42, shuffle=True)
metrics = {'Model':[],'Average error':[],'Pearson R':[]}
i=1
for train_index, test_index in kf.split(X):
    X_train, X_test = X[train_index], X[test_index]
    y_train, y_test = y[train_index], y[test_index]
    metrics = fit_enet(X_train, X_test,y_train, y_test,cols,i,metrics,outdir)
    # fit_lreg(X,y,cols,outdir,'Lreg')
    # fit_ridge(X,y,cols,outdir,'Ridge')
    # fit_lasso(X,y,cols,outdir,'Lasso')
    # fit_BayesianRidge(X,y,cols,outdir,'BayesianRidge')
    metrics = rf_reg(X_train, X_test,y_train, y_test,cols,i,metrics,outdir)
    i+=1
pdb.set_trace()
