country_map = {
    "United States": "US",
    "Czech Republic": "Czechia",
    "South Korea": "Korea, South",
    "TOTAL": "global",
}

def try_get_tests():
    url = "https://ourworldindata.org/grapher/tests-vs-confirmed-cases-covid-19"

    from urllib.request import Request, urlopen
    htmlcontent = urlopen(Request(url, headers={'User-Agent': 'Mozilla/5.0'})).read().decode("utf8")
    dataurl = "https://ourworldindata.org/" + htmlcontent.split("<link rel=\"preload\" href=\"")[1].split("\"")[0]
    jsoncontent =  urlopen(Request(dataurl, headers={'User-Agent': 'Mozilla/5.0'})).read().decode("utf8")

    import json
    json_parsed = json.loads(jsoncontent)
    country_keys = json_parsed["entityKey"]

    print("reading " + json_parsed["variables"]["142596"]["name"])
    tests_countries = json_parsed["variables"]["142596"]["entities"]
    tests_dates = json_parsed["variables"]["142596"]["years"]
    tests_values = json_parsed["variables"]["142596"]["values"]

    print("reading " + json_parsed["variables"]["142582"]["name"])
    confirmed_countries = json_parsed["variables"]["142582"]["entities"]
    confirmed_dates = json_parsed["variables"]["142582"]["years"]
    confirmed_values = json_parsed["variables"]["142582"]["values"]

    test_data = {}

    from datetime import datetime, timedelta
    for i in range(len(tests_values)):
        country = country_keys[str(tests_countries[i])]["name"].split(" - ")
        original_name = country[0]
        if country_map.__contains__(country[0]):
            country[0] = country_map[country[0]]
        country[0] = country[0].replace(" ", "_")
        
        confirmed_at_date = 0
        for k in range(len(confirmed_values)):
            if country_keys[str(confirmed_countries[k])]["name"].startswith(original_name) and confirmed_dates[k] == tests_dates[i]:
                confirmed_at_date = confirmed_values[k]
                break

        if len(country) == 2:
            if not test_data.__contains__(country[0]):
                test_data.update({country[0]: {"total": 0, "original_name": original_name, "confirmed_cases": confirmed_at_date, "regions": {}, "updated": (datetime(2020,1,21) + timedelta(int(tests_dates[i]))).isoformat()}})
            test_data[country[0]]["total"] += tests_values[i]
            test_data[country[0]]["regions"].update({country[1]: tests_values[i]})
        else:
            test_data.update({country[0]: {"total": tests_values[i], "original_name": original_name, "confirmed_cases": confirmed_at_date, "updated": (datetime(2020,1,21) + timedelta(int(tests_dates[i]))).isoformat()}})

    return json.dumps(test_data).encode()

if __name__ == "__main__":
    ret = try_get_tests()
    pass