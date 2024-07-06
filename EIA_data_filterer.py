import pandas as pd


#Advanced Meters
index_to_desc = {
    '0': 'Number AMR-Automated Meter Reading',
    '1': 'Number AMI-Advanced Metering Infrastructure',
    '2': 'Number Home Area Network',
    '3': 'Number Standard (non AMR/AMI) Meters',
    '4': 'Total Numbers of Meters',
    '5': 'Energy Served - AMI (MWh)',
    '6': 'Customers with Daily Digital Access',
    '7': 'Customers with Direct Load Control'
}

def filter_csv(csv_path):
    df = pd.read_csv(csv_path)
    illinois_df = pd.DataFrame()
    for i in range(len(df)):
        if df.iloc[i]['State'] == 'IL':
            copy = df.iloc[i]
            copied_row_df = pd.DataFrame([copy])
            illinois_df = pd.concat([illinois_df, copied_row_df], ignore_index=True) #reindex dataset
    for col in illinois_df.columns:
        for i in range(8):
            if col.__contains__(str(i)):
                illinois_df = illinois_df.rename(columns={col: '|' + col.replace(str(i), index_to_desc[str(i)]) + '|'})

    print(illinois_df)
    save_path = csv_path[:-4] + '_Illinois.csv'
    with open(save_path, 'w') as f:
        f.write(illinois_df.to_string())

for year in range(2014, 2023):
    filter_csv(f'/Users/irislitiu/work/WSU_Outage_Analysis/energy_information_administration_data/{year}/Advanced_Meters_{year}.csv')