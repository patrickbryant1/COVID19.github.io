#!/bin/bash -l

DATADIR=../data/
COUNTRIES="Denmark,Norway,Sweden"
STAN_MODEL=./mobility.stan
OUTDIR=../model_output/R0_2_79/dev/
ED=2020-06-03 #End date, up to which to include data (different depending on forecast)
DTS=107
./dev_model.py --datadir $DATADIR --countries $COUNTRIES --stan_model $STAN_MODEL --days_to_simulate $DTS --end_date $ED --outdir $OUTDIR
