
#Join country data
for COUNTRY in "Denmark" "Italy" "Germany" "Spain" "United_Kingdom" "France" "Norway" "Belgium" "Austria" "Sweden" "Switzerland"
do
  montage $COUNTRY'_cumulative_cases.png' $COUNTRY'_deaths.png' $COUNTRY'_Rt.png' -tile 3x1 -geometry +2+2 $COUNTRY
done

#Markers
montage "NPI_markers.png" "mobility_markers.png" "foreacast_markers.png" -tile 3x1 -geometry +2+2 "markers.png"
#Montage different countries together
montage -label '%f' -pointsize 15 "markers.png" "Austria"  "Belgium" "Denmark" "France" "Germany" -tile 1x6 -geometry +2+2 'part1.png'
montage -label '%f' -pointsize 15  "Italy" "Norway" "Spain" "Sweden" "Switzerland" "United_Kingdom" -tile 1x6 -geometry +2+2 'part2.png'
#All countries
montage -label '%f' -pointsize 15 "Austria"  "Belgium" "Denmark" "France"   "Germany" "Italy"  "Norway" "Spain" "Sweden" "Switzerland" "United_Kingdom"   -tile 1x11 -geometry +2+2 'mobility_model.png'
montage "markers.png" "mobility_model.png" -tile 1x2 -geometry +2+2 "mobility_model.png"
#Mobility
montage -label '%f' -pointsize 15 "Austria_mobility"  "Belgium_mobility" "Denmark_mobility" "France_mobility"  -tile 2x2 -geometry +2+2 'mobility_1.png'
montage -label '%f' -pointsize 15 "Germany_mobility" "Italy_mobility"  "Norway_mobility" "Spain_mobility" "Sweden_mobility" "Switzerland_mobility" "United_Kingdom_mobility"   -tile 2x4 -geometry +2+2 'mobility_2.png'

#Sweden and Spain together
#montage 'Sweden_cumulative_cases.png' 'Spain_cumulative_cases.png' 'Sweden_deaths.png' 'Spain_deaths.png' 'Sweden_Rt.png' 'Spain_Rt.png' -tile 2x3 -geometry +2+2 'Sweden_Spain.png'
montage -label '%f' -pointsize 15  "Italy" "Sweden" -tile 1x2 -geometry +2+2 'Sweden_Italy.png'
montage 'Sweden_Italy.png' "markers.png" -tile 1x2 -geometry +2+2 'Sweden_Italy.png'

#Forecast
montage forecast/Austria_forecast.svg  forecast/Germany_forecast.svg  forecast/Sweden_forecast.svg forecast/Belgium_forecast.svg  forecast/Italy_forecast.svg    forecast/Switzerland_forecast.svg forecast/Denmark_forecast.svg  forecast/Norway_forecast.svg   forecast/United_Kingdom_forecast.svg forecast/France_forecast.svg   forecast/Spain_forecast.svg -tile 3x4 -geometry +2+2 'forecast.png'
