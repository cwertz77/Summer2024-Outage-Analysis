import pandas as pd

def switch(lis,ind1, ind2):
    temp = lis[ind1]
    lis[ind1] = lis[ind2]
    lis[ind2] = temp



df = pd.read_csv("processed_illinois2023.csv")
data = [list(row) for row in df.values]


county = ["Adams"]
for i in range(len(data) - 1):
    min = data[i]
    for j in range(i, len(data)):
        if data[j][2] == county[len(county)-1]:
            if float(data[j][5][5:7]) < float(min[5][5:7]):
                min = data[j]
                continue
            elif float(data[j][5][5:7]) == float(min[5][5:7]):
                if float(data[j][5][8:10]) < float(min[5][8:10]):
                    min = data[j]
                    continue
                elif float(data[j][5][8:10]) == float(min[5][8:10]):
                    if float(data[j][5][11:13]) < float(min[5][11:13]):
                        min = data[j]
                        continue
                    elif float(data[j][5][11:13]) == float(min[5][11:13]):
                        if float(data[j][5][14:16]) < float(min[5][14:16]):
                            min = data[j]
                            continue

        else:
            break

    second = data.index(min)
    switch(data, i, second)

    if data[i+1][2] not in county:
        county.append(data[i+1][2])
        print(county)

import csv

with open('sortedEAGLE2023.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerows(data)


# b, c = a.iloc[0], a.iloc[1]
#
#
# temp = a.iloc[0].copy()
# a.iloc[0] = c
# a.iloc[1] = temp