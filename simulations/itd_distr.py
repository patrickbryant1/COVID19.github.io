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
parser = argparse.ArgumentParser(description = '''Simulate fraction infected for different R0
												t = 1- e^-R0t.''')

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
	plot_pdf(days, itd, 'ITD')

	#Cumulated survival fraction
	fig, ax = plt.subplots(figsize=(15,10))
	ax.plot(days, 1-(0.01*np.cumsum(otd.pdf(days))))
	ax.set_xlabel('Days')
	ax.set_ylabel('Survival Fraction')
	fig.savefig(outdir+'survival_fraction.svg', format='svg')
	plt.close()




#####MAIN#####
args = parser.parse_args()

outdir = args.outdir[0]
simulate(outdir)
