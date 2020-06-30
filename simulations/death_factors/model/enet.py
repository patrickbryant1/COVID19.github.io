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
    coef_df['Coefficient'] = np.array(np.absolute(coefs))
    coef_df=coef_df.sort_values(by='Coefficient',ascending=False)

    fig, ax = plt.subplots(figsize=(18/2.54,100/2.54))
    sns.barplot(x="Coefficient", y="Feature", data=coef_df)
    ax.set_xlabel('abs(Coefficient)')
    #ax.set_ylim([min(coefs),max(coefs)])
    fig.tight_layout()
    fig.show()
    fig.savefig(outdir+id+'_all_enet_coefs.png', format='png')
    plt.close()

    #Plot top 10 coefs
    coef_df = coef_df.reset_index()
    top10 = coef_df.loc[0:20]
    fig, ax = plt.subplots(figsize=(18/2.54,18/2.54))
    sns.barplot(x="Coefficient", y="Feature", data=top10)
    ax.set_xlabel('abs(Coefficient)')
    #ax.set_ylim([min(coefs),max(coefs)])
    fig.tight_layout()
    fig.savefig(outdir+id+'_top20_enet_coefs.png', format='png')
    plt.close()


def fit_model(data,outdir):
    '''Fit model to data
    '''
    #Select data where the death rate is at least 1
    #data = data[data['Death rate per 1000']>10]
    y1 = np.array(data['Death rate per 1000'])
    y2 = np.array(data['Cumulative deaths'])
    data = data.drop(['Death rate per 1000','Cumulative deaths'],axis=1)
    X = np.array(data[data.columns[4:]])
    #Fit 1
    regr1 = ElasticNet(random_state=0)
    regr1.fit(X,y1)
    visualize_output(data.columns[4:], regr1.coef_ ,outdir,'per1000')
    pred = regr1.predict(X)
    print('Average error:',np.average(np.absolute(pred-y1)))
    print('Rsq:',regr1.score(X,y1))
    fig, ax = plt.subplots(figsize=(9/2.54,9/2.54))
    plt.scatter(y1,pred,s=2)
    plt.title('Rsq '+str(np.round(regr1.score(X,y1),2)))
    ax.set_xlabel('True')
    ax.set_ylabel('Predicted')
    fig.tight_layout()
    fig.savefig(outdir+'pred_vs_true_per1000.png', format='png')

    #Fit 2
    regr2 = ElasticNet(random_state=0)
    regr2.fit(X,y2)
    visualize_output(data.columns[4:], regr2.coef_ ,outdir,'cum_deaths')
    pred = regr2.predict(X)
    print('Average error:',np.average(np.absolute(pred-y2)))
    print('Rsq:',regr2.score(X,y2))
    fig, ax = plt.subplots(figsize=(9/2.54,9/2.54))
    plt.scatter(y2,pred,s=2)
    plt.title('Rsq '+str(np.round(regr2.score(X,y2),2)))
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
