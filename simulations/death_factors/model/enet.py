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
from sklearn.linear_model import ElasticNet



#Arguments for argparse module:
parser = argparse.ArgumentParser(description = '''Analyze the effect of population differences on county death tolls using an elastic net regression model. ''')
parser.add_argument('--data', nargs=1, type= str, default=sys.stdin, help = 'Path to all formatted data per county).')
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
    top_bottom = pd.concat([top10,bottom10])
    fig, ax = plt.subplots(figsize=(18/2.54,18/2.54))
    sns.barplot(x="Coefficient", y="Feature", data=top_bottom)
    fig.tight_layout()
    fig.savefig(outdir+id+'_top_bottom10_enet_coefs.png', format='png')
    plt.close()



def fit_model(data,outdir):
    '''Fit model to data
    '''
    #Select data where the Death rate per individual is at least x
    #data = data[data['Death rate per individual']>x]
    y1 = np.array(data['Death rate per individual'])*100000
    y2 = np.array(data['Cumulative deaths'])
    data = data.drop(['Death rate per individual','Cumulative deaths'],axis=1)
    X = np.array(data[data.columns[4:]])
    #Fit 1
    regr1 = ElasticNet(random_state=0,alpha=1.0, l1_ratio=0.5, fit_intercept=True,
    normalize=False, precompute=False, max_iter=1000, copy_X=True, tol=0.001,
    warm_start=True, positive=False, selection='cyclic')
    regr1.fit(X,y1)
    visualize_output(data.columns[4:], regr1.coef_ ,outdir,'per100000')
    pred = regr1.predict(X)
    err=np.average(np.absolute(pred-y1))
    print('Average error:',np.round(err,2))
    R,p=pearsonr(pred,y1)
    print('Pearson R:',np.round(R,2))
    fig, ax = plt.subplots(figsize=(9/2.54,9/2.54))
    plt.scatter(y1,pred,s=2)
    plt.title('R='+str(np.round(R,2))+'|av.err.='+str(np.round(err,2)))
    ax.set_xlabel('True')
    ax.set_ylabel('Predicted')
    fig.tight_layout()
    fig.savefig(outdir+'pred_vs_true_per100000.png', format='png')

    #Fit 2
    regr2 = ElasticNet(random_state=0)
    regr2.fit(X,y2)
    visualize_output(data.columns[4:], regr2.coef_ ,outdir,'cum_deaths')
    pred = regr2.predict(X)
    R,p=pearsonr(pred,y2)
    err = np.average(np.absolute(pred-y2))
    print('Average error:',np.round(err,2))
    print('Pearson R:',np.round(R,2))
    fig, ax = plt.subplots(figsize=(9/2.54,9/2.54))
    plt.scatter(y2,pred,s=2)
    plt.title('R='+str(np.round(R,2))+'|av.err.='+str(np.round(err,2)))
    ax.set_xlabel('True')
    ax.set_ylabel('Predicted')
    fig.tight_layout()
    fig.savefig(outdir+'pred_vs_true_cum_deaths.png', format='png')

#####MAIN#####
args = parser.parse_args()
data = pd.read_csv(args.data[0])
print('Before NaN removal', len(data))
#Remove NaNs
data = data.dropna()
print('After NaN removal', len(data))
outdir = args.outdir[0]
fit_model(data,outdir)
pdb.set_trace()
