#!/bin/bash -l

DATADIR=/home/patrick/COVID19.github.io/simulations/mobility/data/
COUNTRIES="Austria,Belgium,Denmark,France,Germany,Italy,Norway,Spain,Sweden,Switzerland,United_Kingdom"
STAN_MODEL=/home/patrick/COVID19.github.io/simulations/mobility/mobility.stan
DTS=84 #Days to simulate
OUTDIR=/home/patrick/COVID19.github.io/simulations/mobility/model_output/R0_2_79/3_week_forecast/19_April/
ED=2020-03-29 #End date, up to which to include data (different depending on forecast)
/home/patrick/COVID19.github.io/simulations/mobility/mobility_model.py --datadir $DATADIR --countries $COUNTRIES --stan_model $STAN_MODEL --days_to_simulate $DTS --end_date $ED --outdir $OUTDIR
