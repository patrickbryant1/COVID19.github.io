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




#Arguments for argparse module:
parser = argparse.ArgumentParser(description = '''Simulate according to the ICL response team''')

parser.add_argument('--outdir', nargs=1, type= str, default=sys.stdin, help = 'Path to outdir.')

###FUNCTIONS###
def conv_gamma_params(mean,std):
	'''Returns converted shape and scale params'''
	shape = 1/(std*std)
	scale = mean/shape

	return shape,scale

def plot_pdf(days, prob, name):
	fig, ax = plt.subplots(figsize=(15,10))
	ax.plot(days,prob, label = name)
	ax.set_xlabel('Days')
	ax.set_ylabel('Probability')
	plt.legend()
	fig.savefig(outdir+name+'.svg', format='svg')
	plt.close()

def infection_to_death():
	'''Simulate the time from infection to death: Infection --> Onset --> Death'''

	#####Gamma Distributions#######
	#In R
	#x1 = rgammaAlt(5e6,mean1,cv1) # infection-to-onset ----> do all people who are infected get to onset?
    #x2 = rgammaAlt(5e6,mean2,cv2) # onset-to-death
    #From https://cran.r-project.org/web/packages/EnvStats/EnvStats.pdf
    #shape (α) = 1/std^2
	#scale (β) = mean/shape = mean/(1/std^2) = mean*std^2




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

	#PDF plots
	plot_pdf(days, ito.pdf(days), 'ITO')
	plot_pdf(days, otd.pdf(days)*0.01, 'OTD')
	plot_pdf(days, itd.pdf(days)*0.01, 'ITD')


	#Cumulated survival fraction
	fig, ax = plt.subplots(figsize=(15,10))
	ax.plot(days, 1-(0.01*np.cumsum(itd.pdf(days))))
	ax.set_xlabel('Days')
	ax.set_ylabel('Survival Fraction')
	fig.savefig(outdir+'survival_fraction.svg', format='svg')
	plt.close()

	return itd

def serial_interval_distribution():
	'''Models the the time between when a person gets infected and when
	they subsequently infect another other people
	'''

	#To model the number of infections over time we need to specify a serial
	#interval distribution g with density g(τ), (the time between when a person gets infected and when
	#they subsequently infect another other people), which we choose to be Gamma distributed:
	#g ∼ Gamma (6.5,0.62).
	serial_shape, serial_scale = conv_gamma_params(6.5,0.62)
	serial = gamma(a=serial_shape, scale = serial_scale) #a=shape
	plot_pdf(np.arange(0,21), serial.pdf(np.arange(0,21)), 'Serial')

	return serial

def impact_of_intervention():
	'''Model the impact of each intervention
	'''
	#The impact of each intervention on R t,m is characterised by a set of parameters
	#α 1 , ... , α 6 , with independent prior distributions chosen to be α k ∼ Gamma(0.5,1)
	impact_shape, impact_scale = conv_gamma_params(0.5,1)
	impact = gamma(a=impact_shape, scale = impact_scale) #a=shape
	plot_pdf(np.arange(0,3), impact.pdf(np.arange(0,3)), 'Impact')

	#The impacts α k are shared between all m countries and therefore they are informed by all available
	#data. The prior distribution for R 0 was chosen to be
	#R 0,m ∼ Normal(2.4, |κ|) with κ ∼ Normal(0,0.5)
	K =  np.random.normal(0,0.5,1000) #mean and standard deviation
	fig, ax = plt.subplots(figsize=(15,10))
	sns.distplot(K, label = 'Kappa')
	fig.savefig(outdir+'Kappa.svg', format='svg')
	plt.close()
	fig, ax = plt.subplots(figsize=(15,10))
	R = []
	for k in K:
		R.append(np.random.normal(2.4,np.abs(k)))
	sns.distplot(R)
	fig.savefig(outdir+'R0m.svg', format='svg')
	plt.close()

	return None

