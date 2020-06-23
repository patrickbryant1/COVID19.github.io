#! /usr/bin/env python3
# -*- coding: utf-8 -*-


import argparse
import sys
import os
import glob
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

import pdb



#Arguments for argparse module:
parser = argparse.ArgumentParser(description = '''Format data from JHS to use in EpiEstim R estimates''')
parser.add_argument('--indir', nargs=1, type= str, default=sys.stdin, help = 'Path to EpiEstim R estimates per state.')
parser.add_argument('--outdir', nargs=1, type= str, default=sys.stdin, help = 'Path to outdir.')


#####MAIN#####
args = parser.parse_args()
indir = args.indir[0]
outdir = args.outdir[0]
#Read data
all_R = pd.DataFrame()
estimates = glob.glob(indir+'*.csv')
for file in estimates:
    state = file.split('/')[-1].split('_')[0]
    state_R = pd.read_csv(file)
    state_R['state'] = state
    #Append data to final df
    all_R = complete_df.append(state_R, ignore_index=True)

pdb.set_trace()
