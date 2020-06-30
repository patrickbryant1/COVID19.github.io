#!/usr/bin/env bash
DATA=../eda/county/complete_df.csv
OUTDIR=./plots/
./enet.py --data $DATA --outdir $OUTDIR