def death_seed():
	'''We assume that seeding of new infections begins 30 days before the day after a country has
	cumulatively observed 10 deaths. From this date, we seed our model with 6 sequential days of
	infections drawn from c 1,m , ... , c 6,m ~Exponential(τ), where τ~Exponential(0.03).
	'''
	fig, ax = plt.subplots(figsize=(15,10))
	T = np.random.exponential(0.03, 1000)
	sns.distplot(T)
	fig.savefig(outdir+'tau_seed.svg', format='svg')
	plt.close()
	Exp_tau = []
	for t in T:
		Exp_tau.append(np.random.exponential(t))
	fig, ax = plt.subplots(figsize=(15,10))
	sns.distplot(Exp_tau)
	fig.savefig(outdir+'Exp_tau.svg', format='svg')
	plt.close()

	return None

def simulate(outdir):
	'''π m ∼ ifr m ⋅ (Gamma(5.1,0.86) + Gamma(18.8,0.45))
	ifr = 0.01
	'''

	matplotlib.rcParams.update({'font.size': 20})




	########Daily Deaths#########
	#We observe daily deaths D t,m for days t ∈ 1, ... , n and countries m ∈ 1, ... , p. These daily deaths are
	#modelled using a positive real-valued function d t,m = E(D t,m ) that represents the expected number
	#of deaths attributed to COVID-19. D t,m is assumed to follow a negative binomial distribution with expression as target:
	# mean dt,m and variance dt,m + dt,m^2/ψ (psi),
	#where ψ follows a half normal distribution, i.e.
	#D t,m ∼ Negative Binomial (dt,m , dt,m +dt,m^2/ ψ)
	#ψ ∼ Normal+(0,5). (half normal distribution)
	psi = np.random.normal(0,5,10000) #mean and standard deviation
	psi = psi[np.where(psi>0)] #Positive part of normal = half normal
	fig, ax = plt.subplots(figsize=(15,10))
	sns.distplot(psi)
	fig.savefig(outdir+'psi.svg', format='svg')
	plt.close()

	def cov_neg_bin_params(mean,variance):
		'''Returns n = number of successes, p = prob of success
		#neg_bin(n,p), n = number of successes, p = prob of success
		#If defined by mean and variance: mean = np/(1-p), variance = np/(1-p)^2
		'''
		p = 1-(mean/variance)
		n = (mean*mean)/(variance-mean)
		return n,p

	#The expected total number of successes in
	#a negative binomial distribution with parameters (n, p) is np/(1 − p)

	#Using the probability of death distribution, the expected number of deaths d t,m ,
	#on a given day t, for country, m, is given by the following discrete sum:
	#d t,m = ∑ (τ=0 --> t−1)  c τ,m π t−τ,m
	#where c τ,m is the number of new infections on day τ in country m (see next section)
	#and where π m is ∫ (τ=s−0.5 --> τ=s+0.5) πm(τ)d for s = 2,3

	#The number of deaths today is the sum of the past infections weighted by their probability of death,
	#where the probability of death depends on the number of days since infection.

	#1. Get d_tm = sum(c_tm*itd)
	serial = serial_interval_distribution() #Distribution
	itd = infection_to_death() #Distribution for 0-60 days. e.g. itd[0] = prob of day 1

	fig, ax = plt.subplots(figsize=(15,10))
	for d_tm in np.arange(10,20,0.1):
		E_D_tm = []
		for p in psi:
			variance = d_tm+d_tm*d_tm/p
			n,p = cov_neg_bin_params(d_tm, variance)
			E_D_tm.append(n*p/(1-p))
			#d_tm = E_D_tm[-1]
		sns.distplot(E_D_tm, label = d_tm)
	fig.savefig(outdir+'expectation_neg_binomial.svg', format='svg')




#####MAIN#####
args = parser.parse_args()

outdir = args.outdir[0]
infection_to_death()
pdb.set_trace()
simulate(outdir)
