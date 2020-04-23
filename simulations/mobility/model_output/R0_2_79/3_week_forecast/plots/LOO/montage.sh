
#Join country data
#All countries
montage -label '%f' -pointsize 15 "Austria_Rt.png" "Belgium_Rt.png" "Denmark_Rt.png" "France_Rt.png" "Germany_Rt.png" "Italy_Rt.png" "Norway_Rt.png" "Spain_Rt.png" "Sweden_Rt.png" "Switzerland_Rt.png" "United_Kingdom_Rt.png"   -tile 3x4 -geometry +2+2 'LOO.png'
#Correlation
montage "Austria_Rt_corr.png" "Belgium_Rt_corr.png" "Denmark_Rt_corr.png" "France_Rt_corr.png" "Germany_Rt_corr.png" "Italy_Rt_corr.png" "Norway_Rt_corr.png" "Spain_Rt_corr.png" "Sweden_Rt_corr.png" "Switzerland_Rt_corr.png" "United_Kingdom_Rt_corr.png" "PearsonR.png"  -tile 3x4 -geometry +2+2 'LOO_corr.png'
#Mobility alphas
montage  'retail and recreation.png' 'grocery and pharmacy.png' 'transit stations.png' 'workplace.png' 'residential.png' -tile 3x2 -geometry +2+2 'alphas.png'
