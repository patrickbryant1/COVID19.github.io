data {
  int <lower=1> M; // number of countries
  int <lower=1> N; // number of weeks to model
  real deaths_at_drop_end[M]; // Deaths per million at drop end
  real observed_deaths[N, M]; // Observed deaths per million N = 4,5,6,7 and 8 weeks later
  real reg_deaths[N, M]; // Predicted deaths per million due to simple linear regression N = 4,5,6,7 and 8 weeks later
  real covariate1[M]; //retail_and_recreation at drop end
  real covariate2[M]; //grocery_and_pharmacy at drop end
  real covariate3[M]; //transit_stations at drop end
  real covariate4[M]; //workplace at drop end
  real covariate5[M]; //residential at drop end
  real deviation[N, M]; // Deviation between predicted deaths per million due to simple linear regression N = 4,5,6,7 and 8 weeks later
}

parameters {
  real<lower=0> alpha[5]; // reg_deaths * week delay * mob_change * alpha
  real phi;
}

//The transformed parameters are the prediction of the number of deaths
transformed parameters {
    real mobility_impact[M]; //Estimate the mobility impact
	//loop through all countries
    for (m in 1:M){ //need to consider the deaths_at_drop_end[m] when estimating the impact of alpha
        mobility_impact[m] =  tanh(3.14*(covariate1[m] * (alpha[1]) + covariate2[m] * (alpha[2]) +
        covariate3[m] * (alpha[3])+ covariate4[m] * (alpha[4]) - covariate5[m] * (alpha[5])));

        }
    }


//Deaths per million are inferred in our Bayesian posterior distribution.
model {
  phi ~ normal(0, 0.1);
  alpha ~ gamma(.5,1); //alpha distribution - mobility
	//Loop through countries
  for(m in 1:M){
	//Loop through all weeks to estimate
    deviation[,m] ~ normal_lpdf(mobility_impact[m],phi);
   }
}
