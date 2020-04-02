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

#####MAIN#####
args = parser.parse_args()

outdir = args.outdir[0]
simulate(outdir)
