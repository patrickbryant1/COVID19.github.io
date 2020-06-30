#!/usr/bin/env bash
EPIDATA=../../data/county_level/covid_deaths_usafacts.csv
SEX_ETH_AGE=/home/patrick/data/COVID19/death_factors/cc-est_only2019-alldata.csv #From US census (estimates)
PEOPLE=../../data/county_level/People.csv
INCOME=../../data/county_level/Income.csv
JOBS=../../data/county_level/Jobs.csv
OUTDIR=./plots/
./analyze_death.py --epidemic_data $EPIDATA --sex_eth_age_data $SEX_ETH_AGE --people $PEOPLE --income $INCOME --jobs $JOBS --outdir $OUTDIR
