#!/bin/bash -l

DATADIR=../data/
COUNTRIES="Sweden"
STAN_MODEL=./mobility_population.stan
DTS=93 #Days to simulate
OUTDIR=../model_output/R0_2_79/dev/
ED=2020-04-29 #End date, up to which to include data (different depending on forecast)
./dev_model.py --datadir $DATADIR --countries $COUNTRIES --stan_model $STAN_MODEL --days_to_simulate $DTS --end_date $ED --outdir $OUTDIR
