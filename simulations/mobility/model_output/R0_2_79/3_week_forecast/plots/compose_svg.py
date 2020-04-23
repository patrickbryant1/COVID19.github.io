#! /usr/bin/env python3
# -*- coding: utf-8 -*-


import argparse
import sys
import os
import glob
import pdb
from svgutils.compose import *

"""Compose svg figures
"""
countries =  ["Denmark", "Italy", "Germany","Spain", "United_Kingdom",
"France", "Norway", "Belgium", "Austria", "Sweden", "Switzerland"]
outdir='/home/patrick/COVID19.github.io/simulations/mobility/publication_figures/'
def ind_country_format(country):
    '''Compose cum cases, deaths per day and Rt
    '''
    Figure("18cm", "6cm",
              SVG(country+'_cumulative_cases.svg'),
              SVG(country+'_deaths.svg'),
              SVG(country+'_Rt.svg')
             ).tile(3, 1).save(country+'.svg')
#Compose each country
for country in countries:
    ind_country_format(country)

#Markers
Figure("12cm", "2.25cm",
          SVG('NPI_markers.svg'),
          SVG("mobility_markers.svg"),
         ).tile(2, 1).save('markers.svg')

#Figure 1 Italy and Sweden
Figure("18cm", "16cm",
        Panel(
            SVG('Italy.svg'),Text("Italy", 0,12, size=12, weight='bold')
            ),
        Panel(
            SVG('Sweden.svg'),Text("Sweden", 0, 0, size=12, weight='bold')
            ).move(0,180),
        Panel(
          SVG('markers.svg').move(0,360)
             )).save(outdir+'Figure1.svg')

#Figure 2 - forecast
Figure("16cm", "16cm",
          SVG('./forecast/Austria_forecast.svg'),
          SVG('./forecast/Belgium_forecast.svg'),
          SVG('./forecast/Denmark_forecast.svg'),
          SVG('./forecast/France_forecast.svg'),
          SVG('./forecast/Germany_forecast.svg'),
          SVG('./forecast/Italy_forecast.svg'),
          SVG('./forecast/Norway_forecast.svg'),
          SVG('./forecast/Spain_forecast.svg'),
          SVG('./forecast/Sweden_forecast.svg'),
          SVG('./forecast/Switzerland_forecast.svg'),
          SVG('./forecast/United_Kingdom_forecast.svg'),
         ).tile(3, 4).save(outdir+'Figure2.svg')
