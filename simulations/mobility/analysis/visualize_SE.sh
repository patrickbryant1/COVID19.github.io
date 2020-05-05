#!/bin/bash -l

DATADIR=/home/arnee/git/COVID19.github.io/simulations/mobility/data/
COUNTRIES="Stockholm","VästraGötaland","Dalarna","Jönköping","Gävleborg","Skåne","Sörmland","Uppsala","Östergötland"
SD=./model_output/R0_2_79/dev/plots/short_dates.csv
#Visualize model output
#Overlay mobility and intervention
#/home/arnee/git/COVID19.github.io/simulations/mobility/mobility_intervention_overlay_SE.py --datadir $DATADIR --outdir $OUTDIR

#DTS=104
#ED=2020-04-15 #End date, up to which to include data (different depending on forecast)

for DTS in 80 100 120 84 104
do
    for ED in 2020-03-23 2020-04-01 2020-04-07 2020-04-15  # 2020-05-01
    do
	OUTDIR=/home/arnee/git/COVID19.github.io/simulations/mobility/Sweden/${ED}-${DTS}/
	if [ -s ${OUTDIR}/summary.csv ]
	then
	    mkdir  $OUTDIR/plots
	    python3 /home/arnee/git/COVID19.github.io/simulations/mobility/analysis/visualize_model_output_SE.py --datadir $DATADIR --countries $COUNTRIES --days_to_simulate $DTS --short_dates $SD --outdir $OUTDIR
	    for i in `echo $COUNTRIES|sed "s/,/ /g"`
	    do
		echo ${i}
		montage -mode concatenate -tile 3x $OUTDIR/plots/${i}_Rt.png $OUTDIR/plots/${i}_deaths.png $OUTDIR/plots/${i}_cases.png $OUTDIR/plots/${i}_montage.png
	    done
	    convert -append  $OUTDIR/plots/*_montage.png $OUTDIR/plots/montage.png
	fi
    done
done


