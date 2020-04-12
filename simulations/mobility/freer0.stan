data {
  int <lower=1> M; // number of countries
  int <lower=1> N0; // number of days for which to impute infections
  int<lower=1> N[M]; // days of observed data for country m. each entry must be <= N2
  int<lower=1> N2; // days of observed data + # of days to forecast
  real<lower=0> x[N2]; // index of days (starting at 1)
  int cases[N2,M]; // reported cases
  int deaths[N2, M]; // reported deaths -- the rows with i > N contain -1 and should be ignored
  matrix[N2, M] f; // h * s - change in fraction dead each day
  matrix[N2, M] covariate1; // straight line
  // matrix[N2, M] covariate1; //retail_and_recreation
  // matrix[N2, M] covariate2; //grocery_and_pharmacy
  // matrix[N2, M] covariate3; //transit_stations
  // matrix[N2, M] covariate4; //workplace
  // matrix[N2, M] covariate5; //residential
  int EpidemicStart[M];
  real SI[N2]; // fixed pre-calculated SI using emprical data from Neil
}

transformed data {
  real delta = 1e-5; //We’ll need to add a small positive term,δ to the diagonal of the covariance 			    //matrix in order to ensure that our covariance matrix remains positive definite.
}

parameters {
  real<lower=0> mu[M]; // intercept for Rt - hyperparam to be learned
  real<lower=0> alpha[5]; // Rt^exp-(sum(alpha))
  real<lower=0> kappa; //std of R
  real<lower=0> y[M]; //
  //real<lower=0> phi; //variance scaling for neg binomial: var = mu^2/phi
  real<lower=0> phi_mu;
  real<lower=0> phi_tau;
  real<lower=0> phi_eta;
  real<lower=0> tau;
}

//The transformed parameters are the prediction (cases) and E_deaths = (cases*f) due to cumulative probability
transformed parameters {
    real convolution; //value of integration
    matrix[N2, M] prediction = rep_matrix(0,N2,M); //predict for each day for all countries
    matrix[N2, M] E_deaths  = rep_matrix(0,N2,M);
    matrix[N2, M] Rt = rep_matrix(0,N2,M);
    real<lower=0> phi;
    phi = phi_mu+phi_tau*phi_eta; //non-centered representation of phi
	//loop through all countries
    for (m in 1:M){
      prediction[1:N0,m] = rep_vector(y[m],N0); // learn the number of cases in the first N0 days, here N0=6
						//y is the index case
	//mu is the mean R for each country sampled in model
	//For covariates 1-4: if the covariate is negative = less mobility, R will be decreased
  //For covariate 5 (residential), the opposite is true. More mobility at home --> less spread. Why the sign is negative.
        //Rt[,m] = mu[m] * exp(covariate1[,m] * (alpha[1]) + covariate2[,m] * (alpha[2]) +
        // covariate3[,m] * (alpha[3])+ covariate4[,m] * (alpha[4]) - covariate5[,m] * (alpha[5]));
        Rt[,m] = mu[m]* exp(covariate1[,m] * (alpha[1])) ;
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
  tau ~ exponential(0.03);
	//loop through countries
  for (m in 1:M){
      y[m] ~ exponential(1.0/tau); //seed for estimated number of cases in beginning of epidemic - why 1/tau?
  }
  //phi ~ normal(0,5); //variance scaling for neg binomial
  phi_mu ~ normal(0, 5);
  phi_tau ~ cauchy(0, 5);
  phi_eta ~ normal(0, 1); // implies phi ~ normal(phi_mu, phi_tau)
  kappa ~ normal(0,0.5); //std for R distr.
  mu ~ normal(2.4, kappa); // R distribution
  alpha ~ gamma(.5,1); //alpha distribution - NPI
	//Loop through countries
  for(m in 1:M){
	//Loop through from epidemic start to end of epidemic
    for(i in EpidemicStart[m]:N[m]){
       //print(phi);
       deaths[i,m] ~ neg_binomial_2_lpmf(E_deaths[i,m],phi);
    }
   }
}

//Out metrics - baseline, without R0 reduction
generated quantities {
    matrix[N2, M] lp0 = rep_matrix(1000,N2,M); // log-probability for LOO for the counterfactual model
    matrix[N2, M] lp1 = rep_matrix(1000,N2,M); // log-probability for LOO for the main model
    real convolution0;
    matrix[N2, M] prediction0 = rep_matrix(0,N2,M);
    matrix[N2, M] E_deaths0  = rep_matrix(0,N2,M);
    for (m in 1:M){
      prediction0[1:N0,m] = rep_vector(y[m],N0); // learn the number of cases in the first N0 days
      for (i in (N0+1):N2) {
        convolution0=0;
        for(j in 1:(i-1)) {
          convolution0 += prediction0[j, m]*SI[i-j]; // Correctd 22nd March
        }
        prediction0[i, m] = mu[m] * convolution0;
      }

      E_deaths0[1, m]= 1e-9;
      for (i in 2:N2){
        E_deaths0[i,m]= 0;
        for(j in 1:(i-1)){
          E_deaths0[i,m] += prediction0[j,m]*f[i-j,m];
        }
      }
      for(i in 1:N[m]){
        lp0[i,m] = neg_binomial_2_log_lpmf(deaths[i,m] | E_deaths[i,m],phi);
        lp1[i,m] = neg_binomial_2_log_lpmf(deaths[i,m] | E_deaths0[i,m],phi);
      }
    }

}
