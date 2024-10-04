import pandas as pd
from matplotlib import pyplot as plt
import numpy as np
import metric_calculations as mc

def fragility_by_wind():
    data=pd.DataFrame()
    for year in range(2015,2024):
        data=data._append(pd.read_csv(f'wind_and_eagle_I_csvs/{year}.csv'))
    data.replace(' ', np.nan, inplace=True)
    data.dropna(inplace=True)
    num_customers=list()
    percent_customers_out=list()
    for i in data.index:
        num_customers.append(mc.get_num_customers_affected(data.iloc[i]["county"]))
        percent_customers_out.append(data.iloc[i]['num_people_out']/num_customers[-1])
    data['percent_customers_out']=percent_customers_out
    data.to_csv("processed_wind_customer_outage.csv")
def power_quality_vulnerability():
    data=pd.read_csv('outage_records/metrics.csv')
    #only investigate 2023
    plt.scatter(data['saidi'],data['svi'])
    plt.show()
    breakpoint()


fragility_by_wind()