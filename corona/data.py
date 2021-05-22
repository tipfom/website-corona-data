import json
import math
import sched
import threading
import time
from datetime import date, datetime
from importlib import reload

import git
import numpy as np
import scipy.optimize

import corona.fetch_bno
import corona.fetch_tests
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
                function, x[:i], y[:i], p0, jac=jacobian, maxfev=10000
            )
            perr = np.sqrt(np.diag(pcov))
            done = False
            for k in range(len(popt)):
                if math.isnan(popt[k]) or math.isinf(popt[k]):
                    result.append({"param": "undefined", "err": "undefined"})
                    done = True
                    break
            if done:
                break
            for k in range(len(perr)):
                if math.isnan(perr[k]) or math.isinf(perr[k]):
                    result.append({"param": "undefined", "err": "undefined"})
                    done = True
                    break
            if done:
                break
            result.append({"param": popt.tolist(), "err": perr.tolist()})
        except:
            result.append({"param": "undefined", "err": "undefined"})
    return result


submodule_path = "./data/"
data_submodule_path = submodule_path + "csse_covid_19_data/csse_covid_19_time_series/"
datafile_confirmed = data_submodule_path + "time_series_covid19_confirmed_global.csv"
datafile_deaths = data_submodule_path + "time_series_covid19_deaths_global.csv"
datafile_recovered = data_submodule_path + "time_series_covid19_recovered_global.csv"

last_tests_data = None
last_tests_data_refresh = date.today().isoformat()
last_serious_data = None
last_serious_data_refresh = date.today().isoformat()


