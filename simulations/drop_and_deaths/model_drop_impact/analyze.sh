#!/usr/bin/env bash
DROPDF=/home/patrick/COVID19.github.io/simulations/drop_and_deaths/initial_analysis/drop_df.csv
WTS=5
OUTDIR=/home/patrick/results/COVID19/drop_and_deaths/simulation_results/
/home/patrick/COVID19.github.io/simulations/drop_and_deaths/model_drop_impact/analyze_simulation.py --drop_df $DROPDF --weeks_to_simulate $WTS --outdir $OUTDIR
