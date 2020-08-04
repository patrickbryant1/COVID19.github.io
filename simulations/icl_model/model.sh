#!/bin/bash -l

DATADIR=./data/
COUNTRIES="Austria,Belgium,Denmark,France,Germany,Italy,Norway,Spain,Sweden,Switzerland,United_Kingdom"
STAN_MODEL=./base.stan
DTS=84 #Days to simulate
ED=2020-03-29 #End date, up to which to include data (different depending on forecast)
OUTDIR=./model_output/3_week_forecast/
./icl_model.py --datadir $DATADIR --countries $COUNTRIES --stan_model $STAN_MODEL --days_to_simulate $DTS --end_date $ED --outdir $OUTDIR
