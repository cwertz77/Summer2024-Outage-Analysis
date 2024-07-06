import pandas as pd
import os


def convert_xlsx_to_csv(excel_path, csv_save_path, check=False):
    try:
        pd.read_excel(excel_path).to_csv(csv_save_path, index=None, header=True)
        if check:
            dataframe = pd.DataFrame(pd.read_csv(csv_save_path))
            dataframe
    except IOError as e:
        print(f"file type conversion unsupported: {e}")


root = '/Users/irislitiu/Downloads/2014/'
save_path = '/Users/irislitiu/work/WSU_Outage_Analysis/energy_information_administration_data/'
for filename in os.listdir(root):
    if filename.__contains__('.xlsx'):
        out_path = save_path + root.split('/')[-2] + '/' + filename.replace('xlsx', 'csv')
        with open(out_path, 'w') as f:
            f.write('')
        convert_xlsx_to_csv(root+filename, out_path)
