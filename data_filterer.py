from enum import Enum
import pandas as pd
import numpy as np

class sheet_type(Enum):
    ADV_METERS = 1,
    BAL_AUTH = 2,
    DEMAND_RESP = 3,
    DIST_SYST = 4,
    DYNAMIC_PRICING = 5,
    ENERGY_EFF = 6,
    FRAME = 7,
    MERGERS = 8,
    NET_METERING = 9,
    NON_NET_METERING = 10,
    OP_DATA = 11,
    RELIABILITY = 12,
    SALES_ULT_CUST = 13,
    SALES_ULT_CUST_CS = 14,
    SERV_TERR = 15,
    SHORT_FORM = 16,
    UTIL_DATA = 17

def filter_csv_EIA_dataset(csv_path, type: sheet_type):
    df = pd.read_csv(csv_path)
    illinois_df = pd.DataFrame()
    key = ''

    if type in [sheet_type.DEMAND_RESP, sheet_type.DYNAMIC_PRICING, sheet_type.ENERGY_EFF, sheet_type.NET_METERING, sheet_type.OP_DATA, sheet_type.RELIABILITY, sheet_type.SALES_ULT_CUST]:
        key = '|Utility Characteristics..State|'
    elif type == sheet_type.NON_NET_METERING or sheet_type.UTIL_DATA:
        key = '|Utility Characteristics.State|'
    elif type == sheet_type.SALES_ULT_CUST_CS:
        key = '|Utility Characteristics..STATE|'
    elif type == sheet_type.SERV_TERR or sheet_type.SHORT_FORM:
        key = '|State|'
    elif type == sheet_type.FRAME:
        key = 'Utility Name'
    else:
        key = 'State'

    for i in range(len(df)):
        if df.iloc[i][key] == 'IL' or (type == sheet_type.FRAME and (str(df.iloc[i][key]).__contains__('IL') or str(df.iloc[i][key]).__contains__('Illinois'))):
            copy = df.iloc[i]
            copied_row_df = pd.DataFrame([copy])
            illinois_df = pd.concat([illinois_df, copied_row_df], ignore_index=True) #reindex dataset

    save_path = csv_path[:-4] + '_Illinois.csv'
    with open(save_path, 'w') as f:
        f.write(illinois_df.to_csv())


def shift_data_to_correct_col(df, index, cur_col, new_col):
    cur_entry = df.at[index, cur_col]
    if not (pd.isna(cur_entry) or cur_entry == ''):
        df.at[index, new_col] = str(df.at[index, new_col]) + str(cur_entry)
        df.at[index, cur_col] = ''

def shift_data_to_correct_row(df, col, cur_row, new_row):
    cur_entry = df.at[cur_row, col]
    if not (pd.isna(cur_entry) or cur_entry == ''):
        df.at[new_row, col] = str(df.at[cur_row, col]) + ' ' + str(df.at[new_row, col])
        df.at[cur_row, col] = ''

def get_num_empty_entries_in_row(df, index):
    vals = list(df.iloc[index].values)
    empty_entries = filter(lambda e: isinstance(e, float) and np.isnan(e), vals)
    return len(list(empty_entries))

# Major Disturbances and Unusual Occurrences dataset
def reformat(csv_path, filtered_save_path, year):
    df = pd.read_csv(csv_path)
    illinois_df = pd.DataFrame()
    skip_counter = 0

    for i in range(len(df)):
        # Remove duplicate table names (skip next 3 rows - duplicate column names)
        if skip_counter > 0:
            skip_counter -= 1
            continue
        if str(df.iloc[i][0]).__contains__(f'Table B.2 Major Disturbances and Unusual Occurrences, {year}'):
            skip_counter = 3
            continue
    
        # Shift cases: didn't all fit into one entry (column: Area Affected, Type of Disturbance)
        num_empty = get_num_empty_entries_in_row(df, i)
        print(f'num rows empty: {num_empty}')
        if len(df.iloc[i]) - num_empty <= 2:
            if df.iloc[i]['Area Affected'] != '':
                shift_data_to_correct_row(df, 'Area Affected', i, i+1)
            if df.iloc[i]['Type of Disturbance'] != '':
                shift_data_to_correct_row(df, 'Type of Disturbance', i, i+1)
        else:
            illinois_df = pd.concat([illinois_df, pd.DataFrame([df.iloc[i]])], ignore_index=True)

    # Clean up csv by shifting any entries in the empty column to 'Duration'
    for i in range(len(illinois_df)):
        for col in illinois_df.columns:
            print(col)
            if col == 'Unnamed: 7':
                shift_data_to_correct_col(illinois_df, i, col, 'Duration')
    
    with open(filtered_save_path, 'w+') as f:
        f.write(illinois_df.to_csv())

