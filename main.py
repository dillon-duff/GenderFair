from difflib import SequenceMatcher
import requests
import pandas as pd
from io import BytesIO
from xml_parsing import get_990_info_for_company


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


def get_candid_top_df():
    """Returns all organizations with > 50 employees from Candid's Demographics
    """
    candid_demographics_url = "https://info.candid.org/candid-demographics"
    resp = requests.get(candid_demographics_url)
    b = BytesIO(resp.content)
    df = pd.read_excel(BytesIO(resp.content), sheet_name="Organizations")
    df = df[df['total_staff'] >= 50]

    return df


def get_propublica_top_df():
    pass


if __name__ == "__main__":
    candid_top_df = get_candid_top_df()

    def add_info_for_org(row):
        info = get_990_info_for_company(row['ein'])
        if info == -1:
            return None
        for k, v in info.items():
            row[k] = v
        return row

    candid_top_df = candid_top_df.apply(add_info_for_org, axis=1)

    # Get min revenue
    # Use min revenue to get all ProPublica with revenue >= this
    # Merge by EIN
