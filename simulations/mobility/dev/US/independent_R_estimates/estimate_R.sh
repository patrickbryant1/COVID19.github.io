#!/bin/bash -l

#Format data
CASES=../../../data/US/us_cases.csv
MOBILITY_DATA=../../../data/Global_Mobility_Report.csv
OUTDIR=./
./epiestim_format.py --us_cases $CASES --mobility_data $MOBILITY_DATA --outdir $OUTDIR


#Estimate R using EpiEstim
EPIDATA=./complete_case_df.csv
OUTDIR=/home/patrick/results/COVID19/mobility_and_spread/US/EpiEstimR/
STATES=./states.txt
time for i in {1..50}
  do
    STATE=$(sed -nr $i'p' $STATES)
    echo $STATE
    Rscript ./model_R.R $EPIDATA $STATE $OUTDIR
  done
