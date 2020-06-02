#!/usr/bin/env bash

EPIDATA=/home/patrick/COVID19.github.io/simulations/mobility/data/ecdc_20200521.csv
MOBDATA=/home/patrick/COVID19.github.io/simulations/mobility/data/Global_Mobility_Report.csv
DROPDATES=/home/patrick/COVID19.github.io/simulations/drop_and_deaths/initial_analysis/drop_dates.csv
OUTDIR=/home/patrick/results/COVID19/drop_and_deaths/
/home/patrick/COVID19.github.io/simulations/drop_and_deaths/initial_analysis/analyze_drop.py --epidemic_data $EPIDATA --mobility_data $MOBDATA --drop_dates $DROPDATES --outdir $OUTDIR
