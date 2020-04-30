#!/bin/bash -l

DATADIR=/home/arnee/git/COVID19.github.io/simulations/mobility/data/
COUNTRIES="Stockholm","VästraGötaland","Dalarna","Jönköping","Gävleborg","Skåne","Sörmland","Uppsala","Östergötland"
DTS=104
ED=2020-04-15 #End date, up to which to include data (different depending on forecast)
SD=./model_output/R0_2_79/dev/plots/short_dates.csv
OUTDIR=/home/arnee/git/COVID19.github.io/simulations/mobility/Sweden/${ED}-${DTS}/
mkdir  $OUTDIR/plots
#Visualize model output
python3 /home/arnee/git/COVID19.github.io/simulations/mobility/analysis/visualize_model_output_SE.py --datadir $DATADIR --countries $COUNTRIES --days_to_simulate $DTS --short_dates $SD --outdir $OUTDIR
#Overlay mobility and intervention
#/home/arnee/git/COVID19.github.io/simulations/mobility/mobility_intervention_overlay.py --datadir $DATADIR --outdir $OUTDIR
