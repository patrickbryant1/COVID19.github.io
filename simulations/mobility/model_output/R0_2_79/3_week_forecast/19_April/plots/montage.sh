
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
montage forecast/Austria_forecast.svg  forecast/Germany_forecast.svg  forecast/Sweden_forecast.svg forecast/Belgium_forecast.svg  forecast/Italy_forecast.svg    forecast/Switzerland_forecast.svg forecast/Denmark_forecast.svg  forecast/Norway_forecast.svg   forecast/United_Kingdom_forecast.svg forecast/France_forecast.svg   forecast/Spain_forecast.svg -tile 3x4 -geometry +2+2 'forecast.png'