def prepare_data():
    global last_tests_data
    global last_tests_data_refresh
    global last_serious_data
    global last_serious_data_refresh

    recovered = get_data_from_file(datafile_recovered)
    confirmed = get_data_from_file(datafile_confirmed)
    dead = get_data_from_file(datafile_deaths)

    entries = len(confirmed.total)

    recovered_china = recovered.by_region[MAINLAND_CHINA]
    dead_china = dead.by_region[MAINLAND_CHINA]
    confirmed_china = confirmed.by_region[MAINLAND_CHINA]

    recovered_row = confirmed.total[: len(recovered_china)] - recovered_china
    dead_row = dead.total - dead_china
    confirmed_row = confirmed.total - confirmed_china

    fit_start = 16
    fit_data_x = np.arange(0, entries)

    corona.fetch_bno = reload(corona.fetch_bno)
    serious_data = {}
    try:
        serious_data = corona.fetch_bno.try_get_bno_seriouscases()
    except:
        pass
    if len(serious_data) == 0:
        print("serious cases pull failed")
        serious_data = last_serious_data
    else:
        last_serious_data = serious_data
        last_serious_data_refresh = date.today().isoformat()

    corona.fetch_tests = reload(corona.fetch_tests)
    tests_data = {}
    try:
        tests_data = corona.fetch_tests.try_get_tests()
    except:
        pass
    if len(tests_data) == 0:
        print("tests pull failed")
        tests_data = last_tests_data
    else:
        last_tests_data = tests_data
        last_tests_data_refresh = date.today().isoformat()

    temp_overview_dataset = {}
    temp_detail_datasets = {}

    for i in range(REGION_COUNT):
        temp_detail_datasets.update(
            {
                region_names[i]: {
                    "exp": generate_fits(
                        fit_data_x,
                        confirmed.by_region[i],
                        fit_start,
                        [confirmed.by_region[i][0], 0.1],
                        exp_fit_function,
                        exp_fit_jacobian,
                    ),
                    "sig": generate_fits(
                        fit_data_x,
                        confirmed.by_region[i],
                        fit_start,
                        [np.max(confirmed.by_region[i]), 0.2, len(confirmed.by_region[i]) / 2],
                        sig_fit_function,
                        sig_fit_jacobian,
                    ),
                }
            }
        )
        temp_overview_dataset.update(
            {
                region_names[i]: {
                    "confirmed": confirmed.by_region[i].tolist(),
                    "dead": dead.by_region[i].tolist(),
                    "recovered": recovered.by_region[i].tolist(),
                }
            }
        )

    temp_detail_datasets.update(
        {
            "row": {
                "exp": generate_fits(
                    fit_data_x,
                    confirmed_row,
                    fit_start,
                    [confirmed_row[0], 0.1],
                    exp_fit_function,
                    exp_fit_jacobian,
                ),
                "sig": generate_fits(
                    fit_data_x,
                    confirmed_row,
                    fit_start,
                    [np.max(confirmed_row), 0.2, len(confirmed_row) / 2],
                    sig_fit_function,
                    sig_fit_jacobian,
                ),
            }
        }
    )
    temp_overview_dataset.update(
        {
            "row": {
                "confirmed": confirmed_row.tolist(),
                "dead": dead_row.tolist(),
                "recovered": recovered_row.tolist(),
            }
        }
    )

    for n in confirmed.by_country.keys():
        temp_detail_datasets.update(
            {
                n.replace(" ", "_"): {
                    "exp": generate_fits(
                        fit_data_x,
                        confirmed.by_country[n],
                        fit_start,
                        [confirmed.by_country[n][0], 0.1],
                        exp_fit_function,
                        exp_fit_jacobian,
                    ),
                    "sig": generate_fits(
                        fit_data_x,
                        confirmed.by_country[n],
                        fit_start,
                        [np.max(confirmed.by_country[n]), 0.2, len(confirmed.by_country[n]) / 2],
                        sig_fit_function,
                        sig_fit_jacobian,
                    ),
                }
            }
        )
        temp_overview_dataset.update(
            {
                n.replace(" ", "_"): {
                    "confirmed": confirmed.by_country[n].tolist(),
                    "dead": dead.by_country[n].tolist(),
                    "recovered": recovered.by_country[n].tolist(),
                    "tests": tests_data[n]
                    if tests_data.__contains__(n)
                    else "undefined",
                    "serious": {
                        "value": serious_data[n]
                        if serious_data.__contains__(n)
                        else "undefined",
                        "updated": last_serious_data_refresh,
                    },
                }
            }
        )

    temp_detail_datasets.update(
        {
            "global": {
                "exp": generate_fits(
                    fit_data_x,
                    confirmed.total,
                    fit_start,
                    [confirmed.total[0], 0.1],
                    exp_fit_function,
                    exp_fit_jacobian,
                ),
                "sig": generate_fits(
                    fit_data_x,
                    confirmed.total,
                    fit_start,
                    [np.max(confirmed.total), 0.2, len(confirmed.total) / 2],
                    sig_fit_function,
                    sig_fit_jacobian,
                ),
            },
        }
    )
    temp_overview_dataset.update(
        {
            "global": {
                "confirmed": confirmed.total.tolist(),
                "dead": dead.total.tolist(),
                "recovered": recovered.total.tolist(),
                "tests": tests_data["global"]
                if tests_data.__contains__("global")
                else "undefined",
                "serious": {
                    "value": serious_data["global"]
                    if serious_data.__contains__("global")
                    else "undefined",
                    "updated": last_serious_data_refresh,
                },
            }
        }
    )

    temp_details_json = {}
    for k in temp_detail_datasets.keys():
        temp_details_json.update({k: json.dumps(temp_detail_datasets[k]).encode()})

    return (json.dumps(temp_overview_dataset).encode(), temp_details_json)


overview_json, details_json = prepare_data()


def get_detail_dataset(country):
    return details_json[country]


def get_overview_dataset():
    return overview_json


def update_data():
    global overview_json
    global details_json

    scheduler.enter(60 * 60 * 4, 1, update_data)

    print("Updating Corona Data")
    repo = git.cmd.Git("./data")
    repo.fetch("--all")
    repo.reset("--hard", "origin/master")
    repo.pull("origin", "master")
    repo.checkout("master")
    print("Git Pull completed")

    overview_json, details_json = prepare_data()

scheduler = sched.scheduler(time.time, time.sleep)

update_data()
t = threading.Thread(target=scheduler.run)
t.start()
