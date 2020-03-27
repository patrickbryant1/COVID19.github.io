#! /usr/bin/env python3
# -*- coding: utf-8 -*-


import argparse
import sys
import os
import glob
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import pdb



#Arguments for argparse module:
parser = argparse.ArgumentParser(description = '''Plot ECDC data provided in csv format.''')

parser.add_argument('--csvfile', nargs=1, type= str, default=sys.stdin, help = 'Path to csv file with ECDC data.')



###FUNCTIONS###
def order_dates(corona_df):
	'''Assign a value to all dates in the corona df - starting with 0
	'''

	years = np.sort(corona_df['year'].unique())
	dmy = {}
	i = 0 #index
	for y in years:
		y_df = corona_df[corona_df['year']==y]
		months = np.sort(y_df['month'].unique())
		for m in months:
			m_df = y_df[y_df['month']==m]
			days = np.sort(corona_df['day'].unique())
			for d in days:
				if len(str(int(d)))<2:
					d = '0'+str(int(d))
				else:
					d = str(int(d))

				if len(str(int(m)))<2:
					m = '0'+str(int(m))
				else:
					m = str(int(m))

				dmy[d+'/'+m+'/'+str(int(y))] = i
				i+=1

	#Add indices
	corona_df['days_since_outbreak'] = 0
	for i in range(len(corona_df)):
		dateRep = corona_df['dateRep'].loc[i]
		corona_df.set_value(i,'days_since_outbreak',dmy[dateRep])

	return corona_df

def plot_per_country(corona_df):
	'''Plot ECDC collected statistics per country in a joint figure
	Columns:
	dateRep,day,month,year,cases,deaths,countriesAndTerritories,geoId,countryterritoryCode,popData2018
	'''

	#Order dates - get days since start of data
	corona_df =order_dates(corona_df)
	countries = corona_df['countriesAndTerritories'].unique()


	fig, ax = plt.subplots(figsize=(10,10))
	for country in countries:
		country_data = corona_df[corona_df['countriesAndTerritories']==country]
		plt.plot(country_data['days_since_outbreak'], 1/country_data['cases'])
		plt.yscale('log')
	plt.show()
	pdb.set_trace()
		

#####MAIN#####
args = parser.parse_args()


corona_df = pd.read_csv(args.csvfile[0], encoding = "ISO-8859-1")
plot_per_country(corona_df)