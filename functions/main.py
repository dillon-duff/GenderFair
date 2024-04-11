import random
import pdb
from firebase_functions import https_fn
import firebase_admin
from firebase_admin import initialize_app, credentials, firestore
import pandas as pd
import json
import requests
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET
import numpy as np

initialize_app()

propublica_base_url = "https://projects.propublica.org/nonprofits/organizations/"



class ScoreCalculator:

    # def avgOffset(self,ratio):
    #     return abs(50 - ratio)
    def scale_score(self, score):
        return round(score / 60 * 100)

    def calculate_scores(self, company_data, percentiles):

        if not company_data or 'metrics' not in company_data:
            return None

        metrics = company_data['metrics']



        scores = {

            "trustees_score": self.scale_score(self.trustees(metrics['IndividualTrusteeOrDirectorInd_percent_female'],percentiles)),
            "highest_compensated_score":  self.scale_score(self.highest_comp(metrics['HighestCompensatedEmployeeInd_percent_female'],percentiles)),
            "officers_score":  self.scale_score(self.officers(metrics['OfficerInd_percent_female'],percentiles)),
            "pay_gap_score": self.scale_score(self.pay_gap(metrics['pay_gap'],percentiles)),
            "average_salary_score": self.scale_score(self.avg_salary(metrics['salary_revenue_ratio'],percentiles)),
            "CEO_pay_ratio_score": self.scale_score(self.pay_ratio(metrics['CEO_pay_ratio'],percentiles)),
            "Candid_Reporting_score": self.scale_score(self.has_populated_fields(company_data,percentiles)),
            "diversity_reporting_score": self.scale_score(self.white_staff(company_data,percentiles))


        }

        scores['final_score'] = self.aggregate_scores(scores)
        return scores

    def white_staff(self,json_data,percentiles):
        staff_race = json_data.get("staff_race", {})

        # Calculate the total number of staff
        total_staff = sum(float(value) for key, value in staff_race.items() if value not in ["", None])

        # Return 0 if there are no staff details
        if total_staff == 0:
            return 0

        # Get the number of white staff
        if staff_race.get("white",0) == '':
            return 0 #LOOK INTO THIS ASWELL
        white_staff = float(staff_race.get("white", 0))

        # Calculate the percentage of white staff
        percentage_white = (white_staff / total_staff) * 100

        if percentage_white <= 61: #average amount for nonprofits
            return 5
        else: return 0 #Maybe change it so do we sum POC instead of do it this way

    def has_populated_fields(self,json_data,percentiles):
        fields_to_check = [
            "staff_race", "staff_gender", "senior_staff_race", "senior_staff_gender", "board_race", "board_gender"
        ]

        for field in fields_to_check:
            if field in json_data:
                # If any subfield has a non-empty, non-zero value, return True immediately
                if any(value for value in json_data[field].values() if value not in ["", None]):
                    return 5

        # If no populated fields are found, return False
        return 0
    def trustees(self, ratio,percentiles):
        # Logic for score 1
        if ratio:  # placeholder

            ratio = float(ratio)


            # if ratio == self.avgOffset(50):
            #     return 10

            if ratio > 50:
                return 10
            elif ratio > 45:
                return 8

            elif ratio > 40:
                return 6

            elif ratio > percentiles['IndividualTrusteeOrDirectorInd_percent_female'][40]:
                return 4

            elif ratio > percentiles['IndividualTrusteeOrDirectorInd_percent_female'][20]:
                return 2

            else:
                return 0


        else: return 0


    def highest_comp(self, ratio,percentiles):
        # Logic for score 1
        if ratio:  # placeholder

            ratio = float(ratio)

            if ratio > 50:
                return 10
            elif ratio > 46:
                return 8

            elif ratio > 42:
                return 6

            elif ratio > percentiles['HighestCompensatedEmployeeInd_percent_female'][40]:
                return 4

            elif ratio > percentiles['HighestCompensatedEmployeeInd_percent_female'][20]:
                return 2

            else:
                return 0


        else: return 0

        # ... Implement other scoring methods here

    def officers(self,ratio,percentiles):
        if ratio:  # placeholder
            ratio = float(ratio)


            # if ratio == self.avgOffset(50):
            #     return 10

            if ratio > 50:
                return 10
            elif ratio > 42:
                return 8

            elif ratio > 34:
                return 6

            elif ratio > percentiles['OfficerInd_percent_female'][40]:
                return 4

            elif ratio > percentiles['OfficerInd_percent_female'][20]:
                return 2

            else:
                return 0


        else: return 0

    def pay_gap(self,ratio,percentiles):
        if ratio:  # placeholder
            ratio = float(ratio)
            if ratio > 99:
                return 0

            elif ratio > 70:
                return 2

            elif ratio > percentiles['pay_gap'][60]:
                return 4

            elif ratio > percentiles['pay_gap'][40]:
                return 6

            elif ratio > percentiles['pay_gap'][20]:
                return 8

            else:
                return 10


        else: return 0


    def avg_salary(self,ratio,percentiles):
        if ratio:  # placeholder
            ratio = float(ratio)
            if ratio > percentiles['salary_revenue_ratio'][90]:
                return 5

            elif ratio > percentiles['salary_revenue_ratio'][80]:
                return 4

            elif ratio > percentiles['salary_revenue_ratio'][60]:
                return 3

            elif ratio > percentiles['salary_revenue_ratio'][40]:
                return 2

            elif ratio > percentiles['salary_revenue_ratio'][20]:
                return 1

            else:
                return 0


        else: return 0

    def pay_ratio(self,ratio,percentiles):
        if ratio:  # placeholder#COME BACK AND REVISE

            # if ratio =='' or ratio1 =='' or float(ratio1) == 0:
            #     return 0 #YOU NEED TO CHECK WHY THIS HAPPENS
            ratio = float(ratio)
            if ratio < percentiles['CEO_pay_ratio'][20]:
                return 5

            elif ratio < percentiles['CEO_pay_ratio'][40]:
                return 4

            elif ratio < percentiles['CEO_pay_ratio'][60]:
                return 3

            elif ratio < percentiles['CEO_pay_ratio'][80]:
                return 2

            elif ratio < percentiles['CEO_pay_ratio'][90]:
                return 1

            else:
                return 0


        else: return 0



    def aggregate_scores(self, scores):
        total_score = sum(scores.values())
        # normalized_score = (total_score / 13) * (100 / 10)
        return total_score







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

