#!/bin/bash -l

DATADIR=/home/patrick/COVID19.github.io/simulations/icl_model/data/
OUTDIR=/home/patrick/COVID19.github.io/simulations/mobility/model_output/

/home/patrick/COVID19.github.io/simulations/mobility/mobility_model.py --datadir $DATADIR --outdir $OUTDIR
