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
from tensorflow.keras.layers import LSTM, Dense, Activation
from tensorflow.keras.callbacks import TensorBoard
import pdb



#Arguments for argparse module:
parser = argparse.ArgumentParser(description = '''RNN.
                                                A nonlinear model is necessary due to the irregularity of the
                                                mobility effect. Historical data is used to take the previous
                                                epidemic development into account, which is not possible with
                                                e.g. MCMC simulations. ''')
parser.add_argument('--outdir', nargs=1, type= str, default=sys.stdin, help = 'Path to outdir.')


###FUNCTIONS###
def CV_split(X,y,csi,fetched_countries,x_lens):
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
    train_lens = {1:[],2:[],3:[],4:[],5:[]}
    X_valid = {1:[],2:[],3:[],4:[],5:[]}
    y_valid = {1:[],2:[],3:[],4:[],5:[]}
    csi_valid = {1:[0],2:[0],3:[0],4:[0],5:[0]}
    valid_countries = {1:[],2:[],3:[],4:[],5:[]}
    valid_lens = {1:[],2:[],3:[],4:[],5:[]}
    #Split
    kf = KFold(n_splits=5,random_state=42, shuffle=True)
    split = 1
    for train_index, valid_index in kf.split(all_index):
        #Fetch all train points
        for ti in train_index:
            c1=csi[ti]
            c2=csi[ti+1]
            X_train[split].extend(X[c1:c2])
            y_train[split].extend(y[c1:c2,:])
            #Country splits in data
            csi_train[split].append(len(y_train[split]))
            #Country names
            train_countries[split].append(fetched_countries[ti])
            #Lengths of data
            train_lens[split].extend(x_lens[c1:c2])
        #Fetch all valid points
        for vi in valid_index:
            c1=csi[vi]
            c2=csi[vi+1]
            X_valid[split].extend(X[c1:c2])
            y_valid[split].extend(y[c1:c2,:])
            #Country splits in data
            csi_valid[split].append(len(y_valid[split]))
            #Country names
            valid_countries[split].append(fetched_countries[vi])
            #Lengths of data
            valid_lens[split].extend(x_lens[c1:c2])
        #Increase split
        split+=1
    return X_train, y_train, csi_train, train_countries, train_lens, X_valid, y_valid, csi_valid, valid_countries, valid_lens


def train_generator(X_train,y_train,batch_size,train_lens):
    while True:
        random_numbers = np.random.choice(len(y_train),size=(batch_size,),replace=False) #without replacemen
        x_batch = []
        y_batch = y_train[random_numbers]
        padlen = max(train_lens[random_numbers])
        for rn in random_numbers:
            zeros = np.zeros((padlen,7))
            zeros[:len(X_train[rn]),:] = X_train[rn]
            x_batch.append(zeros)
        yield np.array(x_batch), y_batch

def train_RNN(X_train,y_train, X_valid, y_valid_, csi_train, csi_valid, train_lens, valid_lens, valid_countries,ip,pl,outdir):
    '''Fit RNN
    '''
    batch_size=4
    num_epochs=1
    num_timesteps=None
    num_features=7
    model = Sequential()
    model.add(LSTM(units=128, dropout=0.5, batch_input_shape=(batch_size, num_timesteps, num_features)))
    model.add(Dense(pl))#Number of days to predict

    #Compile
    model.compile(loss="mean_absolute_percentage_error", optimizer='adam', metrics=['accuracy'])
    #Write summary of model
    model.summary()
    #Fit model
    model.fit_generator(train_generator(X_train,y_train,batch_size,train_lens), steps_per_epoch=30, epochs=10, verbose=1)



###MAIN###
#Set font size
matplotlib.rcParams.update({'font.size': 9})
args = parser.parse_args()
outdir = args.outdir[0]
#Load data
X = np.load('X.npy',allow_pickle = True)
#Get lengths for X
x_lens = []
for i in range(len(X)):
    x_lens.append(len(X[i]))
y = np.load('y.npy',allow_pickle = True)
csi = np.load('csi.npy',allow_pickle = True)
fetched_countries = np.load('fetched_countries.npy',allow_pickle = True)

#Tensorboard for logging and visualization
log_name = 'log'
tensorboard = TensorBoard(log_dir=outdir+log_name)

#Construct 5-fold CV
X_train, y_train, csi_train, train_countries, train_lens, X_valid, y_valid, csi_valid, valid_countries, valid_lens = CV_split(X,y,csi,fetched_countries,x_lens)
ip=21 #include period, the minimum period to include data
pl=21 #predict lag
for split in range(1,6):
    #Train
    X_train_split = np.array(X_train[split])
    y_train_split = np.array(y_train[split])
    csi_train_split = csi_train[split]
    train_countries_split = train_countries[split]
    train_lens_split = np.array(train_lens[split])
    X_valid_split = np.array(X_valid[split])
    y_valid_split = np.array(y_valid[split])
    csi_valid_split = csi_valid[split]
    valid_countries_split = valid_countries[split]
    valid_lens_split = np.array(valid_lens[split])
    print(len(y_train_split),'training points and', len(y_valid_split),' validation points.')
    train_RNN(X_train_split,y_train_split, X_valid_split, y_valid_split, csi_train_split, csi_valid_split,train_lens_split, valid_lens_split, valid_countries_split,ip,pl,outdir+'split'+str(split)+'/')
