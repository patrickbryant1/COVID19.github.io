
#Join country data
#Markers
montage "NPI_markers.png" "mobility_markers.png" "foreacast_markers.png" -tile 3x1 -geometry +2+2 "markers.png"

#Figure 1
#Sweden and Italy together
montage   "Italy_Fig1.png" "Sweden_Fig1.png" -tile 1x2 -geometry +2+2 'Sweden_Italy.png'
montage 'Sweden_Italy.png' "markers.png" -tile 1x2 -geometry +2+2 '../../../../../publication_figures/Figure1.png'

#Figure 2
montage 'posterior/mean_R0*' -tile 6x2 -geometry +2+2 '../../../../../publication_figures/Figure2.png'

#Figure 3
#Forecast
montage forecast/Austria_forecast.png  forecast/Germany_forecast.png  forecast/Sweden_forecast.png forecast/Belgium_forecast.png  forecast/Italy_forecast.png    forecast/Switzerland_forecast.png forecast/Denmark_forecast.png  forecast/Norway_forecast.png   forecast/United_Kingdom_forecast.png forecast/France_forecast.png   forecast/Spain_forecast.png -tile 3x4 -geometry +2+2 '../../../../../publication_figures/Figure3.png'

#Figuer 4
#Montage posterior distributions
montage "posterior/alpha_0.png" 'posterior/alpha_1.png' 'posterior/alpha_2.png' 'posterior/alpha_3.png' 'posterior/alpha_4.png' -tile 3x2 -geometry +2+2 ../../../../../publication_figures/Figure4.png

#Figure 5
#Montage correlations
montage 'correlations/retail_and_recreation_percent_change_from_baseline.png' 'correlations/grocery_and_pharmacy_percent_change_from_baseline.png' 'correlations/transit_stations_percent_change_from_baseline.png' correlations/workplaces_percent_change_from_baseline.png correlations/residential_percent_change_from_baseline.png -tile 3x2 -geometry +2+2 ../../../../../publication_figures/Figure5.png


#Montage correlations for LOO analysis
#Figure S1
montage  "LOO/Austria_Rt_corr.png"  "LOO/Belgium_Rt_corr.png" "LOO/Denmark_Rt_corr.png" "LOO/France_Rt_corr.png" "LOO/Germany_Rt_corr.png" "LOO/Italy_Rt_corr.png" "LOO/Norway_Rt_corr.png" "LOO/Spain_Rt_corr.png" "LOO/Sweden_Rt_corr.png" "LOO/Switzerland_Rt_corr.png" "LOO/United_Kingdom_Rt_corr.png" -tile 3x4 -geometry +2+2 '../../../../../publication_figures/supplementary/FigureS1.png'

#Figure S4
#Montage different countries together
montage  "markers.png" "Austria"  "Belgium" "Denmark" "France"  -tile 1x5 -geometry +2+2 '../../../../../publication_figures/supplementary/FigureS4part1.png'
montage  "Germany" "Italy" "Norway" "Spain" "Sweden" -tile 1x5 -geometry +2+2 '../../../../../publication_figures/supplementary/FigureS4part2.png'
montage  "Switzerland" "United_Kingdom" -tile 1x2 -geometry +2+2 '../../../../../publication_figures/supplementary/FigureS4part3.png'

#Figure S5
BASE=../../../../../../icl_model/model_output/3_week_forecast/plots/forecast
montage $BASE/Austria_forecast.png  $BASE/Germany_forecast.png  $BASE/Sweden_forecast.png  $BASE/Belgium_forecast.png  $BASE/Italy_forecast.png $BASE/Switzerland_forecast.png $BASE/Denmark_forecast.png  $BASE/Norway_forecast.png  $BASE/United_Kingdom_forecast.png $BASE/France_forecast.png  $BASE/Spain_forecast.png -tile 3x4 -geometry +2+2 '../../../../../publication_figures/supplementary/FigureS5.png'

#Figure S6
#Montage posterior distributions for LOO analysis
montage LOO/all_retail.png LOO/all_grocery.png LOO/all_transit.png LOO/all_work.png LOO/all_residential.png -tile 1x5 -geometry +2+2 ../../../../../publication_figures/supplementary/FigureS6.png

#Figure S8
#Montage EpiEstim and mobility R estimate comparison
montage "EpiEstim/Austria.png" "EpiEstim/Belgium.png" "EpiEstim/Denmark.png" "EpiEstim/France.png" "EpiEstim/Germany.png" "EpiEstim/Italy.png" "EpiEstim/Norway.png" "EpiEstim/Spain.png" "EpiEstim/Sweden.png" "EpiEstim/Switzerland.png" "EpiEstim/United_Kingdom.png" -tile 3x4 -geometry +2+2 ../../../../../publication_figures/supplementary/FigureS8.png
