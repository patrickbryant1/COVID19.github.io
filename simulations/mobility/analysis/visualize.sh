#!/bin/bash -l

DATADIR=/home/patrick/COVID19.github.io/simulations/mobility/data/
OUTDIR=/home/patrick/COVID19.github.io/simulations/mobility/model_output/R0_2_79/3_week_forecast/
COUNTRIES="Austria,Belgium,Denmark,France,Germany,Italy,Norway,Spain,Sweden,Switzerland,United_Kingdom" #Make sure these are in the same order as when simulating!
DTS=84
SD=$OUTDIR'/plots/short_dates.csv'
#Visualize model output
/home/patrick/COVID19.github.io/simulations/mobility/analysis/visualize_model_output.py --datadir $DATADIR --countries $COUNTRIES --days_to_simulate $DTS --short_dates $SD --outdir $OUTDIR
#Overlay mobility and intervention
#/home/patrick/COVID19.github.io/simulations/mobility/mobility_intervention_overlay.py --datadir $DATADIR --outdir $OUTDIR
