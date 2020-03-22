from corona.regions import *
import csv
import numpy as np


class Data:
    def __init__(self):
        self.by_region = []
        for i in range(REGION_COUNT):
            self.by_region.append(np.array([]))

        self.total = np.array([])
        self.by_country = {}

    def to_json(self):
        by_region_dict = {}
        for i in range(len(self.by_region)):
            by_region_dict.update({region_names[i]: self.by_region[i].tolist()})
        return {"by_region": by_region_dict, "total": self.total.tolist()}


def get_data_from_file(filename):
    data_raw = []
    with open(filename) as datafile:
        datafile_reader = csv.reader(datafile, delimiter=",", quotechar='"')
        for row in datafile_reader:
            data_raw.append(row)

    data = Data()
    for i in range(4, len(data_raw[0])):
        column_by_region = np.zeros(REGION_COUNT)
        column_by_country = {}
        for j in range(1, len(data_raw)):
            country = data_raw[j][1]
            if not column_by_country.__contains__(country):
                column_by_country.update({country: 0})
            column_by_country[country] += int(data_raw[j][i])

            if region_map.__contains__(country):
                region = region_map[country]
                if data_raw[j][i] != "":
                    column_by_region[region] += int(data_raw[j][i])
            else:
                print("could not find region for " + country)

        for k, v in column_by_country.items():
            if not data.by_country.__contains__(k):
                data.by_country.update({k:np.array([])})
            data.by_country[k] = np.append(data.by_country[k], v)

        column_total = 0
        for i in range(REGION_COUNT):
            data.by_region[i] = np.append(data.by_region[i], column_by_region[i])

            column_total += column_by_region[i]

        data.total = np.append(data.total, column_total)

    return data
