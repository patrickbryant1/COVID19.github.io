#!/bin/bash -l

DATADIR=../data/
COUNTRIES="Sweden" #Denmark,Norway,
POPULATION="10.023" #5.806,5.368,
STAN_MODEL=./mobility_population_sameR.stan
DTS=62 #Days to simulate
OUTDIR=../model_output/R0_2_79/dev/
ED=2020-03-29 #End date, up to which to include data (different depending on forecast)
./dev_model.py --datadir $DATADIR --countries $COUNTRIES --population $POPULATION --stan_model $STAN_MODEL --days_to_simulate $DTS --end_date $ED --outdir $OUTDIR
