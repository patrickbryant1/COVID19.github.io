#!/bin/bash -x

#Imagick convert required.
#Bugfixing from:
#https://askubuntu.com/questions/1081895/trouble-with-batch-conversion-of-png-to-pdf-using-convert
# convert is a powerful command line tool to convert graphics. Its support for PDF is provided by Ghostscript.
#Because of a significant security hole in Ghostscript prior to version 9.24, use of convert on PDF files
#has been blocked as a stopgap. The issue has been fixed since Ghostscript version 9.24.
#While Ghostscript versions are updated to secure versions in all supported Ubuntu versions
#(at this time from Ubuntu 16.04 onwards), the usage restriction may still be in place.
# The policy file is /etc/ImageMagick-6/policy.xml.
#You may edit that file as root user to change the policies.
# For desktop users not running a webserver, simply eliminating these restrictions
# might be good enough. To that aim, one may delete the file, but it is better practice
# to "move the file out" by renaming it. With this command, you are renaming the file.
# As a result, all policies are lifted, but you still can revert if needed.
#sudo mv /etc/ImageMagick-6/policy.xml /etc/ImageMagick-6/policy.xmlout

for i in *.pdf
do
    j=`basename $i .pdf`
    dir=`echo $j | sed s/.*-[0-9][0-9]_//g | sed s/_.*//g` #Crete the output directory
    convert -density 200 $j.pdf $j.png #Convert the whole pdf to images
    #Make the output directory
    mkdir -p ${dir}/plots/
    #Get all images by cropping the pdfs
    convert -crop 500x280+500+960 $j-0.png ${dir}/plots/$j-retail_and_recreation.png
    convert -crop 500x280+500+1280 $j-0.png ${dir}/plots/$j-grocery_and_pharmacy.png
    convert -crop 500x280+500+1600 $j-0.png ${dir}/plots/$j-parks.png
    convert -crop 500x280+440+120 $j-1.png  ${dir}/plots/$j-transit_stations.png
    convert -crop 500x280+440+440 $j-1.png ${dir}/plots/$j-workplace.png
    convert -crop 500x280+440+760 $j-1.png ${dir}/plots/$j-residential.png
    mv *.png $dir #Move all pdf converted images to the output directory
  done
