#!/bin/bash -x


DATADIR=/home/arnee/git/COVID19.github.io/simulations/mobility/data/
COUNTRIES="Stockholm","VästraGötaland","Dalarna","Jönköping","Gävleborg","Skåne","Sörmland","Uppsala","Östergötland"
DTS=104
ED=2020-04-15
OUTDIR=/home/arnee/git/COVID19.github.io/simulations/mobility/Sweden/${ED}-${DTS}/
#VID19.github.io/simulations/mobility/model_output/R0_2_79/3_week_forecast/
#SD=$OUTDIR'/plots/short_dates.csv'
SD=./model_output/R0_2_79/dev/plots/short_dates.csv
mkdir -p $OUTDIR/plots/forecast
#Visualize model output
#1.Obtain forecast in terms of the mean number of deaths and write to csv
python3 /home/arnee/git/COVID19.github.io/simulations/mobility/analysis/forecast_analysis_SE.py --datadir $DATADIR --countries $COUNTRIES --days_to_simulate $DTS --end_date $ED --outdir $OUTDIR
#2.Plot
FORECAST_CSV=$OUTDIR/'forecast.csv'
OUTDIR=$OUTDIR'/plots/forecast/'
WTF=3 #Number of weeks to forecast
python3 /home/arnee/git/COVID19.github.io/simulations/mobility/analysis/plot_forecast_per_country_SE.py --forecast_csv $FORECAST_CSV --countries $COUNTRIES --weeks_to_forecast $WTF --outdir $OUTDIR
