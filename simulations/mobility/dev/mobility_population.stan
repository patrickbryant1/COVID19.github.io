data {
  int<lower=1> M; // number of countries
  int<lower=1> N0; // number of days for which to impute infections
  int<lower=1> N[M]; // days of observed data for country m. each entry must be <= N2
  int<lower=1> N2; // days of observed data + # of days to forecast
  real<lower=0> x[N2]; // index of days (starting at 1)
  int deaths[N2, M]; // reported deaths -- the rows with i > N contain -1 and should be ignored
  matrix[N2, 9] f[M]; // h * s - change in fraction dead each day, 9 age groups
  matrix[N2, M] covariate1; //retail_and_recreation
  matrix[N2, M] covariate2; //grocery_and_pharmacy
  matrix[N2, M] covariate3; //transit_stations
  matrix[N2, M] covariate4; //workplace
  matrix[N2, M] covariate5; //residential
  int EpidemicStart[M];
  real SI[N2]; // fixed pre-calculated SI using emprical data from Neil
  int<lower=1> population_size [M];
}

transformed data {
  real delta = 1e-5; //We’ll need to add a small positive term,δ to the diagonal of the covariance 			    //matrix in order to ensure that our covariance matrix remains positive definite.
}

parameters {
  real<lower=0> mu1[M]; // intercept for Rt - hyperparam to be learned
  real<lower=0> mu2[M]; // intercept for Rt - hyperparam to be learned
  real<lower=0> mu3[M]; // intercept for Rt - hyperparam to be learned
  real<lower=0> mu4[M]; // intercept for Rt - hyperparam to be learned
  real<lower=0> mu5[M]; // intercept for Rt - hyperparam to be learned
  real<lower=0> mu6[M]; // intercept for Rt - hyperparam to be learned
  real<lower=0> mu7[M]; // intercept for Rt - hyperparam to be learned
  real<lower=0> mu8[M]; // intercept for Rt - hyperparam to be learned
  real<lower=0> mu9[M]; // intercept for Rt - hyperparam to be learned
  real<lower=0> alpha[5]; // Rt^exp(sum(alpha*alpha_scale*covariate))
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
    real cumulative_convolution; //For herd immunity
    matrix[N2, M] prediction[9]; //predict cases for each day for all countries

    matrix[N2, M] E_deaths[9]; //sum of deaths over all age groups
    matrix[N2, M] Rt[9]; //Rt per age group to model spread
    real<lower=0> phi;
    phi = phi_mu+phi_tau*phi_eta; //non-centered representation of phi
	//loop through all countries
  for (m in 1:M){ //Loop through all countries
    //Get Rt for country m
    //mu is the mean R for each country sampled in model
    //For covariates 1-4: if the covariate is negative = less mobility, R will be decreased
    //For covariate 5 (residential), the opposite is true. More mobility at home --> less spread. Why the sign is negative.
        //Define Rt, learned below
    Rt[1,:,m] = mu1[m] * exp(covariate1[,m] * (alpha[1]) + covariate2[,m] * (alpha[2]) + covariate3[,m] * (alpha[3])+ covariate4[,m] * (alpha[4]) - covariate5[,m] * (alpha[5]));
    Rt[2,:,m] = mu2[m] * exp(covariate1[,m] * (alpha[1]) + covariate2[,m] * (alpha[2]) + covariate3[,m] * (alpha[3])+ covariate4[,m] * (alpha[4]) - covariate5[,m] * (alpha[5]));
    Rt[3,:,m] = mu3[m] * exp(covariate1[,m] * (alpha[1]) + covariate2[,m] * (alpha[2]) + covariate3[,m] * (alpha[3])+ covariate4[,m] * (alpha[4]) - covariate5[,m] * (alpha[5]));
    Rt[4,:,m] = mu4[m] * exp(covariate1[,m] * (alpha[1]) + covariate2[,m] * (alpha[2]) + covariate3[,m] * (alpha[3])+ covariate4[,m] * (alpha[4]) - covariate5[,m] * (alpha[5]));
    Rt[5,:,m] = mu5[m] * exp(covariate1[,m] * (alpha[1]) + covariate2[,m] * (alpha[2]) + covariate3[,m] * (alpha[3])+ covariate4[,m] * (alpha[4]) - covariate5[,m] * (alpha[5]));
    Rt[6,:,m] = mu6[m] * exp(covariate1[,m] * (alpha[1]) + covariate2[,m] * (alpha[2]) + covariate3[,m] * (alpha[3])+ covariate4[,m] * (alpha[4]) - covariate5[,m] * (alpha[5]));
    Rt[7,:,m] = mu7[m] * exp(covariate1[,m] * (alpha[1]) + covariate2[,m] * (alpha[2]) + covariate3[,m] * (alpha[3])+ covariate4[,m] * (alpha[4]) - covariate5[,m] * (alpha[5]));
    Rt[8,:,m] = mu8[m] * exp(covariate1[,m] * (alpha[1]) + covariate2[,m] * (alpha[2]) + covariate3[,m] * (alpha[3])+ covariate4[,m] * (alpha[4]) - covariate5[,m] * (alpha[5]));
    Rt[9,:,m] = mu9[m] * exp(covariate1[,m] * (alpha[1]) + covariate2[,m] * (alpha[2]) + covariate3[,m] * (alpha[3])+ covariate4[,m] * (alpha[4]) - covariate5[,m] * (alpha[5]));

      //Cases
      for (p in 1:9){
        prediction[p,1:N0,m] = rep_vector(y[m],N0); // learn the number of cases in the first N0 days, here N0=6
  					                                      //y is the index case
      	//for all days from 7 (1 after the cases in N0 days) to end of forecast
        for (i in (N0+1):N2) {
              convolution=0; //reset
              cumulative_convolution = 0;
      	//loop through all days up to current (integration)
          for(j in 1:(i-1)) {
            convolution += prediction[p,j,m]*SI[i-j]; //Cases today due to cumulative probability, sum(cases*rel.change due to SI)
            cumulative_convolution += prediction[p,j,m];
            }
            prediction[p,i,m] = (1-(cumulative_convolution/population_size[m]))*Rt[p,i,m] * convolution; //Scale with average spread per case
            }

      //Deaths - use all cases, now that they are estimated
    	//Step through all days til end of forecast
        E_deaths[p,1,m]= 1e-9; //Start expectation - practically 0
        for (i in 2:N2){
          E_deaths[p,i,m]= 0; //ensure 0
          //Go through all days up to current
          for(j in 1:(i-1)){
              E_deaths[p,i,m] += prediction[p,j,m]*f[m,i-j,p]; //Deaths today due to cumulative probability, sum(deaths*rel.change due to f)
              }
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
  mu1 ~ normal(2.79, kappa); // R distribution, https://academic.oup.com/jtm/article/27/2/taaa021/5735319
  mu2 ~ normal(2.79, kappa);
  mu3 ~ normal(2.79, kappa);
  mu4 ~ normal(2.79, kappa);
  mu5 ~ normal(2.79, kappa);
  mu6 ~ normal(2.79, kappa);
  mu7 ~ normal(2.79, kappa);
  mu8 ~ normal(2.79, kappa);
  mu9 ~ normal(2.79, kappa);
  alpha ~ gamma(.5,1); //alpha distribution - mobility

	//Loop through countries
  for(m in 1:M){
	//Loop through from epidemic start to end of epidemic
    for(i in EpidemicStart[m]:N[m]){
       deaths[i,1] ~ neg_binomial_2_lpmf((E_deaths[1,i,m]+E_deaths[2,i,m]+E_deaths[3,i,m]+E_deaths[4,i,m]+
       E_deaths[5,i,m]+E_deaths[6,i,m]+E_deaths[7,i,m]+E_deaths[8,i,m]+E_deaths[9,i,m]),phi);
       }
   }
  }
