#! /usr/bin/env python3
# -*- coding: utf-8 -*-


import argparse
import sys
import os
import glob
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from scipy.stats import gamma
import numpy as np
import seaborn as sns
import pystan

import pdb


#matplotlib.rcParams.update({'font.size': 20})

#Arguments for argparse module:
parser = argparse.ArgumentParser(description = '''Simulate according to the ICL response team''')

parser.add_argument('--outdir', nargs=1, type= str, default=sys.stdin, help = 'Path to outdir.')

###FUNCTIONS###
def read_data(datadir):
	'''Read in and format all data needed for the model
	'''

	countries = ["Denmark", "Italy", "Germany", "Spain", "United_Kingdom",
			"France", "Norway", "Belgium", "Austria", "Sweden", "Switzerland"]


def conv_gamma_params(mean,std):
	'''Returns converted shape and scale params
	shape (α) = 1/std^2
	scale (β) = mean/shape
	'''
	shape = 1/(std*std)
	scale = mean/shape

	return shape,scale

def infection_to_death():
	'''Simulate the time from infection to death: Infection --> Onset --> Death'''
	#In R
	#x1 = rgammaAlt(5e6,mean1,cv1) # infection-to-onset ----> do all people who are infected get to onset?
    #x2 = rgammaAlt(5e6,mean2,cv2) # onset-to-death
    #From https://cran.r-project.org/web/packages/EnvStats/EnvStats.pdf

	#Infection to onset
	ito_shape, ito_scale = conv_gamma_params(5.1, 0.86)
	ito = gamma(a=ito_shape, scale = ito_scale) #a=shape
	#Onset to death
	otd_shape, otd_scale = conv_gamma_params(18.8, 0.45)
	otd = gamma(a=otd_shape, scale = otd_scale) #a=shape
	#Infection to death: sum of ito and otd
	itd_shape, itd_scale = conv_gamma_params((5.1+18.8), (0.45))
	itd = gamma(a=itd_shape, scale = itd_scale) #a=shape
	#Days to model
	days = np.arange(0,61)

	return itd

def serial_interval_distribution():
	'''Models the the time between when a person gets infected and when
	they subsequently infect another other people
	'''
	serial_shape, serial_scale = conv_gamma_params(6.5,0.62)
	serial = gamma(a=serial_shape, scale = serial_scale) #a=shape
	plot_pdf(np.arange(0,21), serial.pdf(np.arange(0,21)), 'Serial')

	return serial


def simulate(outdir):
	'''Simulate using stan: Efficient MCMC exploration according to Bayesian posterior distribution
	for parameter estimation.
	'''

	serial = serial_interval_distribution() #Distribution
	itd = infection_to_death() #Distribution for 0-60 days. e.g. itd[0] = prob of day 1




#####MAIN#####
args = parser.parse_args()

outdir = args.outdir[0]

#Simulate
simulate(outdir)
