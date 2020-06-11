#!/bin/bash -l

DATADIR=../data/
OUTDIR=../model_output/R0_2_79/dev/
COUNTRIES="Denmark,Norway,Sweden" #Make sure these are in the same order as when simulating!
DTS=121
ED=2020-06-03
SD=$OUTDIR'/plots/short_dates.csv'
#Visualize model output
./visualize_model_output_herd.py --datadir $DATADIR --countries $COUNTRIES --days_to_simulate $DTS --end_date $ED --short_dates $SD --outdir $OUTDIR
