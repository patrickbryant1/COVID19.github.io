#Join country data
for COUNTRY in "Denmark" "Italy" "Germany" "Spain" "United_Kingdom" "France" "Norway" "Belgium" "Austria" "Sweden" "Switzerland"
do
  montage $COUNTRY'_cases.png' $COUNTRY'_deaths.png' $COUNTRY'_Rt.png' -tile 3x1 -geometry +2+2 $COUNTRY
done

#Montage different countries together
montage  "Austria"  "Belgium" "Denmark" "France" "Germany" "Italy" "Norway" "Spain" "Sweden" "Switzerland" "United_Kingdom" -tile 1x11 -geometry +2+2 'all.png'

#Montage different countries together
montage  "posterior/Austria_lockdown.png"  "posterior/Belgium_lockdown.png" "posterior/Denmark_lockdown.png" "posterior/France_lockdown.png" "posterior/Germany_lockdown.png" "posterior/Italy_lockdown.png" "posterior/Norway_lockdown.png" "posterior/Spain_lockdown.png"  "posterior/Switzerland_lockdown.png" "posterior/United_Kingdom_lockdown.png" -tile 4x3 -geometry +2+2 'posterior/lockdown.png'
