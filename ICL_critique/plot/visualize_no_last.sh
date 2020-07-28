#!/bin/bash -l

DATADIR=../sim/
RESULTS=../results/no_last/
OUTDIR=./no_last/
COUNTRIES="Austria,Belgium,Denmark,France,Germany,Italy,Norway,Spain,Sweden,Switzerland,United_Kingdom" #Make sure these are in the same order as when simulating!
DTS=100
ED='2020-05-04'
SD=./short_dates.csv
#Visualize model output
./visualize_model_output.py --datadir $DATADIR --results_dir $RESULTS --countries $COUNTRIES --days_to_simulate $DTS --end_date $ED --short_dates $SD --outdir $OUTDIR
