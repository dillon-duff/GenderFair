import random
import pdb
from firebase_functions import https_fn
from firebase_admin import initialize_app
import pandas as pd
import json
import requests
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET


initialize_app()

propublica_base_url = "https://projects.propublica.org/nonprofits/organizations/"



def efile_string(st):
    """Converts an XML tag name to those that match the
    XML tags that can be seen online. Just adds the irs
    url to the front
    """
    return "{http://www.irs.gov/efile}" + st


def get_names_from_dataFrame(dataFrame):
    names = dataFrame["PersonNm"]
    names.name = "name"
    return names


def get_total_compensation_from_data_frame(dataFrame):
    totalComp = dataFrame["TotalCompensationFilingOrgAmt"]

    def select_value(row):
        return (
            row["TotalCompensationRltdOrgsAmt"]
            if row["TotalCompensationFilingOrgAmt"] == 0
            else row["TotalCompensationFilingOrgAmt"]
        )

    totalComp = dataFrame.apply(select_value, axis=1)
    totalComp.name = "compensation"
    return totalComp


def format_gender_data_frame(dataFrame):
    names = get_names_from_dataFrame(dataFrame)
    totalComp = get_total_compensation_from_data_frame(dataFrame)
    genders = []
    for name in names:
        if isinstance(name, str):
            results = guess_gender(name.split()[0])
        else:
            results = guess_gender("~~~~~~~~~~~~~~~~~")
        gender = results["gender"]
        genders.append(gender)

    genders = pd.Series(genders, name="gender")
    totalComp = pd.Series(totalComp, name="compensation")

    df = pd.concat([genders, totalComp], axis=1)
    return df


def generate_pay_gap_metric(df):

    if "PersonNm" not in df or "TotalCompensationFilingOrgAmt" not in df:
        print("Error: PersonNm not listed")
        return -1

    calibrated_df = format_gender_data_frame(df)

    sum_comp = calibrated_df.groupby("gender")["compensation"].sum()

    if "M" in sum_comp:
        male_total_comp = sum_comp["M"]
        male_count = len(calibrated_df[calibrated_df["gender"] == "M"])
    else:
        male_total_comp = 0
        male_count = 0

    if "F" in sum_comp:
        female_total_comp = sum_comp["F"]
        female_count = len(calibrated_df[calibrated_df["gender"] == "F"])
    else:
        female_total_comp = 0
        female_count = 0

    average_male_salary = 0 if male_count == 0 else male_total_comp / male_count
    average_female_salary = 0 if female_count == 0 else female_total_comp / female_count

    pay_gap = (
        -1
        if average_male_salary == 0
        else ((average_male_salary - average_female_salary) / average_male_salary) * 100
    )
    percent_male = (
        0
        if (male_count + female_count) == 0
        else male_count / (male_count + female_count)
    )
    percent_female = (
        0
        if (male_count + female_count) == 0
        else female_count / (male_count + female_count)
    )

    result = {
        "average_female_salary": average_female_salary,
        "average_male_salary": average_male_salary,
        "pay_gap": pay_gap,
        "percent_male": percent_male*100,
        "percent_female": percent_female*100,
    }
    return result


gender_df = pd.read_csv("first_name_gender_probabilities.csv")
gender_df["Name"] = gender_df["Name"].str.lower()


def guess_gender(name):
    name = name.lower()
    if name not in gender_df["Name"].values:
        return {"gender": random.choice(["M", "F"])}
    return {
        "gender": "F"
        if random.random()
        <= gender_df[gender_df["Name"] == name]["female_prob"].values[0]
        else "M"
    }


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


