
#Join country data
for COUNTRY in "Denmark" "Norway" "Sweden"
do
  montage $COUNTRY'_cumulative_cases.png' $COUNTRY'_deaths.png' $COUNTRY'_Rt.png' -tile 3x1 -geometry +2+2 $COUNTRY
done

#Markers
montage "NPI_markers.png" "mobility_markers.png" "foreacast_markers.png" -tile 3x1 -geometry +2+2 "markers.png"
#Montage different countries together
montage -label '%f' -pointsize 15 "markers.png" "Denmark" "Norway" "Sweden" -tile 1x4 -geometry +2+2 'Scandinavia.png'
