#Convert all images to have labeled parts (A-Z)

number=0
letters="ABCDEFGHIJKLMNOPQRSTUVWXYZ"
for COUNTRY in "Austria"  "Belgium" "Denmark" "France"
do
  for ending in '_cumulative_cases.png' '_deaths.png' '_Rt.png'
    do
      label=${letters:number:1}
      echo $label
      convert $COUNTRY$ending -pointsize 50 -gravity NorthWest -annotate +0+0 "$label" $COUNTRY$ending
      ((number++))
    done
  montage $COUNTRY'_cumulative_cases.png' $COUNTRY'_deaths.png' $COUNTRY'_Rt.png' -tile 3x1 -geometry +2+2 $COUNTRY

number=0
letters="MNOPQRSTUVWXY"
for COUNTRY in "Germany" "Italy" "Norway" "Spain"
do
  for ending in '_cumulative_cases.png' '_deaths.png' '_Rt.png'
    do
      label=${letters:number:1}
      echo $label
      convert $COUNTRY$ending -pointsize 50 -gravity NorthWest -annotate +0+0 "$label" $COUNTRY$ending
      ((number++))
    done
  montage $COUNTRY'_cumulative_cases.png' $COUNTRY'_deaths.png' $COUNTRY'_Rt.png' -tile 3x1 -geometry +2+2 $COUNTRY

number=0
letters="AAABACADAEAFAGAHAIAJAKALAMANAOAPAQARASATAUAVAWAXAYAZ"
for COUNTRY in "Sweden" "Switzerland" "United_Kingdom"
do
  for ending in '_cumulative_cases.png' '_deaths.png' '_Rt.png'
    do
      label=${letters:number:2}
      echo $label
      convert $COUNTRY$ending -pointsize 50 -gravity NorthWest -annotate +0+0 "$label" $COUNTRY$ending
      number=$((number + 2))
    done
  montage $COUNTRY'_cumulative_cases.png' $COUNTRY'_deaths.png' $COUNTRY'_Rt.png' -tile 3x1 -geometry +2+2 $COUNTRY
done
