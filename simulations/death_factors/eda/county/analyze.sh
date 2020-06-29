#!/usr/bin/env bash
EPIDATA=../data/Deaths_involving_coronavirus_disease_2019__COVID-19__by_race_and_Hispanic_origin_group_and_age__by_state.csv
SEX_ETH_AGE=/home/patrick/data/COVID19/death_factors/cc-est_only2019-alldata.csv #From US census (estimates)
OUTDIR=./plots/
./analyze_death.py --epidemic_data $EPIDATA --comorbidity $COMORBIDITY --sex_eth_age_data $SEX_ETH_AGE --outdir $OUTDIR
