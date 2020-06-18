montage 1.png 2.png 3.png 4.png 5.png 6.png -tile 3x2 -geometry +2+2 mobility.png
montage 1_extreme.png 2_extreme.png 3_extreme.png 4_extreme.png 5_extreme.png -tile 3x2 -geometry +2+2 extreme_mobility.png

#Epiestim vs mobility
montage 'retail_and_recreation_percent_change_from_baseline_all_close_curves.png' 'grocery_and_pharmacy_percent_change_from_baseline_all_close_curves.png' 'transit_stations_percent_change_from_baseline_all_close_curves.png' 'workplaces_percent_change_from_baseline_all_close_curves.png' 'residential_percent_change_from_baseline_all_close_curves.png' -tile 5x1 -geometry +2+2 epiestim_vs_mob_close.png
montage 'retail_and_recreation_percent_change_from_baseline_all_open_curves.png' 'grocery_and_pharmacy_percent_change_from_baseline_all_open_curves.png' 'transit_stations_percent_change_from_baseline_all_open_curves.png' 'workplaces_percent_change_from_baseline_all_open_curves.png' 'residential_percent_change_from_baseline_all_open_curves.png' -tile 5x1 -geometry +2+2 epiestim_vs_mob_open.png
montage  epiestim_vs_mob_close.png epiestim_vs_mob_open.png -tile 1x2 -geometry +2+2 epiestim_vs_mob_open_and_close.png
