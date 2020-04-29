data {
  int <lower=1> M; // number of countries
  int <lower=1> N0; // number of days for which to impute infections
  int<lower=1> N[M]; // days of observed data for country m. each entry must be <= N2
  int<lower=1> N2; // days of observed data + # of days to forecast
  real<lower=0> x[N2]; // index of days (starting at 1)
  real pop_frac_age[10,M]; //Population fractions per age in steps of 10 from 0 to 90+
  real death_frac_age[10,M]; //Death fractions per age in steps of 10 from 0 to 90+
  int deaths[N2, M]; // reported deaths -- the rows with i > N contain -1 and should be ignored
  matrix[N2, M] f; // h * s - change in fraction dead each day
  matrix[N2, M] covariate1; //retail_and_recreation
  matrix[N2, M] covariate2; //grocery_and_pharmacy
  matrix[N2, M] covariate3; //transit_stations
  matrix[N2, M] covariate4; //workplace
  matrix[N2, M] covariate5; //residential
  int EpidemicStart[M];
  real SI[N2]; // fixed pre-calculated SI using emprical data from Neil
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
    real convolution1; //value of integration
    real convolution2;
    real convolution3;
    real convolution4;
    real convolution5;
    real convolution6;
    real convolution7;
    real convolution8;
    real convolution9;
    real convolution10;
    matrix[N2, M] prediction1; //predict cases for each day for all countries
    matrix[N2, M] prediction2; //predict cases for each day for all countries
    matrix[N2, M] prediction3; //predict cases for each day for all countries
    matrix[N2, M] prediction4; //predict cases for each day for all countries
    matrix[N2, M] prediction5; //predict cases for each day for all countries
    matrix[N2, M] prediction6; //predict cases for each day for all countries
    matrix[N2, M] prediction7; //predict cases for each day for all countries
    matrix[N2, M] prediction8; //predict cases for each day for all countries
    matrix[N2, M] prediction9; //predict cases for each day for all countries
    matrix[N2, M] prediction10; //predict cases for each day for all countries
    matrix[N2, M] E_deaths = rep_matrix(0,N2,M); //sum of deaths over all age groups
    matrix[N2, M] Rt;
    real<lower=0> phi;
    phi = phi_mu+phi_tau*phi_eta; //non-centered representation of phi
	//loop through all countries
    for (m in 1:M){
    //Get Rt for country m
    //mu is the mean R for each country sampled in model
    //For covariates 1-4: if the covariate is negative = less mobility, R will be decreased
    //For covariate 5 (residential), the opposite is true. More mobility at home --> less spread. Why the sign is negative.
      Rt[,m] = mu[m] * exp(covariate1[,m] * (alpha[1]) + covariate2[,m] * (alpha[2]) +
      covariate3[,m] * (alpha[3])+ covariate4[,m] * (alpha[4]) - covariate5[,m] * (alpha[5]));
      //Cases
        prediction1[1:N0,m] = rep_vector(y[m],N0); // learn the number of cases in the first N0 days, here N0=6
      	prediction2[1:N0,m] = rep_vector(y[m],N0); //y is the index case
      	prediction3[1:N0,m] = rep_vector(y[m],N0);
      	prediction4[1:N0,m] = rep_vector(y[m],N0);
      	prediction5[1:N0,m] = rep_vector(y[m],N0);
      	prediction6[1:N0,m] = rep_vector(y[m],N0);
      	prediction7[1:N0,m] = rep_vector(y[m],N0);
      	prediction8[1:N0,m] = rep_vector(y[m],N0);
      	prediction9[1:N0,m] = rep_vector(y[m],N0);
      	prediction10[1:N0,m] = rep_vector(y[m],N0);

      	//for all days from 7 (1 after the cases in N0 days) to end of forecast
            for (i in (N0+1):N2) {
              convolution1=0;//reset
              convolution2=0;
              convolution3=0;
              convolution4=0;
              convolution5=0;
              convolution6=0;
              convolution7=0;
              convolution8=0;
              convolution9=0;
              convolution10=0;

      	//loop through all days up to current (integration)
          for(j in 1:(i-1)) { //Cases today due to cumulative probability, sum(cases*rel.change due to SI)
            convolution1 += prediction1[j,m]*SI[i-j];
            convolution2 += prediction2[j,m]*SI[i-j];
            convolution3 += prediction3[j,m]*SI[i-j];
            convolution4 += prediction4[j,m]*SI[i-j];
            convolution5 += prediction5[j,m]*SI[i-j];
            convolution6 += prediction6[j,m]*SI[i-j];
            convolution7 += prediction7[j,m]*SI[i-j];
            convolution8 += prediction8[j,m]*SI[i-j];
            convolution9 += prediction9[j,m]*SI[i-j];
            convolution10 += prediction10[j,m]*SI[i-j];
            }
            prediction1[i,m] = Rt[i,m] * convolution1; //Scale with average spread per case
            prediction2[i,m] = Rt[i,m] * convolution2;
            prediction3[i,m] = Rt[i,m] * convolution3;
            prediction4[i,m] = Rt[i,m] * convolution4;
            prediction5[i,m] = Rt[i,m] * convolution5;
            prediction6[i,m] = Rt[i,m] * convolution6;
            prediction7[i,m] = Rt[i,m] * convolution7;
            prediction8[i,m] = Rt[i,m] * convolution8;
            prediction9[i,m] = Rt[i,m] * convolution9;
            prediction10[i,m] = Rt[i,m] * convolution10;
            }

      //Deaths - use all cases, now that they are estimated
    	//Step through all days til end of forecast
        E_deaths[1,m]= 1e-9; //Start expectation - practically 0
        for (i in 2:N2){
          E_deaths[i,m]= 0; //ensure 0
          //Go through all days up to current
          for(j in 1:(i-1)){ //Deaths today due to cumulative probability, sum(deaths*rel.change due to f)
              E_deaths[i,m] += (prediction1[j,m]*death_frac_age[1,m]+prediction2[j,m]*death_frac_age[2,m]+
              prediction3[j,m]*death_frac_age[3,m]+prediction4[j,m]*death_frac_age[4,m]+prediction5[j,m]*death_frac_age[5,m]+
              prediction6[j,m]*death_frac_age[6,m]+prediction7[j,m]*death_frac_age[7,m]+prediction8[j,m]*death_frac_age[8,m]+
              prediction9[j,m]*death_frac_age[9,m]+prediction10[j,m]*death_frac_age[10,m])*f[i-j,m];
              //print(p)
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
  mu ~ normal(2.79, kappa); // R distribution, https://academic.oup.com/jtm/article/27/2/taaa021/5735319
  alpha ~ gamma(.5,1); //alpha distribution - mobility

	//Loop through countries
  for(m in 1:M){
	//Loop through from epidemic start to end of epidemic
    for(i in EpidemicStart[m]:N[m]){
       deaths[i,m] ~ neg_binomial_2_lpmf(E_deaths[i,m],phi);
       }
   }
  }
