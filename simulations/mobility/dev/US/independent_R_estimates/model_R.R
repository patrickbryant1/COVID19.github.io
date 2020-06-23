#!/usr/bin/env Rscript
args = commandArgs(trailingOnly=TRUE)

epidemic_data=args[1]
country=args[2]
outdir=args[3]


library(EpiEstim)
#outdir="/home/patrick/results/COVID19/mobility_and_spread/US/EpiEstimR/"
#epidemic_data="./complete_case_df.csv"
#country="New_Hampshire"
if (grepl("_", country)){
  country = strsplit(country, "_")
  country = paste(country[[1]][1], country[[1]][2])
} 
#Read data
epidemic_df <- read.csv(epidemic_data)
#Get data per country
country_df <-epidemic_df[epidemic_df$region==country,]
#Sort on date 
country_df <-country_df[order(as.Date(country_df$date, format="%d/%m/%Y")),]

#Get cases for modeling
country_cases <-country_df[,c("cases")]

#Estimate R
R_estimate <- estimate_R(country_cases, method = "parametric_si", config = make_config(list(mean_si = 4.8, std_si = 2.3)))

#Variabel Serial Interval
#R_estimate <-estimate_R(country_cases,  method="uncertain_si", config = make_config(list(mean_si = 7.5, std_mean_si = 2,min_mean_si = 1, max_mean_si = 8.4, std_si = 3.4, std_std_si = 1, min_std_si = 0.5, max_std_si = 4, n1 = 1000, n2 = 1000)))

#Add the dates to the R estimates. The R estimate will start at index 7 due to the
#7-day sliding window
end_i<-length(country_df[,1])
dates<-country_df[(8:end_i),c("date")]
#Out df
out_df<-R_estimate$R
out_df$date<-dates
#Define output name
outname<-paste(outdir,country,'_R_estimate.csv',sep="")
#Save results
write.csv(out_df,outname)
