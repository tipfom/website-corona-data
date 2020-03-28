MAINLAND_CHINA = 0
WESTERN_PACIFIC_REGION = 1
EUROPEAN_REGION = 2
SOUTH_EAST_ASIA_REGION = 3
EASTERN_MEDITERRANEAN_REGION = 4
REGION_OF_THE_AMERICANS = 5
AFRICAN_REGION = 6
OTHER = 7

region_map = {
    "China": MAINLAND_CHINA,
    "Taiwan*": MAINLAND_CHINA,
    #####################################################################
    "Korea, South": WESTERN_PACIFIC_REGION,
    "Japan": WESTERN_PACIFIC_REGION,
    "Singapore": WESTERN_PACIFIC_REGION,
    "Australia": WESTERN_PACIFIC_REGION,
    "Malaysia": WESTERN_PACIFIC_REGION,
    "Vietnam": WESTERN_PACIFIC_REGION,
    "Philippines": WESTERN_PACIFIC_REGION,
    "Cambodia": WESTERN_PACIFIC_REGION,
    "New Zealand": WESTERN_PACIFIC_REGION,
    "Fiji": WESTERN_PACIFIC_REGION,
    "Papua New Guinea": WESTERN_PACIFIC_REGION,
    #####################################################################
    "Italy": EUROPEAN_REGION,
    "France": EUROPEAN_REGION,
    "Germany": EUROPEAN_REGION,
    "Spain": EUROPEAN_REGION,
    "United Kingdom": EUROPEAN_REGION,
    "Switzerland": EUROPEAN_REGION,
    "Norway": EUROPEAN_REGION,
    "Sweden": EUROPEAN_REGION,
    "Austria": EUROPEAN_REGION,
    "Croatia": EUROPEAN_REGION,
    "Netherlands": EUROPEAN_REGION,
    "Azerbaijan": EUROPEAN_REGION,
    "Denmark": EUROPEAN_REGION,
    "Georgia": EUROPEAN_REGION,
    "Greece": EUROPEAN_REGION,
    "Romania": EUROPEAN_REGION,
    "Finland": EUROPEAN_REGION,
    "Russia": EUROPEAN_REGION,
    "Belarus": EUROPEAN_REGION,
    "Belgium": EUROPEAN_REGION,
    "Estonia": EUROPEAN_REGION,
    "Ireland": EUROPEAN_REGION,
    "Lithuania": EUROPEAN_REGION,
    "Monaco": EUROPEAN_REGION,
    "North Macedonia": EUROPEAN_REGION,
    "San Marino": EUROPEAN_REGION,
    "Luxembourg": EUROPEAN_REGION,
    "Iceland": EUROPEAN_REGION,
    "Czechia": EUROPEAN_REGION,
    "Andorra": EUROPEAN_REGION,
    "Portugal": EUROPEAN_REGION,
    "Latvia": EUROPEAN_REGION,
    "Ukraine": EUROPEAN_REGION,
    "Hungary": EUROPEAN_REGION,
    "Liechtenstein": EUROPEAN_REGION,
    "Poland": EUROPEAN_REGION,
    "Bosnia and Herzegovina": EUROPEAN_REGION,
    "Slovenia": EUROPEAN_REGION,
    "Serbia": EUROPEAN_REGION,
    "Slovakia": EUROPEAN_REGION,
    "Malta": EUROPEAN_REGION,
    "Bulgaria": EUROPEAN_REGION,
    "Moldova": EUROPEAN_REGION,
    "Albania": EUROPEAN_REGION,
    "Cyprus": EUROPEAN_REGION,
    "Turkey": EUROPEAN_REGION,  # ?????????????????????
    "Holy See": EUROPEAN_REGION,
    "Kosovo": EUROPEAN_REGION,
    "Montenegro": EUROPEAN_REGION,
    #####################################################################
    "Thailand": SOUTH_EAST_ASIA_REGION,
    "Indonesia": SOUTH_EAST_ASIA_REGION,
    "India": SOUTH_EAST_ASIA_REGION,
    "Nepal": SOUTH_EAST_ASIA_REGION,
    "Sri Lanka": SOUTH_EAST_ASIA_REGION,
    "Bhutan": SOUTH_EAST_ASIA_REGION,
    "Maldives": SOUTH_EAST_ASIA_REGION,
    "Bangladesh": SOUTH_EAST_ASIA_REGION,
    "Brunei": SOUTH_EAST_ASIA_REGION,
    "Mongolia": SOUTH_EAST_ASIA_REGION,  # ??????????
    "Uzbekistan": SOUTH_EAST_ASIA_REGION,  # ?????????
    "Kazakhstan": SOUTH_EAST_ASIA_REGION,  # ????????????
    "Kyrgyzstan": SOUTH_EAST_ASIA_REGION,  # ??????????????
    "Timor-Leste": SOUTH_EAST_ASIA_REGION,
    "Laos": SOUTH_EAST_ASIA_REGION,
    #####################################################################
    "Armenia": EASTERN_MEDITERRANEAN_REGION,  # ????????????
    "Iran": EASTERN_MEDITERRANEAN_REGION,
    "Kuwait": EASTERN_MEDITERRANEAN_REGION,
    "Bahrain": EASTERN_MEDITERRANEAN_REGION,
    "United Arab Emirates": EASTERN_MEDITERRANEAN_REGION,
    "Iraq": EASTERN_MEDITERRANEAN_REGION,
    "Oman": EASTERN_MEDITERRANEAN_REGION,
    "Pakistan": EASTERN_MEDITERRANEAN_REGION,
    "Lebanon": EASTERN_MEDITERRANEAN_REGION,
    "Afghanistan": EASTERN_MEDITERRANEAN_REGION,
    "Egypt": EASTERN_MEDITERRANEAN_REGION,
    "Qatar": EASTERN_MEDITERRANEAN_REGION,
    "Saudi Arabia": EASTERN_MEDITERRANEAN_REGION,
    "Jordan": EASTERN_MEDITERRANEAN_REGION,  # ??????????????
    "Israel": EASTERN_MEDITERRANEAN_REGION,
    "Syria": EASTERN_MEDITERRANEAN_REGION,
    #####################################################################
    "US": REGION_OF_THE_AMERICANS,
    "Canada": REGION_OF_THE_AMERICANS,
    "Brazil": REGION_OF_THE_AMERICANS,
    "Mexico": REGION_OF_THE_AMERICANS,
    "Ecuador": REGION_OF_THE_AMERICANS,
    "Dominican Republic": REGION_OF_THE_AMERICANS,  # ????????????
    "Chile": REGION_OF_THE_AMERICANS,  # ?????????????????
    "Argentina": REGION_OF_THE_AMERICANS,  # ????????????
    "Peru": REGION_OF_THE_AMERICANS,
    "Colombia": REGION_OF_THE_AMERICANS,
    "Costa Rica": REGION_OF_THE_AMERICANS,
    "Paraguay": REGION_OF_THE_AMERICANS,
    "Honduras": REGION_OF_THE_AMERICANS,
    "Jamaica": REGION_OF_THE_AMERICANS,
    "Cuba": REGION_OF_THE_AMERICANS,
    "Guyana": REGION_OF_THE_AMERICANS,
    "Panama": REGION_OF_THE_AMERICANS,
    "Bolivia": REGION_OF_THE_AMERICANS,
    "Venezuela": REGION_OF_THE_AMERICANS,
    "Guatemala": REGION_OF_THE_AMERICANS,
    "Saint Lucia": REGION_OF_THE_AMERICANS,
    "Saint Vincent and the Grenadines": REGION_OF_THE_AMERICANS,
    "Antigua and Barbuda": REGION_OF_THE_AMERICANS,
    "Uruguay": REGION_OF_THE_AMERICANS,
    "Trinidad and Tobago": REGION_OF_THE_AMERICANS,
    "Suriname": REGION_OF_THE_AMERICANS,
    "Bahamas": REGION_OF_THE_AMERICANS,
    "Barbados": REGION_OF_THE_AMERICANS,
    "Nicaragua": REGION_OF_THE_AMERICANS,
    "El Salvador": REGION_OF_THE_AMERICANS,
    "Haiti": REGION_OF_THE_AMERICANS,
    "Dominica": REGION_OF_THE_AMERICANS,
    "Grenada": REGION_OF_THE_AMERICANS,
    "Belize": REGION_OF_THE_AMERICANS,
    #####################################################################
    "Algeria": AFRICAN_REGION,
    "Nigeria": AFRICAN_REGION,
    "Morocco": AFRICAN_REGION,
    "Senegal": AFRICAN_REGION,
    "Tunisia": AFRICAN_REGION,
    "South Africa": AFRICAN_REGION,
    "Togo": AFRICAN_REGION,
    "Cameroon": AFRICAN_REGION,
    "Congo (Kinshasa)": AFRICAN_REGION,
    "Cote d'Ivoire": AFRICAN_REGION,
    "Burkina Faso": AFRICAN_REGION,
    "Ghana": AFRICAN_REGION,
    "Namibia": AFRICAN_REGION,
    "Seychelles": AFRICAN_REGION,
    "Eswatini": AFRICAN_REGION,
    "Gabon": AFRICAN_REGION,
    "Mauritania": AFRICAN_REGION,
    "Rwanda": AFRICAN_REGION,
    "Sudan": AFRICAN_REGION,
    "Kenya": AFRICAN_REGION,
    "Guinea": AFRICAN_REGION,
    "Congo (Brazzaville)": AFRICAN_REGION,
    "Equatorial Guinea": AFRICAN_REGION,
    "Central African Republic": AFRICAN_REGION,
    "Ethiopia": AFRICAN_REGION,
    "Benin": AFRICAN_REGION,
    "Liberia": AFRICAN_REGION,
    "Somalia": AFRICAN_REGION,
    "Tanzania": AFRICAN_REGION,
    "Mauritius": AFRICAN_REGION,  # ???????????
    "Zambia": AFRICAN_REGION,
    "Djibouti": AFRICAN_REGION,  # ??????????
    "Chad": AFRICAN_REGION,
    "Zimbabwe": AFRICAN_REGION,
    "Niger": AFRICAN_REGION,
    "Madagascar": AFRICAN_REGION,
    "Cabo Verde": AFRICAN_REGION,
    "Angola": AFRICAN_REGION,
    "Eritrea": AFRICAN_REGION,
    "Uganda": AFRICAN_REGION,
    "Mozambique": AFRICAN_REGION,
    "Gambia": AFRICAN_REGION,
    "Libya": AFRICAN_REGION,
    #####################################################################
    "Diamond Princess": OTHER,
}

region_names = {
    MAINLAND_CHINA: "china",
    WESTERN_PACIFIC_REGION: "western_pacific_region",
    EUROPEAN_REGION: "european_region",
    SOUTH_EAST_ASIA_REGION: "south_east_asia_region",
    EASTERN_MEDITERRANEAN_REGION: "eastern_mediterranean_region",
    REGION_OF_THE_AMERICANS: "region_of_the_americans",
    AFRICAN_REGION: "african_region",
    OTHER: "other",
}

REGION_COUNT = OTHER + 1

if __name__ == "__main__":
    import csv
    regions_in_file = []
    with open("./corona/data/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv") as datafile:
        datafile_reader = csv.reader(datafile, delimiter=",", quotechar='"')
        for row in datafile_reader:
            if not regions_in_file.__contains__(row[1]):
                regions_in_file.append(row[1])

    regions_in_regionmap = [key for key in region_map.keys()]
    for region in regions_in_file:
        if not regions_in_regionmap.__contains__(region):
            print("missing " + region)
        else:
            regions_in_regionmap.remove(region)
    
    print(regions_in_regionmap)
