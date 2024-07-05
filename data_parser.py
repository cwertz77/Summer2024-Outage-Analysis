import pandas as pd

# read in csv file of yearly historical outage data
csv = pd.read_csv('eaglei_outages_2014.csv', index_col=0)
# drop non relevant data
csv=csv.where(csv['state']=='Illinois')
csv.dropna(inplace=True)
csv.sort_values('county',inplace=True)
csv.reset_index(inplace=True)
# csv.drop(columns='index',inplace=True)
csv.to_csv('outage_records/processed_illinois2014.csv')