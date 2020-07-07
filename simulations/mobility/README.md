This directory contains information on how to model the COVID-19 development using mobilie phone mobility data from Google mobility reports.

The data folder contains all data necessary to run the initial analysis.

The script model.sh runs mobility_model.py which runs MCMC simulations as defined
in mobility.stan

The estimate_R folder contains a runscript for running estimates of the basic reproductive number with the EpiEstim R package.

The analysis folder contains runscripts for analyzing the results, including visualization of the modeled output, Leave One out Analysis, forecast validation and correlations with estimates of the basic reproductive number from EpiEstim .

The model output directory contains all results from the modeling.
