#!/bin/bash -l

DATADIR=../data/
OUTDIR=../model_output/R0_2_79/dev/w_herd/
COUNTRIES="Sweden" #Make sure these are in the same order as when simulating!
DTS=93
SD=$OUTDIR'/plots/short_dates.csv'
#Visualize model output
./visualize_model_output_per_age_group.py --datadir $DATADIR --countries $COUNTRIES --days_to_simulate $DTS --short_dates $SD --outdir $OUTDIR
