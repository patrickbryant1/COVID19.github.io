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
  real<lower=0> y[M]; //
  //real<lower=0> phi; //variance scaling for neg binomial: var = mu^2/phi
  real<lower=0> phi_mu;
  real<lower=0> phi_tau;
  real<lower=0> phi_eta;
  real<lower=0> tau;
}

//The transformed parameters are the prediction of the number of deaths
transformed parameters {
    real pred_deaths; //value of integration
    matrix[N, M] pred_deaths = rep_matrix(0,N,M); //predict for each day for all countries
    real<lower=0> phi;
    phi = phi_mu+phi_tau*phi_eta; //non-centered representation of phi
	//loop through all countries
    for (m in 1:M){
      prediction[1:N0,m] = rep_vector(y[m],N0); // learn the number of cases in the first N0 days, here N0=6
						//y is the index case
	//mu is the mean R for each country sampled in model
	//For covariates 1-4: if the covariate is negative = less mobility, R will be decreased
  //For covariate 5 (residential), the opposite is true. More mobility at home --> less spread. Why the sign is negative.
        Rt[,m] = mu[m] * exp(covariate1[,m] * (alpha[1]) + covariate2[,m] * (alpha[2]) +
        covariate3[,m] * (alpha[3])+ covariate4[,m] * (alpha[4]) - covariate5[,m] * (alpha[5]));
	//for all days from 7 (1 after the cases in N0 days) to end of forecast
      for (i in (N0+1):N2) {
        convolution=0;//reset
	//loop through all days up to current
        for(j in 1:(i-1)) {
          convolution += prediction[j, m]*SI[i-j]; //Cases today due to cumulative probability, sum(cases*rel.change due to SI)
        }
        prediction[i, m] = Rt[i,m] * convolution; //Scale with average spread per case
      }

      E_deaths[1, m]= 1e-9; //Start expectation - practically 0
	//Step through all days til end of forecast
      for (i in 2:N2){
        E_deaths[i,m]= 0; //set to 0
        for(j in 1:(i-1)){
          E_deaths[i,m] += prediction[j,m]*f[i-j,m]; //Deaths today due to cumulative probability, sum(deaths*rel.change due to f)
							  //exp when neg_binomial_2_log_lpmf is used, otherwise without (when neg_binomial_2_log_lpmf
        }
      }
    }


}
//We assume that seeding of new infections begins 30 days before the day after a country has
//cumulatively observed 10 deaths. From this date, we seed our model with 6 sequential days of
//infections drawn from c 1,m , ... , c 6,m ~Exponential(τ), where τ~Exponential(0.03). These seed
//infections are inferred in our Bayesian posterior distribution.
model {
  //phi ~ normal(0,5); //variance scaling for neg binomial
  phi_mu ~ normal(0, 5);
  phi_tau ~ cauchy(0, 5);
  phi_eta ~ normal(0, 1); // implies phi ~ normal(phi_mu, phi_tau)
  kappa ~ normal(0,0.5); //std for R distr.
  mu ~ normal(2.79, kappa); // R distribution, https://academic.oup.com/jtm/article/27/2/taaa021/5735319
  alpha ~ gamma(.5,1); //alpha distribution - mobility
	//Loop through countries
  for(m in 1:M){
	//Loop through from epidemic start to end of epidemic
    for(i in EpidemicStart[m]:N[m]){
       //print(phi);
       deaths[i,m] ~ neg_binomial_2_lpmf(E_deaths[i,m],phi);
    }
   }
}
