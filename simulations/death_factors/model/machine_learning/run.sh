#!/usr/bin/env bash
DATA=../../eda/county/complete_df.csv
SIG_CORR=../../eda/county/sig_feature_corr.csv
OUTDIR=./plots/
./model.py --data $DATA --sig_feature_corr $SIG_CORR --outdir $OUTDIR
