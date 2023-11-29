from multiprocessing import Pool
import copy
import matplotlib.pyplot as plt
import time
from difflib import SequenceMatcher
import requests
import pandas as pd
from io import BytesIO
from xml_parsing import get_990_info_for_company
from multiprocessing import Pool, cpu_count
from io import StringIO
from concurrent.futures import ThreadPoolExecutor
from percentage import calculate_percentages


propublica_api_url = "https://projects.propublica.org/nonprofits/api/v2/search.json"


def get_best_matching_eins_from_company_name(company_name):
    """Returns sorted list of dictionary items of companies that best match the given name.

    Args:
        string (company_name): company's name string

    Returns:
        list of (ein, name) for all results in order by best matching name to company_name (ein is a company's UID)
    """
    PARAMS = {"q": company_name}

    r = requests.get(url=propublica_api_url, params=PARAMS)

    data = r.json()

    similarities = {}

    for i, org in enumerate(data["organizations"]):
        org_name = org["name"]
        similarity = string_similarity(company_name, org_name)
        similarities[i] = similarity

    sorted_similarities = sorted(
        similarities.items(), key=lambda x: x[1], reverse=True)

    return list(
        map(
            lambda x: (
                data["organizations"][x[0]]["ein"],
                data["organizations"][x[0]]["name"],
            ),
            sorted_similarities,
        )
    )


def string_similarity(a, b):
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


def get_candid_top_df():
    """Returns all organizations with > 50 employees from Candid's Demographics"""
    candid_demographics_url = "https://info.candid.org/candid-demographics"
    resp = requests.get(candid_demographics_url)
    b = BytesIO(resp.content)
    df = pd.read_excel(BytesIO(resp.content), sheet_name="Organizations")
    df = df[df["total_staff"] >= 50]

    df = df.reset_index().drop("index", axis=1)
    df = df.apply(lambda col: pd.to_numeric(col, errors="ignore"))

    return df


def fetch_org_info(ein):
    propublica_org_api_url = (
        "https://projects.propublica.org/nonprofits/api/v2//organizations/"
    )
    propub_info = requests.get(
        url=propublica_org_api_url + f"{ein}.json").json()
    return propub_info


def get_top_df_990(min_revenue):
    base_url = "https://www.irs.gov/pub/irs-soi/"
    file_names = ["eo1.csv", "eo2.csv", "eo3.csv", "eo4.csv"]
    dataframes = {}

    for file_name in file_names:
        response = requests.get(base_url + file_name)
        response.raise_for_status()

        data = StringIO(response.text)
        df = pd.read_csv(data)

        dataframes[file_name] = df

    combined_df = pd.concat(dataframes.values(), ignore_index=True)
    combined_df = combined_df.dropna(subset=["INCOME_AMT"])

    combined_df = combined_df[combined_df["INCOME_AMT"] >= min_revenue]
    return combined_df


def add_info_for_org(row):
    try:

        row = row.copy()
        info = get_990_info_for_company(row["ein"])
        if info == -1 or info is None:
            return None
        for k, v in info.items():
            if k not in row:
                row[k] = v
        return row
    except Exception as e:
        return None


if __name__ == "__main__":
    absolute_start = time.time()

    # Get Candid >= 50 employees
    candid_top_df = get_candid_top_df()

    # Multi-processing
    num_procs = 10

    with Pool(num_procs) as pool:
        data = pool.map(add_info_for_org, [
                        row for _, row in candid_top_df.iterrows()])

    candid_top_df = pd.DataFrame([r for r in data if r is not None])

    # Get min revenue
    min_revenue = candid_top_df["total_revenue"].min()
    # print(f"Min revenue: {min_revenue}")

    # Use min revenue to get all 990s with revenue >= this
    top_df_990 = (
        get_top_df_990(min_revenue=min_revenue)
        .rename(columns={"EIN": "ein"})
        .loc[:, ["ein"]]
    )

    with Pool(num_procs) as pool:
        data = pool.map(
            add_info_for_org, [row for _, row in top_df_990.iterrows()]
        )

    absolute_end = time.time()

    print(f"ALL DONE!!!! (took {absolute_end-absolute_start} seconds)")

    top_df_990 = pd.DataFrame([r for r in data if r is not None])

    top_df_990 = top_df_990.reset_index(drop=True)
    candid_top_df = candid_top_df.reset_index(drop=True)

    top_df_990.to_csv("990-Top-11-29.csv", index=False)
    candid_top_df = candid_top_df.drop(columns=["Unnamed: 0", "dei_last_updated", "race_leader", "gender1_leader", "gender2_leader", "orientation_leader",
                                                "disability_status_leader", "race_coleader", "gender1_coleader", "gender2_coleader", "orientation_coleader",
                                                "disability_status_coleader",
                                                "gender2_decline_to_state_board", "gender2_unknown_board", "lgbtqia_board", "straight_board",
                                                "orientation_decline_to_state_board", "orientation_unknown_board", "with_disability_board",
                                                "without_disability_board", "disability_decline_to_state_board", "disability_unknown_board",

                                                "gender2_decline_to_state_senior_staff", "gender2_unknown_senior_staff", "lgbtqia_senior_staff", "straight_senior_staff",
                                                "orientation_decline_to_state_senior_staff", "orientation_unknown_senior_staff", "with_disability_senior_staff",
                                                "without_disability_senior_staff", "disability_decline_to_state_senior_staff", "disability_unknown_senior_staff",


                                                "gender2_decline_to_state_staff", "gender2_unknown_staff", "lgbtqia_staff", "straight_staff",
                                                "orientation_decline_to_state_staff", "orientation_unknown_staff", "with_disability_staff",
                                                "without_disability_staff", "disability_decline_to_state_staff", "disability_unknown_staff"])
    candid_top_df.to_csv("Candid-Top-11-29.csv", index=False)
    calculate_percentages("Candid-Top-11-29.csv",
                          "Candid-Top-11-29-with-Percentages.csv")

    # Merge by EIN
    # candid_top_df['ein'] = candid_top_df['ein'].map(lambda x : x.replace("-", "")).astype("int")
    # candid_with_propublica = top_df_990.merge(candid_top_df, left_on='EIN', right_on='ein', how='inner')

    # candid_top_df.to_csv("Candid-Top.csv")
    # top_df_990.to_csv("ProPublica-Top.csv")
    # candid_with_propublica.to_csv("Candid-Top-With-ProPublica-Info.csv")
