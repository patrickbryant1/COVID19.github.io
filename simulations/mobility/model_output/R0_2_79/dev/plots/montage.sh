OUTDIR=/home/patrick/COVID19.github.io/docs/assets/
montage Alabama_cases.png Alabama_deaths.png Alabama_Rt.png Alaska_cases.png Alaska_deaths.png Alaska_Rt.png Arizona_cases.png Arizona_deaths.png Arizona_Rt.png Arkansas_cases.png Arkansas_deaths.png Arkansas_Rt.png California_cases.png California_deaths.png California_Rt.png Colorado_cases.png Colorado_deaths.png Colorado_Rt.png  -tile 3x6 -geometry +2+2 $OUTDIR/all_states1.png
montage Connecticut_cases.png Connecticut_deaths.png Connecticut_Rt.png Delaware_cases.png Delaware_deaths.png Delaware_Rt.png Florida_cases.png Florida_deaths.png Florida_Rt.png Georgia_cases.png Georgia_deaths.png Georgia_Rt.png Hawaii_cases.png Hawaii_deaths.png Hawaii_Rt.png  -tile 3x6 -geometry +2+2 $OUTDIR/all_states2.png
montage Idaho_cases.png Idaho_deaths.png Idaho_Rt.png Illinois_cases.png Illinois_deaths.png Illinois_Rt.png Indiana_cases.png Indiana_deaths.png Indiana_Rt.png Iowa_cases.png Iowa_deaths.png Iowa_Rt.png Kansas_cases.png Kansas_deaths.png Kansas_Rt.png Kentucky_cases.png Kentucky_deaths.png Kentucky_Rt.png -tile 3x6 -geometry +2+2 $OUTDIR/all_states3.png
montage Louisiana_cases.png Louisiana_deaths.png Louisiana_Rt.png Maine_cases.png Maine_deaths.png Maine_Rt.png Maryland_cases.png Maryland_deaths.png Maryland_Rt.png Massachusetts_cases.png Massachusetts_deaths.png Massachusetts_Rt.png Michigan_cases.png Michigan_deaths.png Michigan_Rt.png Minnesota_cases.png Minnesota_deaths.png Minnesota_Rt.png  -tile 3x6 -geometry +2+2 $OUTDIR/all_states4.png
montage Mississippi_cases.png Mississippi_deaths.png Mississippi_Rt.png Missouri_cases.png Missouri_deaths.png Missouri_Rt.png Montana_cases.png Montana_deaths.png Montana_Rt.png Nebraska_cases.png Nebraska_deaths.png Nebraska_Rt.png Nevada_cases.png Nevada_deaths.png Nevada_Rt.png 'New Hampshire_cases.png' 'New Hampshire_deaths.png' 'New Hampshire_Rt.png' -tile 3x6 -geometry +2+2 $OUTDIR/all_states5.png
montage 'New Jersey_cases.png' 'New Jersey_deaths.png' 'New Jersey_Rt.png' 'New Mexico_cases.png' 'New Mexico_deaths.png' 'New Mexico_Rt.png' 'New York_cases.png' 'New York_deaths.png' 'New York_Rt.png' 'North Carolina_cases.png' 'North Carolina_deaths.png' 'North Carolina_Rt.png' 'North Dakota_cases.png' 'North Dakota_deaths.png' 'North Dakota_Rt.png' Ohio_cases.png Ohio_deaths.png Ohio_Rt.png  -tile 3x6 -geometry +2+2 $OUTDIR/all_states6.png
montage Oklahoma_cases.png Oklahoma_deaths.png Oklahoma_Rt.png Oregon_cases.png Oregon_deaths.png Oregon_Rt.png Pennsylvania_cases.png Pennsylvania_deaths.png Pennsylvania_Rt.png 'Rhode Island_cases.png' 'Rhode Island_deaths.png' 'Rhode Island_Rt.png' 'South Carolina_cases.png' 'South Carolina_deaths.png' 'South Carolina_Rt.png' 'South Dakota_cases.png' 'South Dakota_deaths.png' 'South Dakota_Rt.png'  -tile 3x6 -geometry +2+2 $OUTDIR/all_states7.png
montage Tennessee_cases.png Tennessee_deaths.png Tennessee_Rt.png Texas_cases.png Texas_deaths.png Texas_Rt.png Utah_cases.png Utah_deaths.png Utah_Rt.png Vermont_cases.png Vermont_deaths.png Vermont_Rt.png Virginia_cases.png Virginia_deaths.png Virginia_Rt.png Washington_cases.png Washington_deaths.png Washington_Rt.png -tile 3x6 -geometry +2+2 $OUTDIR/all_states8.png
montage 'West Virginia_cases.png' 'West Virginia_deaths.png' 'West Virginia_Rt.png' Wisconsin_cases.png Wisconsin_deaths.png Wisconsin_Rt.png Wyoming_cases.png Wyoming_deaths.png Wyoming_Rt.png  -tile 3x6 -geometry +2+2 $OUTDIR/all_states9.png

#Montage for paper
#Figure 2
montage 'New York_cases.png' 'New York_deaths.png' 'New York_Rt.png' 'Louisiana_cases.png' 'Louisiana_deaths.png' 'Louisiana_Rt.png' Michigan_cases.png Michigan_deaths.png Michigan_Rt.png 'North Carolina_cases.png' 'North Carolina_deaths.png' 'North Carolina_Rt.png' -tile 3x4 -geometry +2+2 Figure2.png
montage mobility_markers.png sim_markers.png -tile 2x1 -geometry +2+2 markers.png
montage Figure2.png markers.png -tile 1x2 -geometry +2+2 Figure2.png
#Add mob and epiestim r estimates
montage ../epiestim_vs_mob_close.png ../epiestim_vs_mob_open.png Figure2.png -tile 1x3 -geometry +2+2 ../Figure2.png 

#'District of Columbia_cases.png' 'District of Columbia_deaths.png' 'District of Columbia_Rt.png'
#Montage markers
montage  $OUTDIR/all_states9.png markers.png -tile 1x2 -geometry +2+2 $OUTDIR/all_states9.png
