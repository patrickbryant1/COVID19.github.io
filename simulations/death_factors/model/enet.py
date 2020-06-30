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

def visualize_output(cols,coefs,outdir):
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
    fig.savefig(outdir+'all_enet_coefs.png', format='png')
    plt.close()

    #Plot top 10 coefs
    coef_df = coef_df.reset_index()
    top10 = coef_df.loc[0:10]
    fig, ax = plt.subplots(figsize=(18/2.54,18/2.54))
    sns.barplot(x="Coefficient", y="Feature", data=top10)
    ax.set_xlabel('abs(Coefficient)')
    #ax.set_ylim([min(coefs),max(coefs)])
    fig.tight_layout()
    fig.show()
    fig.savefig(outdir+'top10_enet_coefs.png', format='png')
    plt.close()
    pdb.set_trace()

def fit_model(data,outdir):
    '''Fit model to data
    '''

    y1 = np.array(data['Death rate per 1000'])
    y2 = np.array(data['Cumulative deaths'])
    data = data.drop(['Death rate per 1000','Cumulative deaths'],axis=1)
    X = np.array(data[data.columns[4:]])
    #Fit 1
    regr1 = ElasticNet(random_state=0)
    regr1.fit(X,y1)
    visualize_output(data.columns[4:], regr1.coef_ ,outdir)
    #Fit 2
    pdb.set_trace()
    regr2 = ElasticNet(random_state=0)
    regr2.fit(X,y2)
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
