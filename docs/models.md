---
layout: page
title: Epidemic modeling
---

# Epidemic modeling

## R0 vs the final fraction infected
![R0_vs_tau](./assets/R0_vs_tau.png)

## Infection-to-onset: gamma(mean=5.1, variance=0.86)
shape (α) = 1/std^2

scale (β) = mean/shape = mean/(1/std^2) = mean*std^2

![ITO.png](./assets/ITO.png)

## Onset-to-death: gamma(18.8, 0.45)
![OTD.png](./assets/OTD.png)

## Survival Fraction for onset-to-death
![survival_fraction.png](./assets/survival_fraction.png)

## Infection-to-death
![ITD.png](./assets/ITD.svg)

## Serial interval distribution
To model the number of infections over time we need to specify a serial
interval distribution g with density g(τ), (the time between when a person gets infected and when they subsequently infect another other people), which we choose to be Gamma distributed: g ∼ Gamma (6.5,0.62).
![Serial.svg](./assets/Serial.svg)
