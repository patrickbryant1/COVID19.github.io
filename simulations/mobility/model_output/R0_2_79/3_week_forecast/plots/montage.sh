
#Join country data
for COUNTRY in "Denmark" "Italy" "Germany" "Spain" "United_Kingdom" "France" "Norway" "Belgium" "Austria" "Sweden" "Switzerland"
do
  montage $COUNTRY'_cumulative_cases.svg' $COUNTRY'_deaths.svg' $COUNTRY'_Rt.svg' -tile 3x1 -geometry +2+2 $COUNTRY
done

#Markers
montage "NPI_markers.svg" "mobility_markers.svg" -tile 2x1 -geometry +2+2 "markers.svg"
#Montage different countries together
montage -label '%f' -pointsize 15 "markers.svg" "Austria"  "Belgium" "Denmark" "France" "Germany" -tile 1x6 -geometry +2+2 'part1.svg'
montage -label '%f' -pointsize 15  "Italy" "Norway" "Spain" "Sweden" "Switzerland" "United_Kingdom" -tile 1x6 -geometry +2+2 'part2.svg'
#All countries
montage -label '%f' -pointsize 15 "Austria"  "Belgium" "Denmark" "France"   "Germany" "Italy"  "Norway" "Spain" "Sweden" "Switzerland" "United_Kingdom"   -tile 1x11 -geometry +2+2 'mobility_model.svg'
montage "markers.svg" "mobility_model.svg" -tile 1x2 -geometry +2+2 "mobility_model.svg"
#Mobility
montage -label '%f' -pointsize 15 "Austria_mobility"  "Belgium_mobility" "Denmark_mobility" "France_mobility"  -tile 2x2 -geometry +2+2 'mobility_1.svg'
montage -label '%f' -pointsize 15 "Germany_mobility" "Italy_mobility"  "Norway_mobility" "Spain_mobility" "Sweden_mobility" "Switzerland_mobility" "United_Kingdom_mobility"   -tile 2x4 -geometry +2+2 'mobility_2.svg'

#Sweden and Spain together
#montage 'Sweden_cumulative_cases.svg' 'Spain_cumulative_cases.svg' 'Sweden_deaths.svg' 'Spain_deaths.svg' 'Sweden_Rt.svg' 'Spain_Rt.svg' -tile 2x3 -geometry +2+2 'Sweden_Spain.svg'
montage -label '%f' -pointsize 15 "Sweden" "Spain" -tile 1x2 -geometry +2+2 'Sweden_Spain.svg'
montage 'Sweden_Spain.svg' "markers.svg" -tile 1x2 -geometry +2+2 'Sweden_Spain.svg'
montage -label '%f' -pointsize 15 "Spain_mobility" "Sweden_mobility"  -tile 2x2 -geometry +2+2 'Sweden_Spain_mobility.svg'

#Forecast
montage forecast  forecast/Austria_forecast.svg  forecast/Germany_forecast.svg  forecast/Sweden_forecast.svg forecast/Belgium_forecast.svg  forecast/Italy_forecast.svg    forecast/Switzerland_forecast.svg forecast/Denmark_forecast.svg  forecast/Norway_forecast.svg   forecast/United_Kingdom_forecast.svg forecast/France_forecast.svg   forecast/Spain_forecast.svg -tile 3x4 -geometry +2+2 'forecast.svg'
