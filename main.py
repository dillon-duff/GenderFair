from difflib import SequenceMatcher
import requests
from scrape import get_xml_url_from_ein
from xml_parsing import save_top_earners_from_xml


propublica_api_url = "https://projects.propublica.org/nonprofits/api/v2/search.json"


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


def string_similarity(a, b):
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


if __name__ == "__main__":
    s = " "
    while len(s) > 0:
        s = str(input("\nEnter company name to get top earners from: "))
        if len(s) <= 0:
            break
        #save_top_earners_from_company_name(s)
        #save_top_earners_categories_from_company_name(s)
        #save_website_from_company_name(s)
        #save_num_employees_from_company_name(s)