@https_fn.on_request()
def update_database(req: https_fn.Request) -> https_fn.Response:

    # Access Firestore
    db = firestore.client()

    # Specify the collection
    collection_ref = db.collection('non-for-profits')  # Update with your collection name

    # Retrieve documents from the collection
    docs = collection_ref.stream()

    # Convert documents to a list of tuples (doc_id, doc_dict)
    docs_list = [(doc.id, doc.to_dict()) for doc in docs]

    for doc_id, doc_data in docs_list:
        # Retrieve 'average_salary' and 'total_revenue', defaulting to 0 if they are not present
        skip_revenue = 0
        skip_salary = 0

        try:
            average_salary = float(doc_data['metrics']['avg_employee_comp'])
        except ValueError:
            doc_data['metrics']['salary_revenue_ratio'] = 0
            doc_data['metrics']['CEO_pay_ratio'] = 0
            continue
        try:
            total_revenue = float(doc_data['metrics']['total_revenue'])
        except ValueError:
            doc_data['metrics']['salary_revenue_ratio'] = 0
            skip_revenue = 1

        try:
            highest_salary = float(doc_data['metrics']['highest_salary'])
        except ValueError:
            doc_data['metrics']['CEO_pay_ratio'] = 0
            skip_salary =1
            # Ensure that 'total_revenue' is not zero to avoid division by zero error
        if skip_revenue != 1:
            if total_revenue != 0:
                salary_to_revenue_ratio = average_salary / total_revenue
                doc_data['metrics']['salary_revenue_ratio'] = salary_to_revenue_ratio
            else:
                # Handle the case where 'total_revenue' is zero, to avoid division by zero
                # You might want to set the ratio to None or some other indicative value
                doc_data['metrics']['salary_revenue_ratio'] = 0  # or 0, or any other value you deem appropriate

        if skip_salary != 1:
            if highest_salary != 0 and average_salary != 0:
                doc_data['metrics']['CEO_pay_ratio'] = highest_salary / average_salary
            elif highest_salary == 0 and average_salary == 0:
                doc_data['metrics']['CEO_pay_ratio'] = 8
            else:
                doc_data['metrics']['CEO_pay_ratio'] = 100



    fields = [
        'average_female_salary', 'average_male_salary', 'pay_gap',
        'percent_male', 'percent_female', 'avg_employee_comp',
        'highest_salary', 'total_compensation', 'num_employees',
        'total_revenue', 'HighestCompensatedEmployeeInd_percent_female',
        'IndividualTrusteeOrDirectorInd_percent_female',
        'OfficerInd_percent_female', 'KeyEmployeeInd_percent_female',
        'FormerOfcrDirectorTrusteeInd_percent_female','salary_revenue_ratio','CEO_pay_ratio'
    ]  # Replace with your actual field names
    percentiles = [20, 40, 60, 80, 90]
    percentile_data = {}


    # Calculate and print percentiles for each field
    for field in fields:
        print(field)
        # Extract the values for the field from all documents, ensuring values are not None
        values = [
            float(doc[1]['metrics'][field]) for doc in docs_list if field in doc[1]['metrics'] and doc[1]['metrics'][field] is not None and doc[1]['metrics'][field]!='']

        if not values:  # Check if the 'values' list is empty
            print(f"No data available for field '{field}'. Skipping percentile calculation.")
            continue  # Skip the rest of the loop and move to the next field

        # Calculate percentiles since 'values' is not empty
        percentile_values = np.percentile(values, percentiles)
        percentile_data[field] = {percentile: value for percentile, value in zip(percentiles, percentile_values)}

        # Print the results
        # print(f"Percentiles for {field}:")
        # for percentile, value in zip(percentiles, percentile_values):
        #     print(f"  {percentile}th percentile: {value}")

    print(percentile_data)

    score_calculator = ScoreCalculator()
    for doc_id, doc_data in docs_list:
        new_scores = score_calculator.calculate_scores(doc_data,percentile_data)

        for key, value in new_scores.items():
            doc_data[key] = value


    # Sort the list based on your ranking criteria, e.g., a 'score' field
    # Change 'score' to your actual field name and sorting logic as needed
    sorted_docs = sorted(docs_list, key=lambda x: x[1]['final_score'], reverse=True)

    # Assign ranks and update documents
    for rank, (doc_id, doc_dict) in enumerate(sorted_docs, start=1):
        # Update the document with its rank
        # collection_ref.document(doc_id).update({'rank': rank})
        doc_dict['rank'] = rank
        # if rank ==1:
        collection_ref.document(doc_id).update(doc_dict)
        # print(f"Updated doc {doc_id} with rank {rank}, data {doc_dict}")

    return https_fn.Response("Updated Database", status=400)

