
#Join country data
for COUNTRY in "Denmark" "Italy" "Germany" "Spain" "United_Kingdom" "France" "Norway" "Belgium" "Austria" "Sweden" "Switzerland"
do
  montage $COUNTRY'_cumulative_cases.png' $COUNTRY'_deaths.png' $COUNTRY'_Rt.png' -tile 3x1 -geometry +2+2 $COUNTRY
done

#Markers
montage "NPI_markers.png" "mobility_markers.png" -tile 2x1 -geometry +2+2 "markers.png"
#All countries
montage -label '%f' -pointsize 15 "Austria"  "Belgium" "Denmark" "France"   "Germany" "Italy"  "Norway" "Spain" "Sweden" "Switzerland" "United_Kingdom"   -tile 1x11 -geometry +2+2 'mobility_model.png'
montage "markers.png" "mobility_model.png" -tile 1x2 -geometry +2+2 "mobility_model.png"
