#!/bin/bash -l


DATADIR=/home/patrick/COVID19.github.io/simulations/mobility/data/
OUTDIR=/home/patrick/COVID19.github.io/simulations/mobility/model_output/R0_2_79/3_week_forecast/
COUNTRIES="Austria,Belgium,Denmark,France,Germany,Italy,Norway,Spain,Sweden,Switzerland,United_Kingdom" #Make sure these are in the same order as when simulating!
DTS=84
ED=2020-04-12
SD=$OUTDIR'/plots/short_dates.csv'
#Visualize model output
#1.Obtain forecast in terms of the mean number of deaths and write to csv
/home/patrick/COVID19.github.io/simulations/mobility/analysis/forecast_analysis.py --datadir $DATADIR --countries $COUNTRIES --days_to_simulate $DTS --end_date $ED --outdir $OUTDIR
#2.Plot
FORECAST_CSV=$OUTDIR'forecast.csv'
OUTDIR=$OUTDIR'/plots/forecast/'
WTF=3 #Number of weeks to forecast
/home/patrick/COVID19.github.io/simulations/mobility/analysis/plot_forecast_per_country.py --forecast_csv $FORECAST_CSV --countries $COUNTRIES --weeks_to_forecast $WTF --outdir $OUTDIR
