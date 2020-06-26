#!/usr/bin/env bash
EPIDATA=../data/Deaths_involving_coronavirus_disease_2019__COVID-19__by_race_and_Hispanic_origin_group_and_age__by_state.csv
COMORBIDITY=../data/Conditions_contributing_to_deaths_involving_coronavirus_disease_2019__COVID-19___by_age_group__United_States.csv
AGE_ETHNICITY=../data/DP05.csv
OUTDIR=./plots/
./analyze_death.py --epidemic_data $EPIDATA --comorbidity $COMORBIDITY --age_ethnicity_data $AGE_ETHNICITY --outdir $OUTDIR
