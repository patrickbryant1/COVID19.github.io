
for COUNTRY in "Denmark" "Italy" "Germany" "Spain" "United_Kingdom" "France" "Norway" "Belgium" "Austria" "Sweden" "Switzerland"
do
  montage $COUNTRY'_cases.png' $COUNTRY'_deaths.png' $COUNTRY'_Rt.png' -tile 3x1 -geometry +2+2 $COUNTRY'.png'
done

montage -label '%f' "Denmark.png" "Italy.png" "Germany.png" "Spain.png" "United_Kingdom.png" "France.png" "Norway.png" "Belgium.png" "Austria.png" "Sweden.png" "Switzerland.png" -tile 1x11 -geometry +2+2 'all.png' 
