# Instructions on how to extact data from gools mobility plots


## Download files

To download files use this command

for i in `awk '{print $2}' ./country-codes` ; do curl https://www.gstatic.com/covid19/mobility/2020-04-05_${i}_Mobility_Report_en.pdf -o 2020-04-05_${i}_Mobility_Report_en.pdf ; done


## Extract png images

Then extract the images using the script extract-plots.sh


## Digitize this

Manuall using the program [https://apps.automeris.io/wpd/](https://apps.automeris.io/wpd/)

Please not that the dates on the X-axis are assumed to be number of days form 2020-01-01


## Convert the eextracted data to a CVS 

The script convertcsv.py does this

(Please not that some country codes are not the same here as in ECDC (for instance Greece is GR and not EL)

