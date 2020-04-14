#!/bin/bash -x


for i in 2*.pdf
do
    j=`basename $i .pdf`
    dir=`echo $j | sed s/.*-[0-9][0-9]_//g | sed s/_.*//g`
    convert -density 200 $j.pdf $j.png
    mkdir -p ${dir}/plots/regions
    # convert -crop 250x140+250+480 $j-0.png ${dir}/plots/$j-retail_and_recreation.png
    # convert -crop 250x140+250+640 $j-0.png ${dir}/plots/$j-grocery_and_pharmacy.png
    # convert -crop 250x140+250+800 $j-0.png ${dir}/plots/$j-parks.png
    # convert -crop 250x140+220+60 $j-1.png  ${dir}/plots/$j-transit_stations.png
    # convert -crop 250x140+220+220 $j-1.png ${dir}/plots/$j-workplace.png
    # convert -crop 250x140+220+380 $j-1.png ${dir}/plots/$j-residential.png
    convert -crop 500x280+500+960 $j-0.png ${dir}/plots/$j-retail_and_recreation.png
    convert -crop 500x280+500+1280 $j-0.png ${dir}/plots/$j-grocery_and_pharmacy.png
    convert -crop 500x280+500+1600 $j-0.png ${dir}/plots/$j-parks.png
    convert -crop 500x280+440+120 $j-1.png  ${dir}/plots/$j-transit_stations.png
    convert -crop 500x280+440+440 $j-1.png ${dir}/plots/$j-workplace.png
    convert -crop 500x280+440+760 $j-1.png ${dir}/plots/$j-residential.png
    for k in $j-[23456789]*.png $j-1[0-9]*.png 
    do
	echo $k
	l=`basename $k .png`
	convert -crop 800x100+80+100  $k ${dir}/plots/regions/$l-A-county.png
	convert -crop 500x400+80+200  $k ${dir}/plots/regions/$l-A-retail_and_recreation.png
	convert -crop 520x400+540+200  $k ${dir}/plots/regions/$l-A-grocery_and_pharmacy.png
	convert -crop 520x400+1020+200 $k ${dir}/plots/regions/$l-A-parks.png
	convert -crop 500x400+80+600  $k ${dir}/plots/regions/$l-A-transit_stations.png
	convert -crop 520x400+540+600  $k ${dir}/plots/regions/$l-A-workplace.png
	convert -crop 520x400+1020+600 $k ${dir}/plots/regions/$l-A-residential.png

	convert -crop 800x100+80+1000  $k ${dir}/plots/regions/$l-B-county.png
	convert -crop 500x400+80+1100  $k ${dir}/plots/regions/$l-B-retail_and_recreation.png
	convert -crop 520x400+540+1100  $k ${dir}/plots/regions/$l-B-grocery_and_pharmacy.png
	convert -crop 520x400+1020+1100 $k ${dir}/plots/regions/$l-B-parks.png
	convert -crop 500x400+80+1500  $k ${dir}/plots/regions/$l-B-transit_stations.png
	convert -crop 520x400+540+1500  $k ${dir}/plots/regions/$l-B-workplace.png
	convert -crop 520x400+1020+1500 $k ${dir}/plots/regions/$l-B-residential.png
    done
done
#250-480  460-600


