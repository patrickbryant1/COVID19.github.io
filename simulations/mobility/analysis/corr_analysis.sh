#!/bin/bash -l

DATADIR=/home/patrick/COVID19.github.io/simulations/mobility/data/
OUTDIR=/home/patrick/COVID19.github.io/simulations/mobility/model_output/R0_2_79/3_week_forecast/19_April/
COUNTRIES="Austria,Belgium,Denmark,France,Germany,Italy,Norway,Spain,Sweden,Switzerland,United_Kingdom" #Make sure these are in the same order as when simulating!
DTS=105
ED='2020-04-19'
#Visualize model output
./analyze_death_corr.py --datadir $DATADIR --countries $COUNTRIES --days_to_simulate $DTS --end_date $ED --outdir $OUTDIR
