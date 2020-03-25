import json
import math
import sched
import threading
import time

import git
import numpy as np
import scipy.optimize

from corona.load import get_data_from_file
from corona.regions import *


def exp_fit_function(x, a, b):
    return a * np.exp(b * x)


def exp_fit_jacobian(x, a, b):
    return np.transpose([np.exp(b * x), a * x * np.exp(b * x)])


def sig_fit_function(x, a, b, c):
    return a / (1 + np.exp(-b * (x - c)))


def sig_fit_jacobian(x, a, b, c):
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
        try:
            popt, pcov = scipy.optimize.curve_fit(
                function, x[:i], y[:i], p0, jac=jacobian, maxfev=1000
            )
            perr = np.sqrt(np.diag(pcov))
            for k in range(len(popt)):
                if math.isnan(popt[k]) or math.isinf(popt[k]):
                    popt[k] = 10e10
            for k in range(len(perr)):
                if math.isnan(perr[k]) or math.isinf(perr[k]):
                    perr[k] = 10e10
            result.append({"param": popt.tolist(), "err": perr.tolist()})
        except:
            result.append({"param": "undefined", "err": "undefined"})
    return result


submodule_path = "./corona/data/"
data_submodule_path = submodule_path + "csse_covid_19_data/csse_covid_19_time_series/"
datafile_confirmed = data_submodule_path + "time_series_19-covid-Confirmed.csv"
datafile_deaths = data_submodule_path + "time_series_19-covid-Deaths.csv"
datafile_recovered = data_submodule_path + "time_series_19-covid-Recovered.csv"


def prepare_data():
    recovered = get_data_from_file(datafile_recovered)
    confirmed = get_data_from_file(datafile_confirmed)
    dead = get_data_from_file(datafile_deaths)

    entries = len(recovered.total)

    recovered_china = recovered.by_region[MAINLAND_CHINA]
    dead_china = dead.by_region[MAINLAND_CHINA]
    confirmed_china = confirmed.by_region[MAINLAND_CHINA]

    recovered_row = confirmed.total - recovered_china
    dead_row = dead.total - dead_china
    confirmed_row = confirmed.total - confirmed_china

    temp_topcountries = []
    for i in range(len(confirmed.total)):
        topcountries_today = {}
        for c in confirmed.by_country.keys():
            topcountries_today.update(
                {
                    c: confirmed.by_country[c][i]
                    - dead.by_country[c][i]
                    - recovered.by_country[c][i]
                }
            )
            if len(topcountries_today) > 5:
                min_country = ""
                min_infected = 1e10
                for tc in topcountries_today.keys():
                    if topcountries_today[tc] < min_infected:
                        min_infected = topcountries_today[tc]
                        min_country = tc
                del topcountries_today[min_country]
        temp_topcountries.append(topcountries_today)

    temp_topcountries_json = json.dumps(temp_topcountries).encode()

    fit_start = 16
    fit_data_x = np.arange(0, entries)
    temp_datasets = {}

    for i in range(REGION_COUNT):
        temp_datasets.update(
            {
                region_names[i]: {
                    "confirmed": confirmed.by_region[i].tolist(),
                    "dead": dead.by_region[i].tolist(),
                    "recovered": recovered.by_region[i].tolist(),
                    "fits": {
                        "exp": generate_fits(
                            fit_data_x,
                            confirmed.by_region[i],
                            fit_start,
                            [10, 0.2],
                            exp_fit_function,
                            exp_fit_jacobian,
                        ),
                        "sig": generate_fits(
                            fit_data_x,
                            confirmed.by_region[i],
                            fit_start,
                            [np.max(confirmed.by_region[i]), 0.4, 20],
                            sig_fit_function,
                            sig_fit_jacobian,
                        ),
                    },
                }
            }
        )

    temp_datasets.update(
        {
            "row": {
                "confirmed": confirmed_row.tolist(),
                "dead": dead_row.tolist(),
                "recovered": recovered_row.tolist(),
                "fits": {
                    "exp": generate_fits(
                        fit_data_x,
                        confirmed_row,
                        fit_start,
                        [10, 0.2],
                        exp_fit_function,
                        exp_fit_jacobian,
                    ),
                    "sig": generate_fits(
                        fit_data_x,
                        confirmed_row,
                        fit_start,
                        [np.max(confirmed_row), 0.4, 20],
                        sig_fit_function,
                        sig_fit_jacobian,
                    ),
                },
            }
        }
    )

    for n in confirmed.by_country.keys():
        temp_datasets.update(
            {
                n.replace(" ", "_"): {
                    "confirmed": confirmed.by_country[n].tolist(),
                    "dead": dead.by_country[n].tolist(),
                    "recovered": recovered.by_country[n].tolist(),
                    "fits": {
                        "exp": generate_fits(
                            fit_data_x,
                            confirmed.by_country[n],
                            fit_start,
                            [10, 0.2],
                            exp_fit_function,
                            exp_fit_jacobian,
                        ),
                        "sig": generate_fits(
                            fit_data_x,
                            confirmed.by_country[n],
                            fit_start,
                            [np.max(confirmed.by_country[n]), 0.4, 30],
                            sig_fit_function,
                            sig_fit_jacobian,
                        ),
                    },
                }
            }
        )

    temp_datasets.update(
        {
            "global": {
                "confirmed": confirmed.total.tolist(),
                "dead": dead.total.tolist(),
                "recovered": recovered.total.tolist(),
            }
        }
    )

    temp_datasets_json = {}
    for k in temp_datasets.keys():
        temp_datasets_json.update({k: json.dumps(temp_datasets[k]).encode()})

    return (temp_topcountries_json, temp_datasets_json)


def update_data():
    print("Updating Corona Data")
    repo = git.cmd.Git("./corona/data")
    repo.fetch("--all")
    repo.reset("--hard", "origin/master")
    repo.pull("origin", "master")
    output = repo.checkout('master')
    print(output)

    print("Git Pull completed")

    topcountries_json, datasets_json = prepare_data()
    scheduler.enter(60, 1, update_data)

update_data()
topcountries_json, datasets_json = prepare_data()

scheduler = sched.scheduler(time.time, time.sleep)

scheduler.enter(60, 1, update_data)
t = threading.Thread(target=scheduler.run)
t.start()
