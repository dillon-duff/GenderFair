import requests
from bs4 import BeautifulSoup
from xml_parsing import *
from difflib import SequenceMatcher

propublica_api_url = "https://projects.propublica.org/nonprofits/api/v2/search.json"

propublica_base_url = "https://projects.propublica.org/nonprofits/organizations/"


def string_similarity(a, b):
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


def get_best_matching_eins_from_company_name(company_name):
    """Returns sorted list of dictionary items of companies that best match the given name.

    Args:
        string (company_name): company's name string
    
    Returns:
        list of (ein, name) for all results in order by best matching name to company_name (ein is a company's UID)
    """
    PARAMS = {'q': company_name}

    r = requests.get(url=propublica_api_url, params=PARAMS)

    data = r.json()

    similarities = {}

    for i, org in enumerate(data["organizations"]):
        org_name = org["name"]
        similarity = string_similarity(company_name, org_name)
        similarities[i] = similarity

    sorted_similarities = sorted(
        similarities.items(), key=lambda x: x[1], reverse=True)

    return list(map(lambda x: (data["organizations"][x[0]]["ein"], data["organizations"][x[0]]["name"]), sorted_similarities))


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
        print("XML 990 found")
        urls = ["https://projects.propublica.org" +
                e.get("href") for e in xml_buttons]
    else:
        print(
            f"XML 990 couldn't be found on this specific ProPublica page for this company with ein: {ein}")
        return -1

    return urls[0]


def save_top_earners_from_company_name(company_name):
    ordered_eins = get_best_matching_eins_from_company_name(company_name)
    if len(ordered_eins) == 0:
        print(
            f"Failed to find any company with name similar to: {company_name}")

    url_for_xml = None
    for e, name in ordered_eins:
        next_xml_url = get_xml_url_from_ein(e)
        if next_xml_url and next_xml_url != -1:
            url_for_xml = next_xml_url
            saved = save_top_earners_from_xml(url_for_xml, name)
            if saved != -1:
                break

    if url_for_xml is None:
        return -1


if __name__ == "__main__":
    s = " "
    while len(s) > 0:
        s = str(input("\nEnter company name to get top earners from: "))
        if len(s) <= 0 : break
        save_top_earners_from_company_name(s)
