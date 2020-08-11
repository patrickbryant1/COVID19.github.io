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
