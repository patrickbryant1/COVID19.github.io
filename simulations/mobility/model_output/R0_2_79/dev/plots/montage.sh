OUTDIR=/home/pbryant/COVID19.github.io/docs/assets/
montage Alabama_cases.png Alabama_deaths.png Alabama_Rt.png Alaska_cases.png Alaska_deaths.png Alaska_Rt.png Arizona_cases.png Arizona_deaths.png Arizona_Rt.png Arkansas_cases.png Arkansas_deaths.png Arkansas_Rt.png California_cases.png California_deaths.png California_Rt.png -tile 3x5 -geometry +2+2 $OUTDIR/all_states1.png
montage Colorado_cases.png Colorado_deaths.png Colorado_Rt.png Connecticut_cases.png Connecticut_deaths.png Connecticut_Rt.png Delaware_cases.png Delaware_deaths.png Delaware_Rt.png Florida_cases.png Florida_deaths.png Florida_Rt.png Georgia_cases.png Georgia_deaths.png Georgia_Rt.png  -tile 3x6 -geometry +2+2 $OUTDIR/all_states2.png
montage Hawaii_cases.png Hawaii_deaths.png Hawaii_Rt.png Idaho_cases.png Idaho_deaths.png Idaho_Rt.png Illinois_cases.png Illinois_deaths.png Illinois_Rt.png Indiana_cases.png Indiana_deaths.png Indiana_Rt.png Iowa_cases.png Iowa_deaths.png Iowa_Rt.png Kansas_cases.png Kansas_deaths.png Kansas_Rt.png  -tile 3x6 -geometry +2+2 $OUTDIR/all_states3.png
montage Kentucky_cases.png Kentucky_deaths.png Kentucky_Rt.png Louisiana_cases.png Louisiana_deaths.png Louisiana_Rt.png Maine_cases.png Maine_deaths.png Maine_Rt.png Maryland_cases.png Maryland_deaths.png Maryland_Rt.png Massachusetts_cases.png Massachusetts_deaths.png Massachusetts_Rt.png Michigan_cases.png Michigan_deaths.png Michigan_Rt.png -tile 3x6 -geometry +2+2 $OUTDIR/all_states4.png
montage Minnesota_cases.png Minnesota_deaths.png Minnesota_Rt.png Mississippi_cases.png Mississippi_deaths.png Mississippi_Rt.png Missouri_cases.png Missouri_deaths.png Missouri_Rt.png Montana_cases.png Montana_deaths.png Montana_Rt.png Nebraska_cases.png Nebraska_deaths.png Nebraska_Rt.png Nevada_cases.png Nevada_deaths.png Nevada_Rt.png  -tile 3x6 -geometry +2+2 $OUTDIR/all_states5.png
montage 'New Hampshire_cases.png' 'New Hampshire_deaths.png' 'New Hampshire_Rt.png' 'New Jersey_cases.png' 'New Jersey_deaths.png' 'New Jersey_Rt.png' 'New Mexico_cases.png' 'New Mexico_deaths.png' 'New Mexico_Rt.png' 'New York_cases.png' 'New York_deaths.png' 'New York_Rt.png' 'North Carolina_cases.png' 'North Carolina_deaths.png' 'North Carolina_Rt.png' 'North Dakota_cases.png' 'North Dakota_deaths.png' 'North Dakota_Rt.png' -tile 3x6 -geometry +2+2 $OUTDIR/all_states6.png
montage Ohio_cases.png Ohio_deaths.png Ohio_Rt.png Oklahoma_cases.png Oklahoma_deaths.png Oklahoma_Rt.png Oregon_cases.png Oregon_deaths.png Oregon_Rt.png Pennsylvania_cases.png Pennsylvania_deaths.png Pennsylvania_Rt.png 'Rhode Island_cases.png' 'Rhode Island_deaths.png' 'Rhode Island_Rt.png' 'South Carolina_cases.png' 'South Carolina_deaths.png' 'South Carolina_Rt.png'  -tile 3x6 -geometry +2+2 $OUTDIR/all_states7.png
montage 'South Dakota_cases.png' 'South Dakota_deaths.png' 'South Dakota_Rt.png' Tennessee_cases.png Tennessee_deaths.png Tennessee_Rt.png Texas_cases.png Texas_deaths.png Texas_Rt.png Utah_cases.png Utah_deaths.png Utah_Rt.png Vermont_cases.png Vermont_deaths.png Vermont_Rt.png Virginia_cases.png Virginia_deaths.png Virginia_Rt.png -tile 3x6 -geometry +2+2 $OUTDIR/all_states8.png
montage Washington_cases.png Washington_deaths.png Washington_Rt.png 'West Virginia_cases.png' 'West Virginia_deaths.png' 'West Virginia_Rt.png' Wisconsin_cases.png Wisconsin_deaths.png Wisconsin_Rt.png Wyoming_cases.png Wyoming_deaths.png Wyoming_Rt.png  -tile 3x6 -geometry +2+2 $OUTDIR/all_states9.png

