#!/bin/bash -l

DF=/home/patrick/results/COVID19/mobility_and_spread/US/20200611/complete_df.csv
MR=/home/patrick/results/COVID19/mobility_and_spread/US/20200611/summary.csv #Modelling results
OUTDIR=/home/patrick/COVID19.github.io/simulations/mobility/model_output/R0_2_79/dev/
DTS=112 #Max number of days
DE=21 #Days earlier
#Calculate no opening up
./dev_us_earlier_lock.py --complete_df $DF --modelling_results $MR --days_to_simulate $DTS --days_earlier $DE --outdir $OUTDIR
