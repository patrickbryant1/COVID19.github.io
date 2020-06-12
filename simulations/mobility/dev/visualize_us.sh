#!/bin/bash -l

INDIR=/home/patrick/results/COVID19/mobility_and_spread/US/20200611/
DF=/home/patrick/results/COVID19/mobility_and_spread/US/20200611/complete_df.csv
OUTDIR=/home/patrick/COVID19.github.io/simulations/mobility/model_output/R0_2_79/dev/
SD=$OUTDIR'/plots/short_dates.csv'
#Visualize model output
./visualize_us.py --indir $INDIR --complete_df $DF --short_dates $SD --outdir $OUTDIR
