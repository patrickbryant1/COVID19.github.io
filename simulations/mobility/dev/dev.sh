#!/bin/bash -l

DATADIR=../data/
COUNTRIES="Sweden" #Denmark,Norway,
STAN_MODEL=./mobility_population_sameR.stan
OUTDIR=../model_output/R0_2_79/dev/
ED=2020-03-29 #End date, up to which to include data (different depending on forecast)
./dev_model.py --datadir $DATADIR --country $COUNTRIES --stan_model $STAN_MODEL --end_date $ED --outdir $OUTDIR
