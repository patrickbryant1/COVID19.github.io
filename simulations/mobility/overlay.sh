#!/bin/bash -l

DATADIR=/home/patrick/COVID19.github.io/simulations/mobility/data/
OUTDIR=/home/patrick/COVID19.github.io/simulations/mobility/model_output/R0_2_79/

/home/patrick/COVID19.github.io/simulations/mobility/mobility_intervention_overlay.py --datadir $DATADIR --outdir $OUTDIR
