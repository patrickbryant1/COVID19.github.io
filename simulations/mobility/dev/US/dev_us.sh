#!/bin/bash -l

DEATHS=../../data/US/us_deaths.csv
MOBILITY_DATA=../../data/US/Global_Mobility_US.csv
STAN_MODEL=./mobility.stan
OUTDIR=../../model_output/R0_2_79/dev/
DTS=185 #Days to simulate
./dev_us.py --us_deaths $DEATHS --mobility_data $MOBILITY_DATA --stan_model $STAN_MODEL --days_to_simulate $DTS --outdir $OUTDIR
