data {
  int <lower=1> M; // number of countries
  int <lower=1> N; // number of weeks to model
  int deaths_at_drop_end[M]; // Deaths per million at drop end
  int observed_deaths[N, M]; // Observed deaths per million N = 4,5,6,7 and 8 weeks later
  int reg_deaths[N, M]; // Predicted deaths per million duu to simple linear regression N = 4,5,6,7 and 8 weeks later
  real covariate1[M] ; //retail_and_recreation at drop end
  real covariate2[M]; //grocery_and_pharmacy at drop end
  real covariate3[M]; //transit_stations at drop end
  real covariate4[M]; //workplace at drop end
  real covariate5[M]; //residential at drop end
}

parameters {
  real<lower=0> alpha[5]; // Rt^exp(sum(alpha))
  real<lower=0> kappa; //std of R
  real<lower=0> phi; //variance scaling for neg binomial: var = mu^2/phi
}

//The transformed parameters are the prediction of the number of deaths
transformed parameters {
    matrix[N, M] E_deaths = rep_matrix(0,N,M); //Estimate deaths for each day for all countries
    real<lower=0> phi;
    phi = phi_mu+phi_tau*phi_eta; //non-centered representation of phi
	//loop through all countries
    for (m in 1:M){ //need to consider the deaths_at_drop_end[m] when estimating the impact of alpha
        mobility_impact[,m] = covariate1[,m] * (alpha[1]) + covariate2[,m] * (alpha[2]) +
        covariate3[,m] * (alpha[3])+ covariate4[,m] * (alpha[4]) - covariate5[,m] * (alpha[5]);

	//Step through all weeks
      for (i in 1:N2){
          E_deaths[i,m] = reg_deaths[i,m]*i*mobility_impact[,m]; //Deaths per million i weeks later
        }                                                        //Include i to capture delay impact
      }
    }


}
//Deaths per million are inferred in our Bayesian posterior distribution.
model {
  phi ~ normal(0,1); //variance scaling for neg binomial
  mobility_impact ~ normal(0, 1); // Mobility impact
  alpha ~ gamma(.5,1); //alpha distribution - mobility
	//Loop through countries
  for(m in 1:M){
	//Loop through all weeks to estimate
    for(i in 1:N){
       observed_deaths[i,m] ~ neg_binomial_2_lpmf(E_deaths[i,m],phi);
    }
   }
}
