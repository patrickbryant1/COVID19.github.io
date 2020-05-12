#!/bin/bash -l

DATADIR=../data/
COUNTRIES="Sweden"
#SUBREGIONS="Blekinge,Dalarna,Gotland,Gävleborg,Halland,JämtlandHärjedalen,Jönköping,Kalmar,Kronoberg,Norrbotten,Skåne,Stockholm,Sörmland,Uppsala,Värmland,Västerbotten,Västernorrland,Västmanland,VästraGötaland,Örebro,Östergötland"
SUBREGIONS="Dalarna,Gävleborg,Halland,JämtlandHärjedalen,Jönköping,Kalmar,Kronoberg,Norrbotten,Skåne,Stockholm,Sörmland,Uppsala,Värmland,Västerbotten,Västernorrland,Västmanland,VästraGötaland,Örebro,Östergötland"

POP_DATA=$DATADIR'Sweden/county_pop.csv'
EPI_DATA=$DATADIR'Sweden/FHM-2020-05-01.csv'
STAN_MODEL=./mobility_herd.stan
OUTDIR=../model_output/R0_2_79/dev/
ED=2020-05-05 #End date, up to which to include data (different depending on forecast)
DTS=106
./dev_subregions.py --datadir $DATADIR --countries $COUNTRIES --subregions $SUBREGIONS --population_data $POP_DATA --epidemic_data $EPI_DATA --stan_model $STAN_MODEL --days_to_simulate $DTS --end_date $ED --outdir $OUTDIR
