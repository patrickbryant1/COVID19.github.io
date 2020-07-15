
#Join country data
for COUNTRY in "Denmark" "Italy" "Germany" "Spain" "United_Kingdom" "France" "Norway" "Belgium" "Austria" "Sweden" "Switzerland"
do
  montage $COUNTRY'_cumulative_cases.png' $COUNTRY'_deaths.png' $COUNTRY'_Rt.png' -tile 3x1 -geometry +2+2 $COUNTRY
done

#Markers
montage "NPI_markers.png" "mobility_markers.png" "foreacast_markers.png" -tile 3x1 -geometry +2+2 "markers.png"
#Montage different countries together
montage  "markers.png" "Austria"  "Belgium" "Denmark" "France"  -tile 1x5 -geometry +2+2 'part1.png'
montage  "Germany" "Italy" "Norway" "Spain" "Sweden" -tile 1x5 -geometry +2+2 'part2.png'
montage  "Switzerland" "United_Kingdom" -tile 1x2 -geometry +2+2 'part3.png'

#Sweden and Italy together
montage   "Italy" "Sweden" -tile 1x2 -geometry +2+2 'Sweden_Italy.png'
montage 'Sweden_Italy.png' "markers.png" -tile 1x2 -geometry +2+2 'Sweden_Italy.png'

#Forecast
montage forecast/Austria_forecast.png  forecast/Germany_forecast.png  forecast/Sweden_forecast.png forecast/Belgium_forecast.png  forecast/Italy_forecast.png    forecast/Switzerland_forecast.png forecast/Denmark_forecast.png  forecast/Norway_forecast.png   forecast/United_Kingdom_forecast.png forecast/France_forecast.png   forecast/Spain_forecast.png -tile 3x4 -geometry +2+2 'forecast.png'

#Montage posterior distributions
montage 'posterior/alpha_retail and recreation.png' 'posterior/alpha_grocery and pharmacy.png' 'posterior/alpha_transit stations.png' posterior/alpha_workplace.png posterior/alpha_residential.png -tile 3x2 -geometry +2+2 posterior/alphas.png
montage 'posterior/mean R0*' -tile 6x2 -geometry +2+2 posterior/meanR0_all.png
#Montage correlations
montage 'correlations/retail_and_recreation_percent_change_from_baseline.png' 'correlations/grocery_and_pharmacy_percent_change_from_baseline.png' 'correlations/transit_stations_percent_change_from_baseline.png' correlations/workplaces_percent_change_from_baseline.png correlations/residential_percent_change_from_baseline.png -tile 3x2 -geometry +2+2 correlations/all_corr.png

#Montage EpiEstim and mobility R estimate comparison
montage "EpiEstim/Austria.png" "EpiEstim/Belgium.png" "EpiEstim/Denmark.png" "EpiEstim/France.png" "EpiEstim/Germany.png" "EpiEstim/Italy.png" "EpiEstim/Norway.png" "EpiEstim/Spain.png" "EpiEstim/Sweden.png" "EpiEstim/Switzerland.png" "EpiEstim/United_Kingdom.png" -tile 3x4 -geometry +2+2 EpiEstim/all.png

#Montage posterior distributions for LOO analysis
montage "LOO/Austria_0.png" "LOO/Belgium_0.png" "LOO/Denmark_0.png" "LOO/France_0.png" "LOO/Germany_0.png" "LOO/Italy_0.png" "LOO/Norway_0.png" "LOO/Spain_0.png" "LOO/Sweden_0.png" "LOO/Switzerland_0.png" "LOO/United_Kingdom_0.png" -tile 6x2 -geometry +2+2 LOO/all_retail.png
montage "LOO/Austria_1.png" "LOO/Belgium_1.png" "LOO/Denmark_1.png" "LOO/France_1.png" "LOO/Germany_1.png" "LOO/Italy_1.png" "LOO/Norway_1.png" "LOO/Spain_1.png" "LOO/Sweden_1.png" "LOO/Switzerland_1.png" "LOO/United_Kingdom_1.png" -tile 6x2 -geometry +2+2 LOO/all_grocery.png
montage "LOO/Austria_2.png" "LOO/Belgium_2.png" "LOO/Denmark_2.png" "LOO/France_2.png" "LOO/Germany_2.png" "LOO/Italy_2.png" "LOO/Norway_2.png" "LOO/Spain_2.png" "LOO/Sweden_2.png" "LOO/Switzerland_2.png" "LOO/United_Kingdom_2.png" -tile 6x2 -geometry +2+2 LOO/all_transit.png
montage "LOO/Austria_3.png" "LOO/Belgium_3.png" "LOO/Denmark_3.png" "LOO/France_3.png" "LOO/Germany_3.png" "LOO/Italy_3.png" "LOO/Norway_3.png" "LOO/Spain_3.png" "LOO/Sweden_3.png" "LOO/Switzerland_3.png" "LOO/United_Kingdom_3.png" -tile 6x3 -geometry +3+3 LOO/all_work.png
montage "LOO/Austria_4.png" "LOO/Belgium_4.png" "LOO/Denmark_4.png" "LOO/France_4.png" "LOO/Germany_4.png" "LOO/Italy_4.png" "LOO/Norway_4.png" "LOO/Spain_4.png" "LOO/Sweden_4.png" "LOO/Switzerland_4.png" "LOO/United_Kingdom_4.png" -tile 6x4 -geometry +4+4 LOO/all_residential.png
montage LOO/all_retail.png LOO/all_grocery.png LOO/all_transit.png LOO/all_work.png LOO/all_residential.png -tile 1x5 -geometry +2+2 LOO/all_mob.png
