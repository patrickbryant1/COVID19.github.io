
#Join country data
for COUNTRY in "Sweden"
do
  montage $COUNTRY'_cumulative_cases.png' $COUNTRY'_deaths.png' $COUNTRY'_Rt.png' -tile 3x1 -geometry +2+2 $COUNTRY
  montage $COUNTRY'_cumulative_cases_all.png' $COUNTRY'_deaths_all.png' -tile 2x1 -geometry +2+2 $COUNTRY'_All'
done

#Markers
montage "NPI_markers.png" "mobility_markers.png" "foreacast_markers.png" -tile 3x1 -geometry +2+2 "markers.png"

#Together
montage  "markers.png" 'Sweden' 'Sweden_All' -tile 1x3 -geometry +2+2 'Sweden_complete.png'
