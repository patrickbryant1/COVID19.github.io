#!/usr/bin/env bash
EPIDATA=../../data/county_level/covid_deaths_usafacts.csv
SEX_ETH_AGE=/home/patrick/data/COVID19/death_factors/cc-est_only2019-alldata.csv #From US census (estimates)
OUTDIR=./plots/
./analyze_death.py --epidemic_data $EPIDATA --sex_eth_age_data $SEX_ETH_AGE --outdir $OUTDIR
