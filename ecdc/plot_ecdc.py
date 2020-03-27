#! /usr/bin/env python3
# -*- coding: utf-8 -*-


import argparse
import sys
import os
import glob
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import pdb



#Arguments for argparse module:
parser = argparse.ArgumentParser(description = '''Plot ECDC data provided in csv format.''')

parser.add_argument('--csvfile', nargs=1, type= str, default=sys.stdin, help = 'Path to csv file with ECDC data.')



###FUNCTIONS###
def plot_per_country(corona_df):
	'''Plot ECDC collected statistics per country in a joint figure
	Columns:
	dateRep,day,month,year,cases,deaths,countriesAndTerritories,geoId,countryterritoryCode,popData2018
	'''
	countries = corona_df['countriesAndTerritories'].unique()


	for country in countries:
		country_data = corona_df[corona_df['countriesAndTerritories']==country]
		pdb.set_trace()

#####MAIN#####
args = parser.parse_args()

corona_df = pd.read_csv(args.csvfile[0])
