
for COUNTRY in "Denmark" "Italy" "Germany" "Spain" "United_Kingdom" "France" "Norway" "Belgium" "Austria" "Sweden" "Switzerland"
do
  montage $COUNTRY'_cumulative_cases.png' $COUNTRY'_deaths.png' $COUNTRY'_Rt.png' -tile 3x1 -geometry +2+2 $COUNTRY
done


montage -label '%f' -pointsize 15 "Austria"  "Belgium" "Denmark" "France"  -tile 1x4 -geometry +2+2 'part1.png'
montage -label '%f' -pointsize 15 "Germany" "Italy"  "Norway" "Spain" -tile 1x4 -geometry +2+2 'part2.png'
montage -label '%f' -pointsize 15 "Sweden" "Switzerland" "United_Kingdom"   -tile 1x4 -geometry +2+2 'part3.png'

montage -label '%f' -pointsize 15 "Austria"  "Belgium" "Denmark" "France"   "Germany" "Italy"  "Norway" "Spain" "Sweden" "Switzerland" "United_Kingdom"   -tile 1x11 -geometry +2+2 'mobility_model.png'

#Mobility
montage -label '%f' -pointsize 15 "Austria_mobility"  "Belgium_mobility" "Denmark_mobility" "France_mobility"  -tile 2x2 -geometry +2+2 'mobility_1.png'
montage -label '%f' -pointsize 15 "Germany_mobility" "Italy_mobility"  "Norway_mobility" "Spain_mobility" "Sweden_mobility" "Switzerland_mobility" "United_Kingdom_mobility"   -tile 2x4 -geometry +2+2 'mobility_2.png'

#Sweden and Spain together
montage -label '%f' -pointsize 15 "Sweden" "Spain"  -tile 1x2 -geometry +2+2 'Sweden_Spain.png'
montage -label '%f' -pointsize 15 "Spain_mobility" "Sweden_mobility"  -tile 2x2 -geometry +2+2 'Sweden_Spain_mobility.png'
