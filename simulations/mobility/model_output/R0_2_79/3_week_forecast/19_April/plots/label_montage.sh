#Convert all images to have labeled parts (A-Z)

#Figure 1. Sweden and Italy
number=0
letters="ABCDEFGHIJKLMNOPQRSTUVWXYZ"
for COUNTRY in "Italy" "Sweden"
do
  for ending in '_cumulative_cases' '_deaths' '_Rt'
    do
      label=${letters:number:1}
      echo $label
      convert $COUNTRY$ending'.png' -pointsize 50 -gravity NorthWest -annotate +0+0 "$label" $COUNTRY$ending'_Fig1.png'
      ((number++))
    done
  montage $COUNTRY'_cumulative_cases_Fig1.png' $COUNTRY'_deaths_Fig1.png' $COUNTRY'_Rt_Fig1.png' -tile 3x1 -geometry +2+2 $COUNTRY'_Fig1.png'
done

#Figure 2
number=0
letters="ABCDEFGHIJKLMNOPQRSTUVWXYZ"
for f in posterior/mean_R0*
  do
  label=${letters:number:1}
  convert $f -pointsize 30 -gravity NorthWest -annotate +0+0 "$label" $f
  ((number++))
done


#Figure 3
number=0
letters="ABCDEFGHIJKLMNOPQRSTUVWXYZ"
for f in forecast/Austria_forecast.png  forecast/Germany_forecast.png  forecast/Sweden_forecast.png forecast/Belgium_forecast.png  forecast/Italy_forecast.png    forecast/Switzerland_forecast.png forecast/Denmark_forecast.png  forecast/Norway_forecast.png   forecast/United_Kingdom_forecast.png forecast/France_forecast.png   forecast/Spain_forecast.png
do
  label=${letters:number:1}
  convert $f -pointsize 50 -gravity NorthWest -annotate +0+0 "$label" $f
  ((number++))
done

#Figure 4
number=0
letters="ABCDEFGHIJKLMNOPQRSTUVWXYZ"
for f in "posterior/alpha_0.png" 'posterior/alpha_1.png' 'posterior/alpha_2.png' 'posterior/alpha_3.png' 'posterior/alpha_4.png'
  do
  label=${letters:number:1}
  convert "$f" -pointsize 50 -gravity NorthWest -annotate +0+0 "$label" $f
  ((number++))
done

#Figure 5
number=0
letters="ABCDEFGHIJKLMNOPQRSTUVWXYZ"
for f in 'correlations/retail_and_recreation_percent_change_from_baseline.png' 'correlations/grocery_and_pharmacy_percent_change_from_baseline.png' 'correlations/transit_stations_percent_change_from_baseline.png' correlations/workplaces_percent_change_from_baseline.png correlations/residential_percent_change_from_baseline.png
  do
  label=${letters:number:1}
  convert "$f" -pointsize 50 -gravity NorthWest -annotate +0+0 "$label" $f
  ((number++))
done


##SUPPLEMENTARY###
Figure S1
number=0
letters="ABCDEFGHIJKLMNOPQRSTUVWXYZ"
for f in "LOO/Austria_Rt_corr.png"  "LOO/Belgium_Rt_corr.png" "LOO/Denmark_Rt_corr.png" "LOO/France_Rt_corr.png" "LOO/Germany_Rt_corr.png" "LOO/Italy_Rt_corr.png" "LOO/Norway_Rt_corr.png" "LOO/Spain_Rt_corr.png" "LOO/Sweden_Rt_corr.png" "LOO/Switzerland_Rt_corr.png" "LOO/United_Kingdom_Rt_corr.png" -tile 3x4 -geometry +2+2 '/home/patrick/COVID19.github.io/simulations/mobility/publication_figures/supplementary/FigureS1.png'
  do
  label=${letters:number:1}
  convert "$f" -pointsize 50 -gravity NorthWest -annotate +0+0 "$label" $f
  ((number++))
done

#Supplementary figure S4
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
done
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
done
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

