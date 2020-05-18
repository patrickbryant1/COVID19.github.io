#!/usr/bin/env bash

RDIR=/home/patrick/results/COVID19/R_estimates/
EPIDATA=/home/patrick/COVID19.github.io/simulations/mobility/data/ecdc_20200505.csv
MOBDATA=/home/patrick/COVID19.github.io/simulations/mobility/data/Global_Mobility_Report.csv
OUTDIR=/home/patrick/results/COVID19/signal_corr/
/home/patrick/COVID19.github.io/simulations/mobility_signal/construct_signals.py --R_estimates $RDIR --epidemic_data $EPIDATA --mobility_data $MOBDATA --outdir $OUTDIR
