import pandas as pd

def xlsx_to_csv(excel_path, csv_save_path, check=False):
    try:
        pd.read_excel(excel_path).to_csv(csv_save_path, index=None, header=True)
        if check:
            dataframe = pd.DataFrame(pd.read_csv(csv_save_path))
            dataframe
    except IOError as e:
        print(f"file type conversion unsupported: {e}")

def concatenate_csvs(save_path, csv_paths):
    df = pd.DataFrame()
    for path in csv_paths:
        df = pd.concat([df, pd.DataFrame(pd.read_csv(path))], ignore_index=True)
    with open(save_path, 'w') as f:
        f.write(df.to_csv())

def is_not_name_column(column: str, year):
    return not (column.__contains__(year) or column.__contains__('O = Observed') or column.__contains__('I = Imputed'))

# for energy_information_administration_data files 
def normalize_columns(csv_path):
    year = csv_path.split('/')[-2]
    lines = []
    with open(csv_path, 'r+') as f:
        lines = f.readlines()
        list_of_cols = list(list())
        index = 0
        #iterate through rows until hit row with number
        while is_not_name_column(lines[index], year):
            #populate all so none remain empty, then move lowest ones up
            out = lines[index].split(',')
            cur_actual_entry = ''

            for i in range(len(out)):
                if out[i] != '':
                    cur_actual_entry = out[i]
                else:
                    out[i] = cur_actual_entry

            if i != len(out)-1:
                out[i] += ','

            list_of_cols.append(out)
            index += 1
        
        #back populate upper rows until all full
        for i in range(len(list_of_cols)):
            cur_index = len(list_of_cols) - i - 1
            if cur_index - 1 >= 0:
                for j in range(len(list_of_cols[cur_index])):
                    #pass info back into previous row
                    list_of_cols[cur_index - 1][j] += '.' + list_of_cols[cur_index][j]

    for i in range(len(list_of_cols)):
        lines[i] = ','.join(["|" + val + "|" for val in list_of_cols[i]])
    #only care about the first entry in the list_of_cols array; delete the rest from the csv
    indices_to_remove = [i for i in range(1, len(list_of_cols))] 
    new_lines = []
    for i in range(len(lines)):
        if i not in indices_to_remove:
            new_lines.append(lines[i])

    with open(csv_path, 'w+') as f:
        f.writelines([line for line in new_lines])
