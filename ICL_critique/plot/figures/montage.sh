#Join country data
for COUNTRY in "Denmark" "Italy" "Germany" "Spain" "United_Kingdom" "France" "Norway" "Belgium" "Austria" "Sweden" "Switzerland"
do
  montage $COUNTRY'_cases.png' $COUNTRY'_deaths.png' $COUNTRY'_Rt.png' -tile 3x1 -geometry +2+2 $COUNTRY
done

#Montage different countries together
montage  "Austria"  "Belgium" "Denmark" "France" "Germany" "Italy" "Norway" "Spain" "Sweden" "Switzerland" "United_Kingdom" -tile 1x11 -geometry +2+2 'all.png'
