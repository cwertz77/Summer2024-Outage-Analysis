from enum import Enum
import pandas as pd

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

def filter_csv(csv_path, type: sheet_type):
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
