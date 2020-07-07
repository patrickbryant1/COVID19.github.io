#!/bin/bash -l

EPIESTIMDIR=../model_output/R0_2_79/3_week_forecast/19_April/EpiEstim/
STAN_RESULTS=../model_output/R0_2_79/3_week_forecast/19_April/summary.csv
OUTDIR=../model_output/R0_2_79/3_week_forecast/19_April/plots/EpiEstim/
CM=./country_meta.csv #Country meta data
ED='2020-04-19'
SD='../model_output/R0_2_79/3_week_forecast/19_April/plots/short_dates.csv'
#Visualize model output
./compare_R_estimates.py --EpiEstimdir $EPIESTIMDIR --stan_results $STAN_RESULTS --country_meta $CM --end_date $ED --short_dates $SD --outdir $OUTDIR
