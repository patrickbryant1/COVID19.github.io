montage posterior/alpha_schools_universities.png posterior/alpha_self_isolating_if_ill.png posterior/alpha_public_events.png posterior/alpha_lockdown.png posterior/alpha_social_distancing_encouraged.png posterior/last_intervention.png  -tile 3x2 -geometry +2+2 posterior/alphas.png

#Join country data
for COUNTRY in "Denmark" "Italy" "Germany" "Spain" "United_Kingdom" "France" "Norway" "Belgium" "Austria" "Sweden" "Switzerland"
do
  montage $COUNTRY'_cases.png' $COUNTRY'_deaths.png' $COUNTRY'_Rt.png' -tile 3x1 -geometry +2+2 $COUNTRY
done

#Montage different countries together
montage  "Austria"  "Belgium" "Denmark" "France" "Germany" "Italy" "Norway" "Spain" "Sweden" "Switzerland" "United_Kingdom" -tile 1x11 -geometry +2+2 'all_last_for_all.png'

#Montage lockdown posteriors of different countries together
montage  "posterior/Austria_last_intervention.png"  "posterior/Belgium_last_intervention.png" "posterior/Denmark_last_intervention.png" "posterior/France_last_intervention.png" "posterior/Germany_last_intervention.png" "posterior/Italy_last_intervention.png" "posterior/Norway_last_intervention.png" "posterior/Spain_last_intervention.png"  "posterior/Sweden_last_intervention.png" "posterior/Switzerland_last_intervention.png" "posterior/United_Kingdom_last_intervention.png" -tile 4x3 -geometry +2+2 posterior/last_intervention.png

montage posterior/alpha_schools_universities.png posterior/alpha_self_isolating_if_ill.png posterior/alpha_public_events.png posterior/alpha_lockdown.png posterior/alpha_social_distancing_encouraged.png  -tile 3x2 -geometry +2+2 posterior/alphas.png
