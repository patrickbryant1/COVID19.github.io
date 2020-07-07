#!/usr/bin/env bash
EPIDATA=../data/ecdc_20200603.csv
OUTDIR=../model_output/R0_2_79/3_week_forecast/19_April/EpiEstim/
COUNTRIES=./countries.txt
time for i in {1..11}
  do
    COUNTRY=$(sed -nr $i'p' $COUNTRIES)
    echo $COUNTRY
    Rscript ./model_R.R $EPIDATA $COUNTRY $OUTDIR
  done
