#Convert all images to have labeled parts (A-Z)

#Figure 1. posterior for original model with last intervention for Sweden
number=0
BASE=../plot/original_model/figures/posterior
letters="ABCDEFGHIJKLMNOPQRSTUVWXYZ"
for f in $BASE/alpha_schools_universities.png $BASE/alpha_self_isolating_if_ill.png $BASE/alpha_public_events.png $BASE/alpha_lockdown.png $BASE/alpha_social_distancing_encouraged.png $BASE/last_intervention.png
do
  label=${letters:number:1}
  echo $label
  convert $f -pointsize 50 -gravity NorthWest -annotate +0+0 "$label" $f
  ((number++))
done


montage $BASE/alpha_schools_universities.png $BASE/alpha_self_isolating_if_ill.png $BASE/alpha_public_events.png $BASE/alpha_lockdown.png $BASE/alpha_social_distancing_encouraged.png $BASE/last_intervention.png -tile 3x2 -geometry +2+2 Figure1.png


#Figure 2. Fit for sweden with and w/o last intervention
number=0
BASE1=../plot/original_model/figures
BASE2=../plot/no_last/figures
letters="ABCDEFGHIJKLMNOPQRSTUVWXYZ"
for f in $BASE1/Sweden_cases.png $BASE1/Sweden_deaths.png $BASE1/Sweden_Rt.png $BASE2/Sweden_cases.png $BASE2/Sweden_deaths.png $BASE2/Sweden_Rt.png
do
  label=${letters:number:1}
  echo $label
  convert $f -pointsize 50 -gravity NorthWest -annotate +0+0 "$label" $f
  ((number++))
done


montage $BASE1/Sweden_cases.png $BASE1/Sweden_deaths.png $BASE1/Sweden_Rt.png $BASE2/Sweden_cases.png $BASE2/Sweden_deaths.png $BASE2/Sweden_Rt.png -tile 3x2 -geometry +2+2 Figure2.png
montage NPI_markers.png Figure2.png -tile 1x2 -geometry +2+2 Figure2.png
#Figure 3. posterior for model without the last intervention for Sweden
number=0
BASE=../plot/no_last/figures/posterior
letters="ABCDEFGHIJKLMNOPQRSTUVWXYZ"
for f in $BASE/alpha_schools_universities.png $BASE/alpha_self_isolating_if_ill.png $BASE/alpha_public_events.png $BASE/alpha_lockdown.png $BASE/alpha_social_distancing_encouraged.png
do
  label=${letters:number:1}
  echo $label
  convert $f -pointsize 50 -gravity NorthWest -annotate +0+0 "$label" $f
  ((number++))
done

montage $BASE/alpha_schools_universities.png $BASE/alpha_self_isolating_if_ill.png $BASE/alpha_public_events.png $BASE/alpha_lockdown.png $BASE/alpha_social_distancing_encouraged.png -tile 3x2 -geometry +2+2 Figure3.png



#Figure 3. posterior for model without the last intervention for Sweden and without the extra lockdown option
number=0
BASE=../plot/no_lock_no_last/figures/posterior
letters="ABCDEFGHIJKLMNOPQRSTUVWXYZ"
for f in $BASE/alpha_schools_universities.png $BASE/alpha_self_isolating_if_ill.png $BASE/alpha_public_events.png $BASE/alpha_lockdown.png $BASE/alpha_social_distancing_encouraged.png
do
  label=${letters:number:1}
  echo $label
  convert $f -pointsize 50 -gravity NorthWest -annotate +0+0 "$label" $f
  ((number++))
done

montage $BASE/alpha_schools_universities.png $BASE/alpha_self_isolating_if_ill.png $BASE/alpha_public_events.png $BASE/alpha_lockdown.png $BASE/alpha_social_distancing_encouraged.png -tile 3x2 -geometry +2+2 Figure4.png