def filter_disturbances(csv_path, save_path):
    formatted_df = pd.read_csv(csv_path)
    illinois_df = pd.DataFrame()
    for i in range(len(formatted_df)):
        if str(formatted_df.iloc[i]['Area Affected']).__contains__('Illinois'):
            copy = formatted_df.iloc[i]
            copied_row_df = pd.DataFrame([copy])
            illinois_df = pd.concat([illinois_df, copied_row_df], ignore_index=True) #reindex dataset

    with open(save_path, 'w') as f:
        f.write(illinois_df.to_csv())

def filter_weather_events(weather_path, save_path, keywords):
    cur_df = pd.read_csv(weather_path)
    filtered_df = pd.DataFrame()
    for i in range(len(cur_df)):
        cur_entry = str(cur_df.iloc[i]['EVENT_TYPE'])
        for key in keywords:
            if cur_entry.__contains__(key):
                copy = pd.DataFrame([cur_df.iloc[i]])
                filtered_df = pd.concat([filtered_df, copy], ignore_index=True)
                break
    with open(save_path, 'w') as f:
        f.write(filtered_df.to_csv())

'''for i in range(2016,2025):
    filter_weather_events(f"illinois_weather_data/weather_{i}.csv", f"illinois_weather_data/wind_events_{i}.csv", ["Wind", "Tornado"])
'''

def filter_repeats(outage_data, save_path):
    csv = pd.read_csv(outage_data, index_col=0)
    no_repeats_df = pd.DataFrame()
    start_time = ""
    
    for index in range(1, len(csv)):
        percent_done = index / len(csv) * 100
        print(f'on iteration {index}; percent done: {percent_done}%')
        cols = ["county", "state", "customers_out"]
        
        if all(csv.iloc[index][col] == csv.iloc[index-1][col] for col in cols):
            if start_time == "":
                start_time = csv.iloc[index]["run_start_time"]
        else:
            last_time = pd.to_datetime(csv.iloc[index-1]["run_start_time"])
            end_time = last_time + pd.Timedelta(minutes=15)
            end_time = end_time.strftime('%Y-%m-%d %H:%M:%S')

            cur_col = csv.iloc[index-1].copy()
            cur_col["run_start_time"] = start_time if start_time else cur_col["run_start_time"]
            cur_col["run_end_time"] = end_time
            no_repeats_df = pd.concat([no_repeats_df, cur_col.to_frame().T], ignore_index=True)

            start_time = ""

    if start_time:
        last_time = pd.to_datetime(csv.iloc[-1]["run_start_time"])
        end_time = last_time + pd.Timedelta(minutes=15)
        end_time = end_time.strftime('%Y-%m-%d %H:%M:%S')

        cur_col = csv.iloc[-1].copy()
        cur_col["run_start_time"] = start_time if start_time else cur_col["run_start_time"]
        cur_col["run_end_time"] = end_time
        no_repeats_df = pd.concat([no_repeats_df, cur_col.to_frame().T], ignore_index=True)

    with open(save_path, 'w+') as f:
        f.write(no_repeats_df.to_csv())

'''
for i in range(2015, 2024):
    filter_repeats(f'./outage_records/processed_illinois{i}.csv',
                f'./outage_records/filtered_{i}.csv')
'''