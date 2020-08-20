#!/bin/bash -l

DATADIR=../sim/
RESULT="../results/"
OUTDIR='./posterior_overlay/'
COUNTRIES="Austria,Belgium,Denmark,France,Germany,Italy,Norway,Spain,Sweden,Switzerland,United_Kingdom" #Make sure these are in the same order as when simulating!
DTS=100
ED='2020-05-04'
SD=./short_dates.csv
#Visualize model output
./overlay_posteriors.py --datadir $DATADIR --results_dir $RESULT --countries $COUNTRIES --days_to_simulate $DTS --end_date $ED --short_dates $SD --outdir $OUTDIR
