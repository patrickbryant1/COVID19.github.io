#!/bin/bash -l

ECDC_CSV=/home/patrick/COVID19.github.io/ecdc/20200331.csv
WB_DATA=/home/patrick/COVID19.github.io/worldbank/
OUTDIR=/home/patrick/COVID19.github.io/docs/assets/

/home/patrick/COVID19.github.io/visualize/plot_ecdc.py --ecdc_csv $ECDC_CSV --wb_data $WB_DATA --outdir $OUTDIR
