#!/bin/bash -l

DEATHS=/home/patrick/COVID19.github.io/simulations/mobility/data/US/us_deaths.csv
MOBILITY_DATA=/home/patrick/COVID19.github.io/simulations/mobility/data/Global_Mobility_Report.csv
STAN_MODEL=./mobility.stan
OUTDIR=../model_output/R0_2_79/dev/
DTS=112 #Days to simulate
USE_FULL=True #Whether to use the values from the full lockdown effect or not
./dev_us.py --us_deaths $DEATHS --mobility_data $MOBILITY_DATA --stan_model $STAN_MODEL --days_to_simulate $DTS --use_full $USE_FULL --outdir $OUTDIR
