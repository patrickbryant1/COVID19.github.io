#!/bin/bash -l

INDIR=/home/patrick/results/COVID19/mobility_and_spread/US/20200611/
COMDF=/home/patrick/COVID19.github.io/simulations/mobility/dev/US/complete_df.csv
LOCKDF=/home/patrick/COVID19.github.io/simulations/mobility/dev/US/lockdown_df.csv
EPIESTIM=/home/patrick/results/COVID19/mobility_and_spread/US/arnes_countries_regions.csv
OUTDIR=/home/patrick/COVID19.github.io/simulations/mobility/model_output/R0_2_79/dev/
SD=$OUTDIR'/plots/short_dates.csv'
#Visualize model output
./visualize_us.py --indir $INDIR --complete_df $COMDF --lockdown_df $LOCKDF --epiestim_df $EPIESTIM --short_dates $SD --outdir $OUTDIR
