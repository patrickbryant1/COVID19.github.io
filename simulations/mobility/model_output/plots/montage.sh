
for COUNTRY in "Denmark" "Italy" "Germany" "Spain" "United_Kingdom" "France" "Norway" "Belgium" "Austria" "Sweden" "Switzerland"
do
  montage $COUNTRY'_cases.png' $COUNTRY'_deaths.png' $COUNTRY'_Rt.png' -tile 3x1 -geometry +2+2 $COUNTRY'.png'
done

montage -label '%f' "Austria.png"  "Belgium.png" "Denmark.png" "France.png"  -tile 1x4 -geometry +2+2 'part1.png'
montage -label '%f' "Germany.png" "Italy.png"  "Norway.png" "Spain.png" -tile 1x4 -geometry +2+2 'part2.png'
montage -label '%f' "Sweden.png" "Switzerland.png" "United_Kingdom.png"   -tile 1x4 -geometry +2+2 'part3.png' 