def get_990_info_from_xml(xml_string):
    try:
        # Parse the XML string
        tree = ET.ElementTree(ET.fromstring(xml_string))

        root = tree.getroot()

        business_name = (
            root[0].find(efile_string("Filer")).find(
                efile_string("BusinessName"))
        )
        org_name = ""
        for c in business_name:
            org_name += c.text

        # The root currently has ReturnHeader and ReturnData as children.
        # We are only concerned with the ReturnData so we can
        # redefine the root from being the parents of both of these
        # to being ReturnData
        root = root[1]

        # Find the root for the Schedule J Data (Compensation Information)
        root990 = root.find(efile_string("IRS990"))

        if root990 is None:
            print("Invalid XML file, no IRS990 root.")
            return -1

        # Find the root for the Schedule J Data (Compensation Information)
        schedule_j_root = root.find(efile_string("IRS990ScheduleJ"))

        if schedule_j_root is None:
            print("Invalid XML file, no Schedule J root.")
            return -1

        key_employee_group = schedule_j_root.findall(
            efile_string("RltdOrgOfficerTrstKeyEmplGrp")
        )

        # Save data for each employee in this dictionary
        employee_dicts = []

        for employee in key_employee_group:
            employee_dict = {}
            for child in employee:
                tag = child.tag.replace("{http://www.irs.gov/efile}", "")
                text = child.text
                employee_dict[tag] = text
            employee_dicts.append(employee_dict)

        if len(employee_dicts) == 0:
            print("Error: No employees lsited in highest compensated")
            return -1

        key_employee_group_categories = root990.findall(
            efile_string("Form990PartVIISectionAGrp")
        )

        # Save data for each employee in this dictionary
        employee_categories_dicts = []

        for employee in key_employee_group_categories:
            employee_dict = {}
            for child in employee:
                tag = child.tag.replace("{http://www.irs.gov/efile}", "")
                if (
                    tag.__eq__("IndividualTrusteeOrDirectorInd")
                    | tag.__eq__("OfficerInd")
                    | tag.__eq__("HighestCompensatedEmployeeInd")
                    | tag.__eq__("KeyEmployeeInd")
                    | tag.__eq__("FormerOfcrDirectorTrusteeInd")
                ):
                    text = tag
                    tag = "Category"
                else:
                    text = child.text
                employee_dict[tag] = text
            employee_categories_dicts.append(employee_dict)

        names_category_pairs = pd.DataFrame(
            [
                (d["PersonNm"].lower().split()[0], d["Category"])
                for d in employee_categories_dicts
            ]
        )
        names_category_pairs[0] = names_category_pairs[0].apply(
            lambda x: guess_gender(x)["gender"]
        )
        grouped = names_category_pairs.groupby(
            [1, 0]).size().unstack(fill_value=0)

        grouped_percentage = grouped.div(grouped.sum(axis=1), axis=0) * 100

        category_gender_percentage_dict = grouped_percentage.to_dict(
            orient='index')

        total_compensation = root990.find(
            efile_string("CYSalariesCompEmpBnftPaidAmt")
        ).text

        web_address = (
            "N/A"
            if root990.find(efile_string("WebsiteAddressTxt")) is None
            else root990.find(efile_string("WebsiteAddressTxt")).text
        )
        total_employees = (
            -1
            if root990.find(efile_string("EmployeeCnt")) is None
            else int(root990.find(efile_string("EmployeeCnt")).text)
        )
        total_compensation = (
            -1
            if root990.find(efile_string("CYSalariesCompEmpBnftPaidAmt")) is None
            else float(root990.find(efile_string("CYSalariesCompEmpBnftPaidAmt")).text)
        )

        revenue_root = root.find(efile_string("IRS990"))
        revenue = (
            -1
            if revenue_root is None
            else float(revenue_root.find(efile_string("CYTotalRevenueAmt")).text)
        )

        df = pd.DataFrame(employee_dicts)

        if "TotalCompensationFilingOrgAmt" in df:
            df["TotalCompensationFilingOrgAmt"] = df[
                "TotalCompensationFilingOrgAmt"
            ].astype("float64")
        if "TotalCompensationRltdOrgsAmt" in df:
            df["TotalCompensationRltdOrgsAmt"] = df[
                "TotalCompensationRltdOrgsAmt"
            ].astype("float64")

        highest_paid_cumulative_comp = df["TotalCompensationFilingOrgAmt"].sum(
        )
        num_highest_comp_employees = df.shape[0]

        info = generate_pay_gap_metric(df)
        if info == -1:
            return -1
        info["avg_employee_comp"] = (
            None
            if not (
                total_compensation
                and highest_paid_cumulative_comp
                and total_employees
                and num_highest_comp_employees
                and (total_employees - num_highest_comp_employees != 0)
            )
            else (total_compensation - highest_paid_cumulative_comp)
            / (total_employees - num_highest_comp_employees)
        )
        info["highest_salary"] = df["TotalCompensationFilingOrgAmt"].max()
        info["total_compensation"] = total_compensation
        info["web_address"] = web_address
        info["num_employees"] = total_employees
        info["total_revenue"] = revenue
        info["org_name"] = org_name

        for category, gender_distribution in category_gender_percentage_dict.items():
            info[f"{category}_percent_female"] = gender_distribution['F']

        return info

    except ET.ParseError as e:
        print(f"Error parsing XML: {e}")
        return -1
    except Exception as e:
        print(f"An error occurred: {e}")
        return -1


@https_fn.on_request()
def get_org_990_xml(req: https_fn.Request) -> https_fn.Response:
    org_name = req.args.get("org_name")
    ein = req.args.get("ein")
    if not org_name and not ein:
        return https_fn.Response("One of org_name and ein parameters are required", status=400)

    xml_url = get_xml_url_from_ein(ein)
    if xml_url == -1:
        return https_fn.Response(f"Could not find valid 990 XML for EIN: {ein}", status=400)

    xml_string = requests.get(xml_url).content

    info = get_990_info_from_xml(xml_string)

    if info == -1:
        return https_fn.Response(f"Invalid 990 XML for EIN: {ein}", status=400)

    return https_fn.Response(json.dumps(info), content_type="application/json")
