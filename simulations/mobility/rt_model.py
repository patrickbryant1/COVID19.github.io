#! /usr/bin/env python3
# -*- coding: utf-8 -*-


import sys
import os
import glob
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from scipy.stats import gamma
import numpy as np
import seaborn as sns

import pdb

#Model Rt as a function of R0*exp(sum(cov*alpha)) with varying scaling of the residential parameter
#This will exemplify which sign the residential mobility change must have (negative)
R0 = 2.4

covariates = pd.read_csv('data/mobility.csv')
#Covariate names
covariate_names = ['retail_and_recreation','grocery_and_pharmacy','transit_stations','workplace','residential']
country = 'Sweden'
country_cov = covariates[covariates['Country']==country]

alpha = np.arange(0,1.1,0.1)
fig, ax = plt.subplots(figsize=(4, 4))
for s in [1,5,10]:
    Rt1 = []
    Rt2 = []
    for a in alpha:
        cov_sum1 = country_cov['retail_and_recreation'].values[0]+country_cov['grocery_and_pharmacy'].values[0]+country_cov['transit_stations'].values[0]+country_cov['workplace'].values[0]-s*country_cov['residential'].values[0]
        print(cov_sum1)
        cov_sum2 = country_cov['retail_and_recreation'].values[0]+country_cov['grocery_and_pharmacy'].values[0]+country_cov['transit_stations'].values[0]+country_cov['workplace'].values[0]+(1/s)*country_cov['residential'].values[0]
        print(cov_sum2)
        Rt1.append(R0*np.exp(a*(cov_sum1)))
        Rt2.append(R0*np.exp(a*(cov_sum2)))
    ax.plot(alpha,Rt1, label = str(s)+' residential -')
    ax.plot(alpha,Rt2, label = str(1/s)+' residential +')
ax.legend()
ax.set_xlabel('alpha')
ax.set_ylabel('Rt')
plt.tight_layout()
fig.savefig('model_output/plots/Rt_model.png', format='png')
