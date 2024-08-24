# Summer2024-Outage-Analysis

## EAGLE-I EIA Overlap
#### The data contained in this folder are JSON files, each with a key of a date and a time and the value associated with the times is a list of counties. The date is significant of a major outage disturbance noticed by the EIA, and the list of couties is representative of counties with customers that experienced a disturbance on that date, based on the EAGLE-I data.

## Sorted EAGLE-I
#### The data contained in this folder is EAGLE-I data for each year sorted in a CSV file. The original EAGLE-I data is the recorded amount of customers who experienced an outage every 15 minutes. The data available for each year is the county, zip code, time, date, and customers impacted. The original data is out of order in terms of dates and times. The python file, "county_data.py" utilizes a selection sort algorithm to sort the EAGLE-I data by date and time. 

## illinois_weather_data
#### The data in the illinois_weather data are CSV files of the major weather disturbances(hail, winter storm, thunder, etc.) in Illinois for each year. The files with "filtered" only contain rows that have measurements for the magnitude of a major disturbance. For example, the strong wind events given the measurement for the knots. The other files are the untouched CSV files of the weather data pulled from NOAA.

## Weather + EAGLE-I
#### The single CSV in the folder is a combination of the weather data and the EAGLE-I data. It is in the form of a timeline and puts a specific weather disturbance in the EAGLE-I data in order to see the aftermath of certain weather events. Due to the unnecessary amount of data points and length, this data doesn't fully serve our purpose, so it has been excluded from our final results.
