
#Join country data
#All countries
montage -label '%f' -pointsize 15 "Austria_Rt.svg" "Belgium_Rt.svg" "Denmark_Rt.svg" "France_Rt.svg" "Germany_Rt.svg" "Italy_Rt.svg" "Norway_Rt.svg" "Spain_Rt.svg" "Sweden_Rt.svg" "Switzerland_Rt.svg" "United_Kingdom_Rt.svg"   -tile 3x4 -geometry +2+2 'LOO.png'
#Correlation
montage "Austria_Rt_corr.svg" "Belgium_Rt_corr.svg" "Denmark_Rt_corr.svg" "France_Rt_corr.svg" "Germany_Rt_corr.svg" "Italy_Rt_corr.svg" "Norway_Rt_corr.svg" "Spain_Rt_corr.svg" "Sweden_Rt_corr.svg" "Switzerland_Rt_corr.svg" "United_Kingdom_Rt_corr.svg" "PearsonR.svg"  -tile 3x4 -geometry +2+2 'LOO_corr.png'
#Mobility alphas
montage  'retail and recreation.svg' 'grocery and pharmacy.svg' 'transit stations.svg' 'workplace.svg' 'residential.svg' -tile 3x2 -geometry +2+2 'alphas.svg'
