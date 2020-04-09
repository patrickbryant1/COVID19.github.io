
for COUNTRY in "Denmark" "Norway" "Sweden"
do
  montage $COUNTRY'_cases.png' $COUNTRY'_deaths.png' $COUNTRY'_Rt.png' -tile 3x1 -geometry +2+2 $COUNTRY'.png'
done

montage -label '%f' "Denmark.png" "Norway.png" "Sweden.png"  -tile 1x3 -geometry +2+2 'all.png'
