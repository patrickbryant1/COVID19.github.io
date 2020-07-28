montage posterior/alpha_schools_universities.png posterior/alpha_self_isolating_if_ill.png posterior/alpha_public_events.png posterior/alpha_lockdown.png posterior/alpha_social_distancing_encouraged.png posterior/last_intervention.png  -tile 3x2 -geometry +2+2 posterior/alphas.png

#Join country data
for COUNTRY in "Denmark" "Italy" "Germany" "Spain" "United_Kingdom" "France" "Norway" "Belgium" "Austria" "Sweden" "Switzerland"
do
  montage $COUNTRY'_cases.png' $COUNTRY'_deaths.png' $COUNTRY'_Rt.png' -tile 3x1 -geometry +2+2 $COUNTRY
done

#Montage different countries together
montage  "Austria"  "Belgium" "Denmark" "France" "Germany" "Italy" "Norway" "Spain" "Sweden" "Switzerland" "United_Kingdom" -tile 1x11 -geometry +2+2 'all_no_last.png'

#Montage lockdown posteriors of different countries together
montage  "posterior/Austria_lockdown.png"  "posterior/Belgium_lockdown.png" "posterior/Denmark_lockdown.png" "posterior/France_lockdown.png" "posterior/Germany_lockdown.png" "posterior/Italy_lockdown.png" "posterior/Norway_lockdown.png" "posterior/Spain_lockdown.png"  "posterior/Switzerland_lockdown.png" "posterior/United_Kingdom_lockdown.png" -tile 4x3 -geometry +2+2 'posterior/lockdown.png'

montage posterior/alpha_schools_universities.png posterior/alpha_self_isolating_if_ill.png posterior/alpha_public_events.png posterior/alpha_lockdown.png posterior/alpha_social_distancing_encouraged.png  -tile 3x2 -geometry +2+2 posterior/alphas.png
