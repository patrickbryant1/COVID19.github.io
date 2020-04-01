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



#Arguments for argparse module:
parser = argparse.ArgumentParser(description = '''Simulate fraction infected for different R0
												t = 1- e^-R0t.''')

parser.add_argument('--outdir', nargs=1, type= str, default=sys.stdin, help = 'Path to outdir.')



###FUNCTIONS###
def simulate(outdir):
	'''t = 1- e^-R0t
	Evaluate equation for different R0
	'''

	matplotlib.rcParams.update({'font.size': 20})
	fig, ax = plt.subplots(figsize=(15,10))

	#No preventive measures
	R0 = np.arange(0,5,0.01)

	#With preventive measures
	#RE = = (1-ctot)R0
	#R0 = p*c*l
	#p = transmission prob. for a contact
	#R0 = 2-2.5, Sweden = 10 million → p = 2-2.5/10 million = 0,0000002-0,00000025
	#c = number of contacts/day
	#l = duration of infectious period (Incubation period = 2-14 days for Corona, infectious period not known)
	#Reduction in number of contacts
	ctot = np.arange(0.2,1,0.2)
	

	tau = np.arange(0.001,1,0.001)
	tau_er = []
	frac_inf = []
	for i in range(len(R0)):
		R = R0[i]
		er = [] #Save errors in tau
		for t in tau:
			calc_t = 1-np.exp(-R*t)
			er.append(t-calc_t)
		
		er = np.absolute(np.array(er))
		pos = np.where(er==min(er))[0][0]
		tau_er.append(min(er))
		frac_inf.append(tau[pos])

	ax.plot(R0, frac_inf)

	#If measures are reduced: 
	# #Get the tau values of the reduced R0s
	# RE = []
	# RE_frac = []
	# red = int(0.3*len(R0))
	# for i in range(red ,len(R0)):
	# 	RE.append(R0[i])
	# 	RE_frac.append(frac_inf[i-red])

	# ax.plot(RE, RE_frac)

	#ax.errorbar(R0, frac_inf, yerr=tau_er, fmt='--o') #Not visible
	ax.set_xlabel('R0')
	ax.set_ylabel('Final fraction infected')

	fig.savefig(outdir+'R0_vs_tau.png', format='png')
	plt.close()
	
	
#####MAIN#####
args = parser.parse_args()

outdir = args.outdir[0]
simulate(outdir)
