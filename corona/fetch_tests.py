country_map = {
    "World": "global",
    "USA": "US",
    "S. Korea": "Korea, South",
    "UK": "United Kingdom",
    "TOTAL": "global",
    "Myanmar": "Burma",
}


def try_get_tests():
    url = "https://www.worldometers.info/coronavirus/"

    from urllib.request import Request, urlopen
    from datetime import datetime, timedelta
    import json

    htmlcontent = (
        urlopen(Request(url, headers={"User-Agent": "Mozilla/5.0"}))
        .read()
        .decode("utf8")
    )
    table = htmlcontent.split('<table id="main_table_countries_today"')[1].split(
        "</table>"
    )[0]
    tablebody = table.split("<tbody>")[1].split("</tbody>")[0]
    test_data = {}
    for row in tablebody.split("</tr>"):
        columns = row.split("</td>")
        if len(columns) > 11:
            try:
                name = columns[0].split("<a ")[1].split(">")[1].replace("</a", "")
                country = name
                if country_map.__contains__(country):
                    country = country_map[country]
                country = country.replace(" ", "_")
                cases = columns[1].split(">")[1]
                tests = columns[10].split(">")[1]
                if tests != "":
                    test_data.update(
                        {
                            country: {
                                "total": tests.replace(",", ""),
                                "original_name": name,
                                "confirmed_cases": cases.replace(",", ""),
                                "updated": datetime.now().isoformat(),
                            }
                        }
                    )
            except Exception:
                pass

    return json.dumps(test_data).encode()


if __name__ == "__main__":
    ret = try_get_tests()
    print(ret)
    pass
