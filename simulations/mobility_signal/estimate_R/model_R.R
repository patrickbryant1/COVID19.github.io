#!/usr/bin/env Rscript
args = commandArgs(trailingOnly=TRUE)

epidemic_data=args[1]
country=args[2]
outdir=args[3]


library(EpiEstim)
#outdir="/home/patrick/results/viral_mutation_to_phenotype/R_estimates/"
#epidemic_data="/home/patrick/viral_mutation_to_phenotype/data/ecdc_20200505.csv"
#country="Spain"
#Read data
epidemic_df <- read.csv(epidemic_data)
#Get data per country
country_df <-epidemic_df[epidemic_df$countriesAndTerritories==country,]
#Sort on date
country_df <-country_df[order(as.Date(country_df$dateRep, format="%d/%m/%Y")),]
#Cumulative deaths
cum_deaths <-cumsum(country_df[,c("deaths") ])
#Select data 30 days before 10 cumulative deaths were observed
indices<-which(cum_deaths>=10)
start_i<-indices[1]-30
if (start_i<0){
  start_i<-0
}
end_i <-tail(indices, n=1)

country_df <- country_df[(start_i:end_i),]
#Get cases for modeling
country_cases <-country_df[,c("cases")]

#Fix case corrections by averaging the previous and subsequent days
adj_indices<-which(country_cases<0)
for(i in adj_indices){
  country_cases[i] = (country_cases[i-1]+country_cases[i+1])/2
}
#Estimate R
#R_estimate <- estimate_R(country_cases,
#method = "parametric_si", config = make_config(list(mean_si = 4.8, std_si = 2.3)))

#Variabel Serial Interval
R_estimate <-estimate_R(country_cases,  method="uncertain_si", config = make_config(list(mean_si = 7.5, std_mean_si = 2,min_mean_si = 1, max_mean_si = 8.4, std_si = 3.4, std_std_si = 1, min_std_si = 0.5, max_std_si = 4, n1 = 1000, n2 = 1000)))

#Plotting function
# custom results plotting function to avoid the ugly
# TableGrob messages returned by the plotting function in the
# EpiEstim package
plot_Ri <- function(estimate_R_obj) {
  p_I <- plot(estimate_R_obj, "incid", add_imported_cases = TRUE)  # plots the incidence
  p_SI <- plot(estimate_R_obj, "SI")  # plots the serial interval distribution
  p_Ri <- plot(estimate_R_obj, "R")
  return(gridExtra::grid.arrange(p_I, p_SI, p_Ri, ncol = 1))
}

#plot_Ri(R_estimate)

#Add the dates to the R estimates. The R estimate will start at index 7 due to the
#7-day sliding window
end_i<-length(country_df[,1])
dates<-country_df[(8:end_i),c("dateRep")]
#Out df
out_df<-R_estimate$R
out_df$date<-dates
#Define output name
outname<-paste(outdir,country,'_R_estimate.csv',sep="")
#Save results
write.csv(out_df,outname)
