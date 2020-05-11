#!/bin/bash -l

DATADIR=../data/
COUNTRIES="Sweden"
SUBREGIONS="Blekinge_County,Dalarna_County,Gavleborg_County,Gotland_County,Halland_County,Jamtland_County,Jonkoping_County,Kalmar_County,Kronoberg_County,Norrbotten_County,Örebro_County,Östergötland_County,Skåne_County,Södermanland_County,Stockholm_County,Uppsala_County,Varmland_County,Västerbotten_County,Västernorrland_County,Västmanland_County,Västra_Götaland_County"
POP_DATA=$DATADIR'Sweden/county_pop.csv'
EPI_DATA=$DATADIR'Sweden/FHM-2020-05-01.csv'
STAN_MODEL=./mobility_herd.stan
OUTDIR=../model_output/R0_2_79/dev/
ED=2020-05-05 #End date, up to which to include data (different depending on forecast)
DTS=106
./dev_subregions.py --datadir $DATADIR --countries $COUNTRIES --subregions $SUBREGIONS --population_data $POP_DATA --epidemic_data $EPI_DATA --stan_model $STAN_MODEL --days_to_simulate $DTS --end_date $ED --outdir $OUTDIR