#Figure S5
BASE=./forecast
number=0
letters="ABCDEFGHIJKLMNOPQRSTUVWXYZ"
for f in $BASE/Austria_forecast.png  $BASE/Germany_forecast.png  $BASE/Sweden_forecast.png $BASE/Belgium_forecast.png  $BASE/Italy_forecast.png $BASE/Switzerland_forecast.png $BASE/Denmark_forecast.png  $BASE/Norway_forecast.png  $BASE/United_Kingdom_forecast.png $BASE/France_forecast.png  $BASE/Spain_forecast.png
do
  label=${letters:number:1}
  convert "$f" -pointsize 50 -gravity NorthWest -annotate +0+0 "$label" $f
  ((number++))
done

#Figure S6
#Montage posterior distributions for LOO analysis
montage "LOO/Austria_0.png" "LOO/Belgium_0.png" "LOO/Denmark_0.png" "LOO/France_0.png" "LOO/Germany_0.png" "LOO/Italy_0.png" "LOO/Norway_0.png" "LOO/Spain_0.png" "LOO/Sweden_0.png" "LOO/Switzerland_0.png" "LOO/United_Kingdom_0.png" -tile 6x2 -geometry +2+2 LOO/all_retail.png
montage "LOO/Austria_1.png" "LOO/Belgium_1.png" "LOO/Denmark_1.png" "LOO/France_1.png" "LOO/Germany_1.png" "LOO/Italy_1.png" "LOO/Norway_1.png" "LOO/Spain_1.png" "LOO/Sweden_1.png" "LOO/Switzerland_1.png" "LOO/United_Kingdom_1.png" -tile 6x2 -geometry +2+2 LOO/all_grocery.png
montage "LOO/Austria_2.png" "LOO/Belgium_2.png" "LOO/Denmark_2.png" "LOO/France_2.png" "LOO/Germany_2.png" "LOO/Italy_2.png" "LOO/Norway_2.png" "LOO/Spain_2.png" "LOO/Sweden_2.png" "LOO/Switzerland_2.png" "LOO/United_Kingdom_2.png" -tile 6x2 -geometry +2+2 LOO/all_transit.png
montage "LOO/Austria_3.png" "LOO/Belgium_3.png" "LOO/Denmark_3.png" "LOO/France_3.png" "LOO/Germany_3.png" "LOO/Italy_3.png" "LOO/Norway_3.png" "LOO/Spain_3.png" "LOO/Sweden_3.png" "LOO/Switzerland_3.png" "LOO/United_Kingdom_3.png" -tile 6x3 -geometry +3+3 LOO/all_work.png
montage "LOO/Austria_4.png" "LOO/Belgium_4.png" "LOO/Denmark_4.png" "LOO/France_4.png" "LOO/Germany_4.png" "LOO/Italy_4.png" "LOO/Norway_4.png" "LOO/Spain_4.png" "LOO/Sweden_4.png" "LOO/Switzerland_4.png" "LOO/United_Kingdom_4.png" -tile 6x4 -geometry +4+4 LOO/all_residential.png

number=0
letters="ABCDEFGHIJKLMNOPQRSTUVWXYZ"
for f in LOO/all_retail.png LOO/all_grocery.png LOO/all_transit.png LOO/all_work.png LOO/all_residential.png
do
  label=${letters:number:1}
  convert "$f" -pointsize 50 -gravity NorthWest -annotate +0+0 "$label" $f
  ((number++))
done


#Figure S8
number=0
letters="ABCDEFGHIJKLMNOPQRSTUVWXYZ"
for f in "EpiEstim/Austria.png" "EpiEstim/Belgium.png" "EpiEstim/Denmark.png" "EpiEstim/France.png" "EpiEstim/Germany.png" "EpiEstim/Italy.png" "EpiEstim/Norway.png" "EpiEstim/Spain.png" "EpiEstim/Sweden.png" "EpiEstim/Switzerland.png" "EpiEstim/United_Kingdom.png"
do
  label=${letters:number:1}
  convert "$f" -pointsize 50 -gravity NorthWest -annotate +0+0 "$label" $f
  ((number++))
done
