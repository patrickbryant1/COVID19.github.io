#!/usr/bin/env bash
DROPDF=/home/patrick/COVID19.github.io/simulations/drop_and_deaths/initial_analysis/drop_df.csv
STAN_MODEL=/home/patrick/COVID19.github.io/simulations/drop_and_deaths/model_drop_impact/drop_impact.stan
WTS=5
OUTDIR=/home/patrick/results/COVID19/drop_and_deaths/
/home/patrick/COVID19.github.io/simulations/drop_and_deaths/model_drop_impact/drop_model.py --drop_df $DROPDF --stan_model $STAN_MODEL --weeks_to_simulate $WTS --outdir $OUTDIR
