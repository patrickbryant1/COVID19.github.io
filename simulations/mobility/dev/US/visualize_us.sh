#!/bin/bash -l

INDIR=./modeling_results/
COMDF=./modeling_results/complete_df.csv
CASEDF=./independent_R_estimates/complete_case_df.csv
LOCKDF=./lockdown_df.csv
EARLYLOCKDF=./earlier_lockdown_df.csv
EPIESTIM=/home/patrick/results/COVID19/mobility_and_spread/US/arnes_countries_regions.csv #This data is available here: https://covid19.bioinfo.se/Data/countries_regions.csv
OUTDIR=../../model_output/R0_2_79/dev/
SD=$OUTDIR'/plots/short_dates.csv'
#Visualize model output
./visualize_us.py --indir $INDIR --complete_df $COMDF --lockdown_df $LOCKDF --early_lockdown_df $EARLYLOCKDF --epiestim_df $EPIESTIM  --case_df $CASEDF --short_dates $SD --outdir $OUTDIR
