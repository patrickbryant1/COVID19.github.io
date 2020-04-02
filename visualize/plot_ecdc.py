#! /usr/bin/env python3
# -*- coding: utf-8 -*-


import argparse
import sys
import os
import glob
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
import numpy as np
import seaborn as sns
import pdb



#Arguments for argparse module:
parser = argparse.ArgumentParser(description = '''Plot ECDC data provided in csv format.''')

parser.add_argument('--ecdc_csv', nargs=1, type= str, default=sys.stdin, help = 'Path to csv file with ECDC data.')
parser.add_argument('--wb_data', nargs=1, type= str, default=sys.stdin, help = 'Path to directory with csv files containing worldbank data.')
parser.add_argument('--outdir', nargs=1, type= str, default=sys.stdin, help = 'Path to outdir.')



###FUNCTIONS###
def order_dates(ecdc_df):
	'''Assign a value to all dates in the corona df - starting with 0
	'''

	years = np.sort(ecdc_df['year'].unique())
	dmy = {}
	i = 0 #index
	for y in years:
		y_df = ecdc_df[ecdc_df['year']==y]
		months = np.sort(y_df['month'].unique())
		for m in months:
			m_df = y_df[y_df['month']==m]
			days = np.sort(ecdc_df['day'].unique())
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
	ecdc_df['days_since_outbreak'] = 0
	for i in range(len(ecdc_df)):
		dateRep = ecdc_df['dateRep'].loc[i]
		ecdc_df.at[i,'DaysSinceFirstReportedCase'] = dmy[dateRep]

	return ecdc_df

def add_wb_data(ecdc_df, pop_meta_df):
	'''Add wb data to the ecdc df per country
	'''
	#Add new columns to ecdc df
	ecdc_df['popData2018_millions'] = 0
	ecdc_df['Region'] = 'Home'
	ecdc_df['IncomeGroup'] = 'Unknown'
	countries = ecdc_df['countriesAndTerritories'].unique()
	for country in countries:
		country_data = pop_meta_df[pop_meta_df['Country Name']==country]
		try:
			pop_size = np.round(country_data['2018']/1000000,0).values[0]
		except:
			pop_size = 0
		try:
			region = country_data['Region'].values[0]
		except:
			region = 'NA'
		try:
			inc = country_data['IncomeGroup'].values[0]
		except:
			inc = 'NA'
		#Assign
		ecdc_df.loc[ecdc_df['countriesAndTerritories']==country, 'popData2018_millions']=pop_size
		ecdc_df.loc[ecdc_df['countriesAndTerritories']==country, 'Region']=region
		ecdc_df.loc[ecdc_df['countriesAndTerritories']==country, 'IncomeGroup']=inc

	return ecdc_df

def plot_per_country(ecdc_df, pop_meta_df, outdir):
	'''Plot ECDC collected statistics per country in a joint figure
	Columns:
	dateRep,day,month,year,cases,deaths,countriesAndTerritories,geoId,countryterritoryCode,popData2018
	'''
	#Set fontsize
	matplotlib.rcParams.update({'font.size': 15})

	for_markdown = open(outdir+'for_markdown.txt', 'w')
	#Order dates - get days since start of data
	ecdc_df =order_dates(ecdc_df)
	#Add worldbank data
	ecdc_df = add_wb_data(ecdc_df, pop_meta_df)
	#Plot deaths per country, where each country has at least 10 deaths
	fig, ax = plt.subplots(figsize=(20,10))
	death_df = ecdc_df[ecdc_df['deaths']>=10]
	sns.lineplot(x='DaysSinceFirstReportedCase', y = 'deaths', data=death_df, hue = 'countryterritoryCode')
	fig.savefig(outdir+'deaths_10_per_country.png', format='png')
	plt.close()
	#Plot deaths grouped by income group
	fig, ax = plt.subplots(figsize=(20,10))
	sns.lineplot(x='DaysSinceFirstReportedCase', y = 'deaths', data=death_df, hue = 'IncomeGroup')
	fig.savefig(outdir+'deaths_10_income_group_country.png', format='png')
	plt.close()



	#Plot cases and deaths individually
	plot_ind = False
	if plot_ind == True:

		countries = ecdc_df['countriesAndTerritories'].unique()
		for country in countries:
			country_data = ecdc_df[ecdc_df['countriesAndTerritories']==country]
			start = country_data['DaysSinceFirstReportedCase'].min() #Start of outbreak
			#Cases
			fig, ax = plt.subplots(figsize=(10,10))
			ax.bar((country_data['DaysSinceFirstReportedCase']-start).values, country_data['cases'], width=0.8)
			ax.set_xlabel('Days since outbreak')
			ax.set_ylabel('Cases')
			fig.savefig(outdir+country+'_cases.png', format='png')
			plt.close()

			#Deaths
			fig, ax = plt.subplots(figsize=(10,10))
			ax.bar((country_data['DaysSinceFirstReportedCase']-start).values, country_data['deaths'], width=0.8)
			ax.set_xlabel('Days since outbreak')
			ax.set_ylabel('Deaths)')

			fig.savefig(outdir+country+'_deaths.png', format='png')
			plt.close()

			for_markdown.write(country+'\n')
			for_markdown.write('!['+country+'_cases](./assets/'+country+'_cases.png)'+'\n'+'\n')
			for_markdown.write('!['+country+'_cases](./assets/'+country+'_deaths.png)'+'\n'+'\n')


		for_markdown.close()

	return ecdc_df

#####MAIN#####
args = parser.parse_args()


ecdc_df = pd.read_csv(args.ecdc_csv[0])
wb_data = args.wb_data[0]
pop_df = pd.read_csv(wb_data+'population_total.csv')
meta_df = pd.read_csv(wb_data+'Metadata_Country.csv')
pop_meta_df = pd.merge(pop_df, meta_df, on=['Country Code'], how='left')
outdir = args.outdir[0]
plot_per_country(ecdc_df, pop_meta_df, outdir)
