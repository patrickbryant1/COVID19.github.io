#!/bin/bash -l

EPIESTIMDIR=../model_output/R0_2_79/3_week_forecast/19_April/EpiEstim/
STAN_RESULTS=../model_output/R0_2_79/3_week_forecast/19_April/summary.csv
OUTDIR=../model_output/R0_2_79/3_week_forecast/19_April/plots/EpiEstim/
COUNTRIES="Austria,Belgium,Denmark,France,Germany,Italy,Norway,Spain,Sweden,Switzerland,United_Kingdom" #Make sure these are in the same order as when simulating!
DTS=84
ED='2020-04-19'
SD=$OUTDIR'/plots/short_dates.csv'
#Visualize model output
./compare_R_estimates.py --EpiEstimdir $EPIESTIMDIR --stan_results $STAN_RESULTS --countries $COUNTRIES --days_to_simulate $DTS --end_date $ED --short_dates $SD --outdir $OUTDIR
