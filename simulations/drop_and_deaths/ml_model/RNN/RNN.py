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
from scipy.stats import pearsonr
from sklearn.model_selection import KFold

#NN
import tensorflow as tf
import tensorflow.keras as keras
from tensorflow.keras.models import Sequential, Model
from tensorflow.keras.layers import Dense, Embedding, Flatten
from tensorflow.keras.layers import Bidirectional,CuDNNLSTM, Dropout, BatchNormalization

import pdb



#Arguments for argparse module:
parser = argparse.ArgumentParser(description = '''RNN.
                                                A nonlinear model is necessary due to the irregularity of the
                                                mobility effect. Historical data is used to take the previous
                                                epidemic development into account, which is not possible with
                                                e.g. MCMC simulations. ''')
parser.add_argument('--outdir', nargs=1, type= str, default=sys.stdin, help = 'Path to outdir.')


###FUNCTIONS###
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
            csi_train[split].append(len(y_train[split]))
            #Country names
            train_countries[split].append(fetched_countries[ti])
        #Fetch all valid points
        for vi in valid_index:
            c1=csi[vi]
            c2=csi[vi+1]
            X_valid[split].extend(X[c1:c2,:])
            y_valid[split].extend(y[c1:c2,:])
            #Country splits in data
            csi_valid[split].append(len(y_valid[split]))
            #Country names
            valid_countries[split].append(fetched_countries[vi])
        #Increase split
        split+=1
    return X_train, y_train, csi_train, train_countries, X_valid, y_valid, csi_valid, valid_countries

def pad_data(X, padlen):
	'''Pads entries in each batch with zeros to have equal lengths
	'''

	#Loop through X
	X_pad = [] #save padded data
	for i in range(0,len(X)):
		if len(X[i])>padlen:
			pdb.set_trace()
		X_pad.append(np.pad(X[i], (0,padlen-len(X[i])), 'constant'))

	return X_pad


def train_RNN(X_train,y_train, X_valid, y_valid_, csi_train, csi_valid,valid_countries,ip,pl,outdir):
    '''Fit RNN
    '''

    model = Sequential()
    model.add(LSTM(units=128, dropout=0.5))
    model.add(Dense(pl))
    model.add(Activation('sigmoid'))

    #Compile
    model.compile(loss="mean_absolute_percentage_error", optimizer='adam', metrics=['accuracy'])
    #Write summary of model
    model.summary()
    batch_size=4
    #Fit model
    model.fit(X_train, y_train, batch_size = batch_size,
              epochs=num_epochs,
              validation_data=(X_valid,y_valid),
              shuffle=True) #Dont feed continuously


###MAIN###
#Set font size
matplotlib.rcParams.update({'font.size': 9})
args = parser.parse_args()
outdir = args.outdir[0]
#Load data
X = np.load('X.npy',allow_pickle = True)
y = np.load('y.npy',allow_pickle = True)
csi = np.load('csi.npy',allow_pickle = True)
fetched_countries = np.load('fetched_countries.npy',allow_pickle = True)

#Tensorboard for logging and visualization
log_name = str(time.time())
tensorboard = TensorBoard(log_dir=out_dir+log_name)

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
    print(len(y_train_split),'training points and', len(y_valid_split),' validation points.')
    train_RNN(X_train_split,y_train_split, X_valid_split, y_valid_split, csi_train_split, csi_valid_split,valid_countries_split,ip,pl,outdir+'split'+str(split)+'/')
