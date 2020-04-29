#!/bin/bash -l

DATADIR=/home/patrick/COVID19.github.io/simulations/mobility/data/
COUNTRIES="Sweden"
STAN_MODEL=/home/patrick/COVID19.github.io/simulations/mobility/dev/mobility_population.stan
DTS=69 #Days to simulate
OUTDIR=/home/patrick/COVID19.github.io/simulations/mobility/model_output/R0_2_79/dev/
ED=2020-04-19 #End date, up to which to include data (different depending on forecast)
/home/patrick/COVID19.github.io/simulations/mobility/dev/dev_model.py --datadir $DATADIR --countries $COUNTRIES --stan_model $STAN_MODEL --days_to_simulate $DTS --end_date $ED --outdir $OUTDIR
