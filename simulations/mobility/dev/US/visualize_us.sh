#!/bin/bash -l

INDIR=/home/patrick/results/COVID19/mobility_and_spread/US/20200611/
COMDF=./complete_df.csv
CASEDF=./independent_R_estimates/complete_case_df.csv
LOCKDF=./lockdown_df.csv
EPIESTIM=./independent_R_estimates/EpiEstimR_estimates.csv
#/home/patrick/results/COVID19/mobility_and_spread/US/arnes_countries_regions.csv
OUTDIR=../../model_output/R0_2_79/dev/
SD=$OUTDIR'/plots/short_dates.csv'
#Visualize model output
./visualize_us.py --indir $INDIR --complete_df $COMDF --lockdown_df $LOCKDF --epiestim_df $EPIESTIM  --case_df $CASEDF --short_dates $SD --outdir $OUTDIR
