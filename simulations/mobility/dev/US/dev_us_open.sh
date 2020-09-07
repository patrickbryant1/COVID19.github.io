#!/bin/bash -l

DEATHS=../../data/US/us_deaths.csv
MODELED_SUMMARY=./modeling_results/summary.csv
DTO=./modeling_results/days_til_open.csv
MOBILITY_DATA=../../data/US/Global_Mobility_US.csv
POPDATA=../../data/US/us_state_populations.csv
STAN_MODEL=./mobility_open.stan
OUTDIR=../../model_output/R0_2_79/dev/
DTS=71 #Days to simulate
SD='20200411' #start date
ED='20200901' #end date
./dev_us_open.py --us_deaths $DEATHS --modeled_summary $MODELED_SUMMARY --days_til_open $DTO --mobility_data $MOBILITY_DATA --population_sizes $POPDATA --stan_model $STAN_MODEL --days_to_simulate $DTS --end_date $ED --start_date $SD --outdir $OUTDIR