#Montage for paper
#Figure 2
montage 'New York_cases.png' 'New York_deaths.png' 'New York_Rt.png' 'Louisiana_cases.png' 'Louisiana_deaths.png' 'Louisiana_Rt.png' Michigan_cases.png Michigan_deaths.png Michigan_Rt.png 'North Carolina_cases.png' 'North Carolina_deaths.png' 'North Carolina_Rt.png' -tile 3x4 -geometry +2+2 Figure2.png
montage mobility_markers.png sim_markers.png -tile 2x1 -geometry +2+2 markers.png
montage Figure2.png markers.png -tile 1x2 -geometry +2+2 Figure2.png

montage 'New York_cases.png' 'New York_deaths.png' 'New York_Rt.png' 'North Carolina_cases.png' 'North Carolina_deaths.png' 'North Carolina_Rt.png' -tile 3x4 -geometry +2+2 newyork_northcarolina.png
montage mobility_markers.png sim_markers.png -tile 2x1 -geometry +2+2 markers.png
montage newyork_northcarolina.png markers.png -tile 1x2 -geometry +2+2 newyork_northcarolina.png
#Add mob and epiestim r estimates
montage ../epiestim_vs_mob_close.png ../epiestim_vs_mob_open.png Figure2.png -tile 1x3 -geometry +2+2 ../Figure2.png

#'District of Columbia_cases.png' 'District of Columbia_deaths.png' 'District of Columbia_Rt.png'
#Montage markers
montage  $OUTDIR/all_states9.png markers.png -tile 1x2 -geometry +2+2 $OUTDIR/all_states9.png


#Montage posterior alphas
montage posterior/alpha_0.png posterior/alpha_1.png posterior/alpha_2.png posterior/alpha_3.png posterior/alpha_4.png -tile 3x2 -geometry +2+2 posterior/alphas.png

#Montage posterior R0
montage posterior/R_Alabama.png posterior/R_Alaska.png posterior/R_Arizona.png posterior/R_Arkansas.png posterior/R_California.png posterior/R_Colorado.png posterior/R_Connecticut.png posterior/R_Delaware.png posterior/R_Florida.png posterior/R_Georgia.png posterior/R_Hawaii.png posterior/R_Idaho.png posterior/R_Illinois.png posterior/R_Indiana.png posterior/R_Iowa.png posterior/R_Kansas.png posterior/R_Kentucky.png posterior/R_Louisiana.png posterior/R_Maine.png posterior/R_Maryland.png posterior/R_Massachusetts.png posterior/R_Michigan.png posterior/R_Minnesota.png posterior/R_Mississippi.png posterior/R_Missouri.png posterior/R_Montana.png posterior/R_Nebraska.png posterior/R_Nevada.png 'posterior/R_New Hampshire.png' 'posterior/R_New Jersey.png' 'posterior/R_New Mexico.png' 'posterior/R_New York.png' 'posterior/R_North Carolina.png' 'posterior/R_North Dakota.png' posterior/R_Ohio.png posterior/R_Oklahoma.png posterior/R_Oregon.png posterior/R_Pennsylvania.png 'posterior/R_Rhode Island.png' 'posterior/R_South Carolina.png' 'posterior/R_South Dakota.png' posterior/R_Tennessee.png posterior/R_Texas.png posterior/R_Utah.png posterior/R_Vermont.png posterior/R_Virginia.png posterior/R_Washington.png 'posterior/R_West Virginia.png' posterior/R_Wisconsin.png posterior/R_Wyoming.png  -tile 6x9 -geometry +2+2 posterior/R.png

#Montage R_comparison R0
montage R_comparison/Alabama.png R_comparison/Alaska.png R_comparison/Arizona.png R_comparison/Arkansas.png R_comparison/California.png R_comparison/Colorado.png R_comparison/Connecticut.png R_comparison/Delaware.png R_comparison/Florida.png R_comparison/Georgia.png R_comparison/Hawaii.png R_comparison/Idaho.png R_comparison/Illinois.png R_comparison/Indiana.png R_comparison/Iowa.png R_comparison/Kansas.png R_comparison/Kentucky.png R_comparison/Louisiana.png R_comparison/Maine.png R_comparison/Maryland.png R_comparison/Massachusetts.png R_comparison/Michigan.png R_comparison/Minnesota.png R_comparison/Mississippi.png -tile 4x6 -geometry +2+2 R_comparison/R1.png

montage R_comparison/Missouri.png R_comparison/Montana.png R_comparison/Nebraska.png R_comparison/Nevada.png 'R_comparison/New Hampshire.png' 'R_comparison/New Jersey.png' 'R_comparison/New Mexico.png' 'R_comparison/New York.png' 'R_comparison/North Carolina.png' 'R_comparison/North Dakota.png' R_comparison/Ohio.png R_comparison/Oklahoma.png R_comparison/Oregon.png R_comparison/Pennsylvania.png 'R_comparison/Rhode Island.png' 'R_comparison/South Carolina.png' 'R_comparison/South Dakota.png' R_comparison/Tennessee.png R_comparison/Texas.png R_comparison/Utah.png R_comparison/Vermont.png R_comparison/Virginia.png R_comparison/Washington.png 'R_comparison/West Virginia.png' -tile 4x6 -geometry +2+2 R_comparison/R2.png

montage  R_comparison/Wisconsin.png R_comparison/Wyoming.png R_comparison/Wisconsin.png R_comparison/Wyoming.png  -tile 4x1 -geometry +2+2 R_comparison/R3.png
