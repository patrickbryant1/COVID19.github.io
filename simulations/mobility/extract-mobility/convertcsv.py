#!/usr/bin/env python3

import numpy as np
import pandas as pd

from dateutil.parser import parse
from datetime import datetime,date,time, timedelta
from dateutil import parser
import argparse
from argparse import RawTextHelpFormatter


def FormatDate(x):
    #return (parser.parse(x))
    return (datetime.strptime(x,"%Y-%m-%d"))

p = argparse.ArgumentParser(description =  '- convert CSV',
                           formatter_class=RawTextHelpFormatter)
p.add_argument('-i','--input', required= True)
ns = p.parse_args()

startdate=FormatDate("2020-01-01")
input_df=pd.read_csv(ns.input, sep=',',header=None,names=["X","Y"]).sort_values("X")
#print (input_df)

print ("%s,%s,%s" % ("Days","Date","Change"))
for i in range(int(input_df["X"].min()-0.2),int(input_df["X"].max()+0.8)):
    average=input_df.loc[(input_df.X>i-1)&(input_df.X<i+1)]['Y'].mean()
    if np.isnan(average):
        average=0
    print ("%d,%s,%f" % (i,str((startdate+ timedelta(days=i)).date()),average))


#    Names:
#
#    -grocery_and_pharmacy.csv
#    -retail_and_recreation.csv
#    -parks.csv
#    -transit_stations.csv
#    -residential.csv
#    -workplace.csv
