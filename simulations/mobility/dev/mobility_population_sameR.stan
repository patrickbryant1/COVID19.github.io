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
  real<lower=0> mu[M]; // intercept for Rt - hyperparam to be learned
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
    matrix[N2, M] cumulative_cases; //For herd immunity
    matrix[N2, M] prediction; //predict cases for each day for all countries
    matrix[N2, M] E_deaths; //sum of deaths over all age groups
    matrix[N2, M] Rt; //Rt per age group to model spread
    real<lower=0> phi;
    phi = phi_mu+phi_tau*phi_eta; //non-centered representation of phi
	//loop through all countries
  for (m in 1:M){ //Loop through all countries
    //Get Rt for country m
    //mu is the mean R for each country sampled in model
    //For covariates 1-4: if the covariate is negative = less mobility, R will be decreased
    //For covariate 5 (residential), the opposite is true. More mobility at home --> less spread. Why the sign is negative.
        //Define Rt, learned below
        Rt[:,m] = mu[m] * exp(covariate1[,m] * (alpha[1]) + covariate2[,m] * (alpha[2]) +
        covariate3[,m] * (alpha[3])+ covariate4[,m] * (alpha[4]) - covariate5[,m] * (alpha[5]));

      //Cases
      //initial seed
      prediction[1:N0,m] = rep_vector(y[m],N0); // learn the number of cases in the first N0 days, here N0=6
  					                                      //y is the index case

      	//for all days from 7 (1 after the cases in N0 days) to end of forecast
        for (i in (N0+1):N2) {
          convolution=0; //reset
          Rt[i,m] = Rt[i,m]*(1-(cumulative_cases[i-1,m]/population_size[m]))
      	//loop through all days up to current
          for(j in 1:(i-1)){
              convolution += prediction[j,m]*SI[i-j]; //Cases today due to cumulative probability, sum(cases*rel.change due to SI)
                                                      //i-j since that will be the fraction infected left from day j on day i
              cumulative_cases[i,m] += prediction[j,m];
          }
          prediction[i,m] = Rt[i,m] * convolution; //Scale with average spread per case
        }


      //Deaths - use all cases, now that they are estimated
    	//Step through all days til end of forecast
        E_deaths[1,m]= 1e-9; //Start expectation - practically 0
        for (i in 2:N2){
          E_deaths[i,m]= 0; //ensure 0
          //Go through all days up to current
          for(j in 1:(i-1)){
            E_deaths[i,m] += prediction[j,m]/9*(f[m,i-j,1]+f[m,i-j,2]+f[m,i-j,3]+f[m,i-j,4]+f[m,i-j,5]
            +f[m,i-j,6]+f[m,i-j,7]+f[m,i-j,8]+f[m,i-j,9]); //Deaths today due to cumulative probability, sum(deaths*rel.change due to f)
          }
        }
  } //country end
} //transformed params end


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
  mu ~ normal(2.79, kappa); // R distribution, https://academic.oup.com/jtm/article/27/2/taaa021/5735319
  alpha ~ gamma(.5,1); //alpha distribution - mobility

	//Loop through countries
  for(m in 1:M){
	//Loop through from epidemic start to end of epidemic
    for(i in EpidemicStart[m]:N[m]){
       deaths[i,1] ~ neg_binomial_2_lpmf(E_deaths[i,m],phi);
       }
   }
  }
