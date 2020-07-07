#!/bin/bash -l

DATADIR=../model_output/R0_2_79/3_week_forecast/19_April/LOO/
EPIDATA=../data/ecdc_20200603.csv
CC=./country_combos_LOO.txt
DTS=84
OUTDIR=../model_output/R0_2_79/3_week_forecast/19_April/

#Visualize LOO
./leave_one_out_analysis.py --datadir $DATADIR --epidemic_data $EPIDATA --country_combos $CC --days_to_simulate $DTS --outdir $OUTDIR
