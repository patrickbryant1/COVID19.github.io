#!/bin/bash -l

DEATHS=/home/patrick/COVID19.github.io/simulations/mobility/data/US/us_deaths.csv
MOBILITY_DATA=/home/patrick/COVID19.github.io/simulations/mobility/data/Global_Mobility_Report.csv
STAN_MODEL=./mobility.stan
OUTDIR=../model_output/R0_2_79/dev/
ED=2020-06-03 #End date, up to which to include data (different depending on forecast)
DTS=121
./dev_us.py --us_deaths $DEATHS --mobility_data $MOBILITY_DATA --stan_model $STAN_MODEL --days_to_simulate $DTS --end_date $ED --outdir $OUTDIR
