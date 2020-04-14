#!/bin/bash -l

DATADIR=/home/patrick/COVID19.github.io/simulations/mobility/data/
COUNTRIES="Austria,Belgium,Denmark,France,Germany,Italy,Norway,Spain,Sweden,Switzerland,United_Kingdom"
OUTDIR=/home/patrick/COVID19.github.io/simulations/mobility/model_output/R0_2_79/

/home/patrick/COVID19.github.io/simulations/mobility/mobility_model.py --datadir $DATADIR --countries $COUNTRIES --outdir $OUTDIR
