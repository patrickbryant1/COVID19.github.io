#!/bin/bash -l

DATADIR=/home/patrick/COVID19.github.io/simulations/mobility/data/
OUTDIR=/home/patrick/COVID19.github.io/simulations/mobility/model_output/R0_2_79/dev/
COUNTRIES="Sweden" #Make sure these are in the same order as when simulating!
DTS=69
SD=$OUTDIR'/plots/short_dates.csv'
#Visualize model output
/home/patrick/COVID19.github.io/simulations/mobility/dev/visualize_model_output.py --datadir $DATADIR --countries $COUNTRIES --days_to_simulate $DTS --short_dates $SD --outdir $OUTDIR
