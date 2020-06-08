#!/usr/bin/env bash

EPIDATA=/home/patrick/COVID19.github.io/simulations/mobility/data/ecdc_20200603.csv
MOBDATA=/home/patrick/COVID19.github.io/simulations/mobility/data/Global_Mobility_Report.csv
OUTDIR=/home/patrick/results/COVID19/mobility_and_spread/
/home/patrick/COVID19.github.io/simulations/mobility_and_spread/mobility_vs_case_change.py --epidemic_data $EPIDATA --mobility_data $MOBDATA --outdir $OUTDIR
