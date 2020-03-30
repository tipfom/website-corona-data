country_map = {
    "United States": "US",
    "Czech Republic": "Czechia",
    "TOTAL": "global"
}

def try_get_bno_seriouscases():
    import urllib.request
    from urllib.request import Request, urlopen

    try:
        url = "https://bnonews.com/index.php/2020/03/the-latest-coronavirus-cases/"
        mybytes = urlopen(Request(url, headers={'User-Agent': 'Mozilla/5.0'})).read()
        htmlcontent = mybytes.decode("utf8")
        data_url = htmlcontent.split("</iframe>")[0].split("<iframe")[1].split("src=")[1].split("\"")[1]

        mybytes = urlopen(Request(data_url)).read()
        htmlcontent = mybytes.decode("utf8")

        table = htmlcontent.split("<tbody>")[1].split("</tbody>")[0]
        rows = table.split("<tr style='height:39px;'>")
        serious = {}
        for row in rows:
            columns = row.split("</td>")
            try:
                country = columns[0].split("th>")[1].split(">")[1]
                if country_map.__contains__(country):
                    country = country_map[country]
                cases = columns[6].split(">")[1]
                serious.update({country: cases})
            except:
                pass
        return serious
    except:
        return None
