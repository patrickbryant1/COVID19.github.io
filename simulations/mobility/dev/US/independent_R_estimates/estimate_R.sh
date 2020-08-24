#!/bin/bash -l

#Format data
# CASES=../../../data/US/us_cases.csv
# MOBILITY_DATA=../../../data/US/Global_Mobility_US.csv
# OUTDIR=./
# ./epiestim_format.py --us_cases $CASES --mobility_data $MOBILITY_DATA --outdir $OUTDIR


#Estimate R using EpiEstim
EPIDATA=./complete_case_df.csv
OUTDIR=/home/pbryant/results/COVID19/mobility_and_spread/US/EpiEstimR/
STATES=./states.txt
time for i in {1..50}
  do
    STATE=$(sed -nr $i'p' $STATES)
    echo $STATE
    /home/pbryant/R-3.6.2/bin/Rscript ./model_R.R $EPIDATA $STATE $OUTDIR
  done

#Join all data
#./join_epiR.py --indir /home/patrick/results/COVID19/mobility_and_spread/US/EpiEstimR/ --outdir ./
