#!/bin/bash -l

DF=./modeling_results/complete_df.csv
MR=./modeling_results/summary.csv #Modelling results
OUTDIR=../../model_output/R0_2_79/dev/
DTS=185 #Max number of days
#Calculate no opening up
./dev_us_calc_diff.py --complete_df $DF --modelling_results $MR --days_to_simulate $DTS --outdir $OUTDIR
