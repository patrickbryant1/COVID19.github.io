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
from statsmodels.distributions.empirical_distribution import ECDF
import numpy as np
import seaborn as sns
import pdb



#Arguments for argparse module:
parser = argparse.ArgumentParser(description = '''Simulate according to the ICL response team''')

parser.add_argument('--outdir', nargs=1, type= str, default=sys.stdin, help = 'Path to outdir.')



###FUNCTIONS###
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
	psi = np.random.normal(0,0.5,1000) #mean and standard deviation

	def cov_neg_bin_params(mean,variance):
		'''Returns n = number of successes, p = prob of success
		#neg_bin(n,p), n = number of successes, p = prob of success
		#If defined by mean and variance: mean = np/(1-p), variance = np/(1-p)^2
		'''
		p = 1-(mean/std)
		n = (mean*mean/variance)/(1-*mean/variance)
		return n,p

	for p in psi:
		variance = d_tm+d_tm*d_tm/psi
		n,p = cov_neg_bin_params(d_tm,
		#neg_bin(n,p), n = number of successes, p = prob of success
		#If defined by mean and variance: mean = np/(1-p), variance = np/(1-p)^2
		D_tm = np.random.negative_binomial(n, p )



	#####Gamma Distributions#######
	#In R
	#x1 = rgammaAlt(5e6,mean1,cv1) # infection-to-onset ----> do all people who are infected get to onset?
    #x2 = rgammaAlt(5e6,mean2,cv2) # onset-to-death
    #From https://cran.r-project.org/web/packages/EnvStats/EnvStats.pdf
    #shape (α) = 1/std^2
	#scale (β) = mean/shape = mean/(1/std^2) = mean*std^2

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


	#Infection to onset
	ito_shape, ito_scale = conv_gamma_params(5.1, 0.86)
	ito = gamma(a=ito_shape, scale = ito_scale) #a=shape
	#Onset to death
	otd_shape, otd_scale = conv_gamma_params(18.8, 0.45)
	otd = gamma(a=otd_shape, scale = otd_scale) #a=shape

	#Days to model
	days = np.arange(0,61)

	#PDF plots
	plot_pdf(days, ito.pdf(days), 'ITO')
	plot_pdf(days, otd.pdf(days)*0.01, 'OTD')

	#Infection to death
	fig, ax = plt.subplots(figsize=(15,10))
	itd = 0.01*(ito.pdf(days)+otd.pdf(days))
	ax.plot(days, itd, label='ITD')
	ax.plot(days, ito.pdf(days)*0.01, label='ITO')
	ax.plot(days, otd.pdf(days)*0.01, label='OTD')
	ax.set_xlabel('Days')
	ax.set_ylabel('Probability')
	plt.legend()
	fig.savefig(outdir+'ITD.svg', format='svg')
	plt.close()

	#Cumulated survival fraction
	fig, ax = plt.subplots(figsize=(15,10))
	ax.plot(days, 1-(0.01*np.cumsum(otd.pdf(days))))
	ax.set_xlabel('Days')
	ax.set_ylabel('Survival Fraction')
	fig.savefig(outdir+'survival_fraction.svg', format='svg')
	plt.close()

	#To model the number of infections over time we need to specify a serial
	#interval distribution g with density g(τ), (the time between when a person gets infected and when
	#they subsequently infect another other people), which we choose to be Gamma distributed:
	#g ∼ Gamma (6.5,0.62).
	serial_shape, serial_scale = conv_gamma_params(6.5,0.62)
	serial = gamma(a=serial_shape, scale = serial_scale) #a=shape
	plot_pdf(np.arange(0,21), serial.pdf(np.arange(0,21)), 'Serial')


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

	#We assume that seeding of new infections begins 30 days before the day after a country has
	#cumulatively observed 10 deaths. From this date, we seed our model with 6 sequential days of
	#infections drawn from c 1,m , ... , c 6,m ~Exponential(τ), where τ~Exponential(0.03).
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



#####MAIN#####
args = parser.parse_args()

outdir = args.outdir[0]
simulate(outdir)
