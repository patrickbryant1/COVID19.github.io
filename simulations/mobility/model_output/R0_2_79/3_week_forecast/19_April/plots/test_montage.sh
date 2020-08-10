#Convert all images to have labeled parts (A-Z)

# #Figure 1. Sweden and Italy
# number=0
# letters="ABCDEFGHIJKLMNOPQRSTUVWXYZ"
# for COUNTRY in "Italy" "Sweden"
# do
#   for ending in '_cumulative_cases' '_deaths' '_Rt'
#     do
#       label=${letters:number:1}
#       echo $label
#       convert $COUNTRY$ending'.png' -pointsize 50 -gravity NorthWest -annotate +0+0 "$label" $COUNTRY$ending'_Fig1.png'
#       ((number++))
#     done
#   montage $COUNTRY'_cumulative_cases_Fig1.png' $COUNTRY'_deaths_Fig1.png' $COUNTRY'_Rt_Fig1.png' -tile 3x1 -geometry +2+2 $COUNTRY'_Fig1.png'
# done

#Figure 2
letters="ABCDEFGHIJKLMNOPQRSTUVWXYZ"
for f in posterior/mean_R0*
  do
  label=${letters:number:1}
  convert $f -pointsize 30 -gravity NorthWest -annotate +0+0 "$label" $f
  ((number++))
done


#Figure 3
# letters="ABCDEFGHIJKLMNOPQRSTUVWXYZ"
# for f in forecast/Austria_forecast.png  forecast/Germany_forecast.png  forecast/Sweden_forecast.png forecast/Belgium_forecast.png  forecast/Italy_forecast.png    forecast/Switzerland_forecast.png forecast/Denmark_forecast.png  forecast/Norway_forecast.png   forecast/United_Kingdom_forecast.png forecast/France_forecast.png   forecast/Spain_forecast.png
# do
#   label=${letters:number:1}
#   convert $f -pointsize 50 -gravity NorthWest -annotate +0+0 "$label" $f
#   ((number++))
# done



#
# #Supplementary figure S4
# number=0
# letters="ABCDEFGHIJKLMNOPQRSTUVWXYZ"
# for COUNTRY in "Austria"  "Belgium" "Denmark" "France"
# do
#   for ending in '_cumulative_cases.png' '_deaths.png' '_Rt.png'
#     do
#       label=${letters:number:1}
#       echo $label
#       convert $COUNTRY$ending -pointsize 50 -gravity NorthWest -annotate +0+0 "$label" $COUNTRY$ending
#       ((number++))
#     done
#   montage $COUNTRY'_cumulative_cases.png' $COUNTRY'_deaths.png' $COUNTRY'_Rt.png' -tile 3x1 -geometry +2+2 $COUNTRY
#
# number=0
# letters="MNOPQRSTUVWXY"
# for COUNTRY in "Germany" "Italy" "Norway" "Spain"
# do
#   for ending in '_cumulative_cases.png' '_deaths.png' '_Rt.png'
#     do
#       label=${letters:number:1}
#       echo $label
#       convert $COUNTRY$ending -pointsize 50 -gravity NorthWest -annotate +0+0 "$label" $COUNTRY$ending
#       ((number++))
#     done
#   montage $COUNTRY'_cumulative_cases.png' $COUNTRY'_deaths.png' $COUNTRY'_Rt.png' -tile 3x1 -geometry +2+2 $COUNTRY
#
# number=0
# letters="AAABACADAEAFAGAHAIAJAKALAMANAOAPAQARASATAUAVAWAXAYAZ"
# for COUNTRY in "Sweden" "Switzerland" "United_Kingdom"
# do
#   for ending in '_cumulative_cases.png' '_deaths.png' '_Rt.png'
#     do
#       label=${letters:number:2}
#       echo $label
#       convert $COUNTRY$ending -pointsize 50 -gravity NorthWest -annotate +0+0 "$label" $COUNTRY$ending
#       number=$((number + 2))
#     done
#   montage $COUNTRY'_cumulative_cases.png' $COUNTRY'_deaths.png' $COUNTRY'_Rt.png' -tile 3x1 -geometry +2+2 $COUNTRY
# done
