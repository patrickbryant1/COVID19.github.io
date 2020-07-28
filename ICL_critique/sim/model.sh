#!/bin/bash -l

DATADIR=./
COUNTRIES="Austria,Belgium,Denmark,France,Germany,Italy,Norway,Spain,Sweden,Switzerland,United_Kingdom"
STAN_MODEL=./base.stan
DTS=100 #Days to simulate
ED=2020-05-04 #End date, up to which to include data (different depending on forecast)
LI=0
OUTDIR=../results/
./icl_model.py --datadir $DATADIR --countries $COUNTRIES --stan_model $STAN_MODEL --days_to_simulate $DTS --end_date $ED --last_intervention_for_all $LI --outdir $OUTDIR
