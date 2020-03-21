from corona.regions import MAINLAND_CHINA
from corona.load import get_data_from_file
import scipy.optimize
import json
import numpy as np

data_submodule_path = "./corona/data/csse_covid_19_data/csse_covid_19_time_series/"
datafile_confirmed = data_submodule_path + "time_series_19-covid-Confirmed.csv"
datafile_deaths = data_submodule_path + "time_series_19-covid-Deaths.csv"
datafile_recovered = data_submodule_path + "time_series_19-covid-Recovered.csv"

recovered = get_data_from_file(datafile_recovered)
confirmed = get_data_from_file(datafile_confirmed)
dead = get_data_from_file(datafile_deaths)

entries = len(recovered.total)

recovered_china = recovered.by_region[MAINLAND_CHINA]
confirmed_china = confirmed.by_region[MAINLAND_CHINA]

recovered_row = confirmed.total - recovered_china
confirmed_row = confirmed.total - confirmed_china


def row_fit_function(x, a, b):
    return a * np.exp(b * x)


def row_fit_jacobian(x, a, b):
    return np.transpose([np.exp(b * x), a * x * np.exp(b * x)])


def china_fit_function(x, a, b, c):
    return a / (1 + np.exp(-b * (x - c)))


def china_fit_jacobian(x, a, b, c):
    return np.transpose(
        [
            1 / (1 + np.exp(-b * (x - c))),
            -a / ((1 + np.exp(-b * (x - c))) ** 2) * (c - x) * np.exp(-b * (x - c)),
            -a / ((1 + np.exp(-b * (x - c))) ** 2) * b * np.exp(-b * (x - c)),
        ]
    )

def generate_fits(x, y, start, p0, function, jacobian):
    result = []
    for i in range(start, len(x) + 1):
        popt, pcov = scipy.optimize.curve_fit(function, x[:i], y[:i], p0, jac=jacobian)
        result.append({"param": popt.tolist(), "err": np.sqrt(np.diag(pcov)).tolist()})
    return result

plot_start = 16

fit_data_x = np.arange(0, entries)

china_fits = generate_fits(
    fit_data_x,
    confirmed_china,
    plot_start,
    [80000, 0.4, 20],
    china_fit_function,
    china_fit_jacobian,
)

row_fits = generate_fits(
    fit_data_x,
    confirmed_row,
    plot_start,
    [10, 0.2],
    row_fit_function,
    row_fit_jacobian,
)

data = {
    "confirmed": confirmed.to_json(),
    "dead": dead.to_json(),
    "recovered": recovered.to_json(),
    "fits": {
        "china": china_fits,
        "row": row_fits
    }
}

data_json = json.dumps(data).encode()
