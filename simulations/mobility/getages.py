#!/usr/bin/env python3


import numpy as np
import pandas as pd
import argparse
import sys
import os

parser = argparse.ArgumentParser(description = '''Converting age data from UN''')
parser.add_argument('-i', nargs=1, type= str, default=sys.stdin, help = 'Path to inputfile.')

args = parser.parse_args()
input = args.i[0]

input_df=pd.read_csv(input, sep=',')
output_df=pd.DataFrame([])
countries=input_df['Location'].drop_duplicates()
year=2020

print('"Region, subregion, country or area *",0-9,10-19,20-29,30-39,40-49,50-59,60-69,70-79,80+')
for country in countries:
    new_df=input_df.loc[(input_df['Location']==country)&(input_df['Time']==year)]
    #print (new_df)
    population=[]
    for i in range(0,71,10):
        #print (i,i+10) 
        population+=[new_df.loc[(new_df.AgeGrpStart>=i)&(new_df.AgeGrpStart<=i+5)]['PopTotal'].sum()]
        #print (country,i,population)
    #print (i,i+10)
    i=80
    population+=[new_df.loc[(new_df.AgeGrpStart>=i)]['PopTotal'].sum()]
    #print (country,i,population)
    print ("%s,%.3f,%.3f,%.3f,%.3f,%.3f,%.3f,%.3f,%.3f,%.3f" % (country,
                                                                    population[0],
                                                                    population[1],
                                                                    population[2],
                                                                    population[3],
                                                                    population[4],
                                                                    population[5],
                                                                    population[6],
                                                                    population[7],
                                                                    population[8]
                                                                    ))

