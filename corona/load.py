from corona.regions import *
import csv
import numpy as np

class Data:
    def __init__(self):
        self.by_region = []
        for i in range(REGION_COUNT):
            self.by_region.append(np.array([]))
        
        self.total = np.array([])

    def to_json(self):
        return {"by_region": [region.tolist() for region in self.by_region], "total": self.total.tolist()}

def get_data_from_file(filename):
    data_raw = []
    with open(filename) as datafile:
        datafile_reader = csv.reader(datafile, delimiter=",", quotechar="\"")
        for row in datafile_reader:
            data_raw.append(row)

    data = Data()
    for i in range(4, len(data_raw[0])):
        column_by_region = np.zeros(REGION_COUNT)

        for j in range(1, len(data_raw)):
            country = data_raw[j][1]
            if region_map.__contains__(country):
                region = region_map[country]
                if(data_raw[j][i] != ""):
                    column_by_region[region] += int(data_raw[j][i])
            else:
                print("could not find region for " + country)

        column_total = 0
        for i in range(REGION_COUNT):
            data.by_region[i] = np.append(data.by_region[i], column_by_region[i])

            column_total += column_by_region[i]

        data.total = np.append(data.total, column_total)

    return data