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
parser = argparse.ArgumentParser(description = '''Analyze the effect of population differences on county death tolls using an elastic net regression model. ''')
parser.add_argument('--data', nargs=1, type= str, default=sys.stdin, help = 'Path to all formatted data per county).')
parser.add_argument('--outdir', nargs=1, type= str, default=sys.stdin, help = 'Path to outdir.')



#####MAIN#####
args = parser.parse_args()
data = pd.read_csv(args.data[0])
outdir = args.outdir[0]
pdb.set_trace()
