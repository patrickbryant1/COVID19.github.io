
for COUNTRY in "Denmark" "Italy" "Germany" "Spain" "United_Kingdom" "France" "Norway" "Belgium" "Austria" "Sweden" "Switzerland"
do
  montage $COUNTRY'_cases.png' $COUNTRY'_deaths.png' $COUNTRY'_Rt.png' -tile 3x1 -geometry +2+2 $COUNTRY
done

montage -label '%f' -pointsize 15 "Austria"  "Belgium" "Denmark" "France"  -tile 1x4 -geometry +2+2 'part1.png'
montage -label '%f' -pointsize 15 "Germany" "Italy"  "Norway" "Spain" -tile 1x4 -geometry +2+2 'part2.png'
montage -label '%f' -pointsize 15 "Sweden" "Switzerland" "United_Kingdom"   -tile 1x4 -geometry +2+2 'part3.png'

montage -label '%f' -pointsize 15 "Austria_overlay.png"  "Belgium_overlay.png" "Denmark_overlay.png"  -tile 1x3 -geometry +2+2 'overlay_part1.png'
montage -label '%f' -pointsize 15 "France_overlay.png" "Germany_overlay.png" "Italy_overlay.png"   -tile 1x3 -geometry +2+2 'overlay_part2.png'
montage -label '%f' -pointsize 15  "Norway_overlay.png" "Spain_overlay.png" "Sweden_overlay.png" -tile 1x3 -geometry +2+2 'overlay_part3.png'
montage -label '%f' -pointsize 15  "Switzerland_overlay.png" "United_Kingdom_overlay.png"   -tile 1x2 -geometry +2+2 'overlay_part4.png'
