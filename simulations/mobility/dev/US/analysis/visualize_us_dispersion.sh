#!/bin/bash -l

INDIR=/home/patrick/results/COVID19/mobility_and_spread/US/20200615/
COMDF=/home/patrick/results/COVID19/mobility_and_spread/US/20200615/complete_df.csv
LOCKDF=/home/patrick/COVID19.github.io/simulations/mobility/dev/US/lockdown_df.csv
OUTDIR=/home/patrick/results/COVID19/mobility_and_spread/US/20200615/
SD=$OUTDIR'/plots/short_dates.csv'
#Visualize model output
./visualize_us.py --indir $INDIR --complete_df $COMDF --lockdown_df $LOCKDF --short_dates $SD --outdir $OUTDIR
