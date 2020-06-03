#!/usr/bin/env bash

EPIDATA=/home/patrick/COVID19.github.io/simulations/mobility/data/ecdc_20200603.csv
MOBDATA=/home/patrick/COVID19.github.io/simulations/mobility/data/Global_Mobility_Report.csv
DROPSTARTS=/home/patrick/COVID19.github.io/simulations/drop_and_deaths/ml_model/drop_starts.csv
OUTDIR=/home/patrick/results/COVID19/drop_and_deaths/
/home/patrick/COVID19.github.io/simulations/drop_and_deaths/ml_model/predict_deaths.py --epidemic_data $EPIDATA --mobility_data $MOBDATA --drop_starts $DROPSTARTS --outdir $OUTDIR
