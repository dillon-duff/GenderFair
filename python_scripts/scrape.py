import requests
from bs4 import BeautifulSoup


propublica_base_url = "https://projects.propublica.org/nonprofits/organizations/"


def get_xml_url_from_ein(ein):
    """Returns most recent URL for 990 XML form

    Args:
        string (ein): company's UID

    Returns:
        string: most recent URL for 990 XML form
    """
    propublica_url = propublica_base_url + str(ein)
    page = requests.get(propublica_url)
    soup = BeautifulSoup(page.content, "html.parser")

    xml_buttons = soup.find_all(lambda x: x.name == "a" and x.text == "XML")

    if xml_buttons:
        urls = ["https://projects.propublica.org" +
                e.get("href") for e in xml_buttons]
    else:
        return -1

    return urls[0]


def get_top_n_eins_by_revenue(n):
    NUM_COMPANIES = n

    propublica_api_url = "https://projects.propublica.org/nonprofits/api/v2/search.json"
    PARAMS = {'q': "", "total_results": NUM_COMPANIES,
              "per_page": NUM_COMPANIES}

    eins = []
    page = 0

    consecutive_misses = 0

    while len(eins) < NUM_COMPANIES:
        PARAMS = {'q': "", "total_results": NUM_COMPANIES,
                  "per_page": NUM_COMPANIES, "page": page}

        r = requests.get(url=propublica_api_url, params=PARAMS)

        data = r.json()

        if 'error' in data:
            if data["error"] == "Pagination out of range":
                return eins
            page += 1
            consecutive_misses += 1
            if consecutive_misses > 5:
                return eins
            continue

        if "organizations" in data:
            for org in data["organizations"]:
                ein = org["ein"]
                eins.append(ein)
            page += 1
        consecutive_misses = 0

    return eins


if __name__ == "__main__":
    print(get_top_n_eins_by_revenue(25))
