#!/bin/bash -l

DATADIR=/home/patrick/COVID19.github.io/simulations/mobility/data/
OUTDIR=/home/patrick/COVID19.github.io/simulations/mobility/model_output/R0_2_79/
COUNTRIES="Austria,Belgium,Denmark,France,Germany,Italy,Norway,Spain,Sweden,Switzerland,United_Kingdom"
DTS=84
#Visualize model output
/home/patrick/COVID19.github.io/simulations/mobility/visualize_model_output.py --datadir $DATADIR --countries $COUNTRIES --days_to_simulate $DTS --outdir $OUTDIR
#Overlay mobility and intervention
#/home/patrick/COVID19.github.io/simulations/mobility/mobility_intervention_overlay.py --datadir $DATADIR --outdir $OUTDIR
