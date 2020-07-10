#!/usr/bin/env bash
COUNTY_DEATHS=../../data/county_level/covid_deaths_usafacts.csv
STATE_DEATHS=../../data/state_level/Deaths_involving_coronavirus_disease_2019__COVID-19__by_race_and_Hispanic_origin_group_and_age__by_state.csv
PEOPLE=/home/patrick/data/COVID19/death_factors/tract/nhgis0001_csv/nhgis0001_ds239_20185_2018_tract.csv #Aavailable upon request from NHGIS
OUTDIR=./
./format_data.py --county_deaths $COUNTY_DEATHS --state_deaths $STATE_DEATHS --people $PEOPLE --outdir $OUTDIR
