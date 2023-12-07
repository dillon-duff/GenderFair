import xml.etree.ElementTree as ET
import requests
from scrape import *
import pandas as pd
from metrics import *
import uuid
import os
import zipfile_deflate64 as zipfile
import time


def find_and_extract_990(ein, filename, start_year=2021, end_year=2023):
    index_folder = "indexes"
    archive_folder = "990_xml_archive"

    for year in reversed(range(start_year, end_year + 1)):
        index_file = f"{index_folder}/index_{year}.csv"
        if os.path.exists(index_file):
            df = pd.read_csv(index_file)
            match = df[df["EIN"] == int(str(ein).replace("-", ""))]
            if not match.empty:
                object_id = match["OBJECT_ID"].values[0]
                year_folder = f"{archive_folder}/{year}"
                for zip_filename in filter(
                    lambda x: ".zip" in x, os.listdir(year_folder)
                ):
                    with zipfile.ZipFile(
                        f"{year_folder}/{zip_filename}", "r"
                    ) as zip_ref:
                        xml_filename = f"{object_id}_public.xml"
                        if xml_filename in zip_ref.namelist():
                            zip_ref.extract(xml_filename)
                            os.rename(xml_filename, f"{filename}")
                            return 0
    return -1


def find_and_extract_990_unzipped(ein, filename, start_year=2021, end_year=2023):
    index_folder = "../indexes"
    archive_folder = "../990_xml_archive"

    for year in reversed(range(start_year, end_year + 1)):
        index_file = f"{index_folder}/index_{year}.csv"
        if os.path.exists(index_file):
            df = pd.read_csv(index_file)
            match = df[df["EIN"] == int(str(ein).replace("-", ""))]
            if not match.empty:
                object_id = match["OBJECT_ID"].values[0]
                year_folder = f"{archive_folder}/{year}"

                for subdir in os.listdir(year_folder):
                    subdir_path = os.path.join(year_folder, subdir)
                    if os.path.isdir(subdir_path):
                        xml_filename = f"{object_id}_public.xml"
                        xml_file_path = os.path.join(subdir_path, xml_filename)
                        if os.path.exists(xml_file_path):
                            with open(xml_file_path, "r") as file:
                                xml_data = file.read()
                            return xml_data
    return -1


def efile_string(st):
    """Converts an XML tag name to those that match the
    XML tags that can be seen online. Just adds the irs
    url to the front
    """
    return "{http://www.irs.gov/efile}" + st


def get_990_info_for_company(ein):
    file_prefix = int(uuid.uuid1())
    xml_string = find_and_extract_990_unzipped(ein, f"{file_prefix}.xml")
    if xml_string == -1:
        # print(f"No valid XML string for EIN: {ein}")
        return -1
    info = get_990_info_from_xml(xml_string)
    if info == -1:
        # print(f"No valid XML info for EIN: {ein}")
        return -1
    try:
        os.remove(f"{file_prefix}.xml")
    except:
        pass

    return info


def get_990_info_from_xml(xml_string):
    try:
        # Parse the XML string
        tree = ET.ElementTree(ET.fromstring(xml_string))

        root = tree.getroot()

        business_name = (
            root[0].find(efile_string("Filer")).find(efile_string("BusinessName"))
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

        if not root990:
            # print("Invalid XML file, no IRS990 root.")
            return -1

        # Find the root for the Schedule J Data (Compensation Information)
        schedule_j_root = root.find(efile_string("IRS990ScheduleJ"))

        if not schedule_j_root:
            # print("Invalid XML file, no Schedule J root.")
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
            # print("Error: No employees lsited in highest compensated")
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
        grouped = names_category_pairs.groupby([1, 0]).size().unstack(fill_value=0)

        grouped_percentage = grouped.div(grouped.sum(axis=1), axis=0) * 100

        category_gender_percentage_dict = grouped_percentage.to_dict(orient='index')


        

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

        highest_paid_cumulative_comp = df["TotalCompensationFilingOrgAmt"].sum()
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
        # print(f"Error parsing XML: {e}")
        return -1
    except Exception as e:
        # print(f"An error occurred: {e}")
        return -1


if __name__ == "__main__":
    info = get_990_info_for_company("311640316")
    for key, item in info.items():
        print(f"\n{key}: {item}")
