OUTDIR=. #/home/patrick/COVID19.github.io/docs/assets
montage *pred_vs_true_per100000.png -tile 3x2 -geometry +2+2 $OUTDIR/all_pred_vs_true.png
montage *top_bottom10_enet_coefs.png -tile 3x2 -geometry +2+2 $OUTDIR/all_top_bottom10.png
