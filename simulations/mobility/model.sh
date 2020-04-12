#!/bin/bash -l

DATADIR=/home/patrick/COVID19.github.io/simulations/mobility/data/
OUTDIR=/home/patrick/COVID19.github.io/simulations/mobility/model_output/R0_3_28/

/home/patrick/COVID19.github.io/simulations/mobility/mobility_model.py --datadir $DATADIR --outdir $OUTDIR
