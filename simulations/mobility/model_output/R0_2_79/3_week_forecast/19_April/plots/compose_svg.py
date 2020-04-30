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
Figure("18cm", "2.25cm",
          SVG('NPI_markers.svg'),
          SVG("mobility_markers.svg"),
           SVG("foreacast_markers.svg"),
         ).tile(3, 1).save('markers.svg')

#Figure 1 Italy and Sweden
Figure("18cm", "16cm",
        Panel(
            SVG('Italy.svg'),Text("Italy", 310,10, size=10,weight='bold', font='Times New Roman')
            ),
        Panel(
            SVG('Sweden.svg'),Text("Sweden", 310, 5, size=10,weight='bold', font='Times New Roman')
            ).move(0,180),
        Panel(
          SVG('markers.svg').move(0,360)
             )).save(outdir+'Figure1.svg')

#Figure 2 - forecast
Figure("14cm", "14cm",
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


#Supplementary material
#Figure S1 - cum cases/deaths per day/Rt
#Part 1
y_move=0
text_x=310
text_y=5
Figure("18cm", "29cm",
        Panel(
             SVG('Austria.svg'),Text("Austria", text_x,text_y, size=10,weight='bold', font='Times New Roman')
            ).move(0,y_move),
         Panel(
              SVG('Belgium.svg'),Text("Belgium", text_x,text_y, size=10,weight='bold', font='Times New Roman')
             ).move(0,y_move*2),
         Panel(
              SVG('Denmark.svg'),Text("Denmark", text_x,text_y, size=10,weight='bold', font='Times New Roman')
             ).move(0,y_move*3),
         Panel(
              SVG('France.svg'),Text("France", text_x,text_y, size=10,weight='bold', font='Times New Roman')
             ).move(0,y_move*4),
        Panel(
             SVG('Germany.svg'),Text("Germany", text_x,text_y, size=10,weight='bold', font='Times New Roman')
            ).move(0,y_move*5)
         ).tile(1, 6).save(outdir+'FigureS1_part1.svg')
Figure("18cm", "29cm",
        Panel(
            SVG('markers.svg')
            ),
        Panel(
            SVG(outdir+'FigureS1_part1.svg')
            ).move(0,90)
        ).save(outdir+'FigureS1_part1.svg')

#Part 2
Figure("18cm", "29cm",
        Panel(
             SVG('Italy.svg'),Text("Italy", text_x,10, size=10,weight='bold', font='Times New Roman')
            ),
         Panel(
              SVG('Norway.svg'),Text("Norway", text_x,text_y, size=10,weight='bold', font='Times New Roman')
             ).move(0,y_move),
         Panel(
              SVG('Spain.svg'),Text("Spain", text_x,text_y, size=10,weight='bold', font='Times New Roman')
             ).move(0,y_move*2),
         Panel(
              SVG('Sweden.svg'),Text("Sweden", text_x,text_y, size=10,weight='bold', font='Times New Roman')
             ).move(0,y_move*3),
        Panel(
             SVG('Switzerland.svg'),Text("Switzerland", text_x,text_y, size=10,weight='bold', font='Times New Roman')
            ).move(0,y_move*4),
        Panel(
             SVG('United_Kingdom.svg'),Text("United Kingdom", text_x,text_y, size=10,weight='bold', font='Times New Roman')
            ).move(0,y_move*5)
         ).tile(1, 6).save(outdir+'FigureS1_part2.svg')

#Figure S2 - forecast for ICL model
Figure("14cm", "14cm",
          SVG('/home/patrick/COVID19.github.io/simulations/icl_model/model_output/3_week_forecast/plots/forecast/Austria_forecast.svg'),
          SVG('/home/patrick/COVID19.github.io/simulations/icl_model/model_output/3_week_forecast/plots/forecast/Belgium_forecast.svg'),
          SVG('/home/patrick/COVID19.github.io/simulations/icl_model/model_output/3_week_forecast/plots/forecast/Denmark_forecast.svg'),
          SVG('/home/patrick/COVID19.github.io/simulations/icl_model/model_output/3_week_forecast/plots/forecast/France_forecast.svg'),
          SVG('/home/patrick/COVID19.github.io/simulations/icl_model/model_output/3_week_forecast/plots/forecast/Germany_forecast.svg'),
          SVG('/home/patrick/COVID19.github.io/simulations/icl_model/model_output/3_week_forecast/plots/forecast/Italy_forecast.svg'),
          SVG('/home/patrick/COVID19.github.io/simulations/icl_model/model_output/3_week_forecast/plots/forecast/Norway_forecast.svg'),
          SVG('/home/patrick/COVID19.github.io/simulations/icl_model/model_output/3_week_forecast/plots/forecast/Spain_forecast.svg'),
          SVG('/home/patrick/COVID19.github.io/simulations/icl_model/model_output/3_week_forecast/plots/forecast/Sweden_forecast.svg'),
          SVG('/home/patrick/COVID19.github.io/simulations/icl_model/model_output/3_week_forecast/plots/forecast/Switzerland_forecast.svg'),
          SVG('/home/patrick/COVID19.github.io/simulations/icl_model/model_output/3_week_forecast/plots/forecast/United_Kingdom_forecast.svg'),
         ).tile(3, 4).save(outdir+'FigureS2.svg')

#Figure S3 - LOO alphas
Figure("18cm", "26cm",
          SVG('./LOO/retail and recreation.svg'),
          SVG('./LOO/grocery and pharmacy.svg'),
          SVG('./LOO/transit stations.svg'),
          SVG('./LOO/workplace.svg'),
          SVG('./LOO/residential.svg'),
         ).tile(2, 3).save(outdir+'FigureS4.svg')
