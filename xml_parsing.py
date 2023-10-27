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
    index_folder = 'indexes'
    archive_folder = '990_xml_archive'

    for year in reversed(range(start_year, end_year+1)):
        index_file = f'{index_folder}/index_{year}.csv'
        if os.path.exists(index_file):
            df = pd.read_csv(index_file)            
            match = df[df['EIN'] == int(ein.replace("-", ""))]
            if not match.empty:
                object_id = match['OBJECT_ID'].values[0]
                year_folder = f'{archive_folder}/{year}'
                for zip_filename in filter(lambda x : ".zip" in x, os.listdir(year_folder)):
                    with zipfile.ZipFile(f'{year_folder}/{zip_filename}', 'r') as zip_ref:
                        xml_filename = f'{object_id}_public.xml'
                        if xml_filename in zip_ref.namelist():
                            zip_ref.extract(xml_filename)
                            os.rename(xml_filename, f'{filename}')
                            return 0
    return -1


def efile_string(st):
    """Converts an XML tag name to those that match the
    XML tags that can be seen online. Just adds the irs
    url to the front
    """
    return "{http://www.irs.gov/efile}" + st


def get_990_info_for_company(ein):
    file_prefix = int(uuid.uuid1())
    start = time.time()
    find_and_extract_990(ein, f'{file_prefix}.xml')
    end = time.time()
    print(f"Extraction took {abs(start-end)} seconds")
    start = time.time()
    info = get_990_info_from_xml(file_prefix)
    end = time.time()
    print(f"Getting info took {end-start} seconds")
    try:
        os.remove(f'{file_prefix}.xml')
    except:
        pass

    if info == -1:
        return -1

    return info


def get_990_info_from_xml(file_prefix):

    filename = f'{file_prefix}.xml'

    if filename not in os.listdir():
        return -1
    # Parse the XML
    tree = ET.parse(filename)

    root = tree.getroot()

    business_name = root[0].find(efile_string('Filer')).find(
        efile_string('BusinessName'))
    org_name = ""
    for c in business_name:
        org_name += c.text

    # The root currently has ReturnHeader and ReturnData as children.
    # We are only concerned with the ReturnData so we can
    # redefine the root from being the parents of both of these
    # to being ReturnData
    root = root[1]

    # Find the root for the Schedule J Data (Compensation Information)
    root990 = root.find(efile_string('IRS990'))

    if not root990:
        print("Invalid XML file, no IRS990 root.")
        return -1

    # Find the root for the Schedule J Data (Compensation Information)
    schedule_j_root = root.find(efile_string('IRS990ScheduleJ'))

    if not schedule_j_root:
        print("Invalid XML file, no Schedule J root.")
        return -1

    key_employee_group = schedule_j_root.findall(
        efile_string('RltdOrgOfficerTrstKeyEmplGrp'))

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
        return -1

    total_compensation = root990.find(
        efile_string('CYSalariesCompEmpBnftPaidAmt')).text

    key_employee_group = root990.findall(
        efile_string('Form990PartVIISectionAGrp'))

    # # Save data for each employee in this dictionary
    # employee_categories_dicts = []

    # for employee in key_employee_group:
    #     employee_dict = {}
    #     for child in employee:
    #         tag = child.tag.replace("{http://www.irs.gov/efile}", "")
    #         if (tag.__eq__("IndividualTrusteeOrDirectorInd") | tag.__eq__("OfficerInd") | tag.__eq__("HighestCompensatedEmployeeInd") | tag.__eq__("KeyEmployeeInd") | tag.__eq__("FormerOfcrDirectorTrusteeInd")):
    #             text = tag
    #             tag = "Category"
    #         else:
    #             text = child.text
    #         employee_dict[tag] = text
    #     employee_categories_dicts.append(employee_dict)

    web_address = 'N/A' if root990.find(efile_string('WebsiteAddressTxt')
                                        ) is None else root990.find(efile_string('WebsiteAddressTxt')).text
    total_employees = -1 if root990.find(efile_string(
        'EmployeeCnt')) is None else root990.find(efile_string('EmployeeCnt')).text
    total_compensation = -1 if root990.find(
        efile_string('CYSalariesCompEmpBnftPaidAmt')) is None else root990.find(
        efile_string('CYSalariesCompEmpBnftPaidAmt')).text

    revenue_root = root.find(efile_string("IRS990"))
    revenue = -1 if revenue_root is None else int(revenue_root.find(
        efile_string("CYTotalRevenueAmt")).text)

    df = pd.DataFrame(employee_dicts)

    if 'TotalCompensationFilingOrgAmt' in df:
        df['TotalCompensationFilingOrgAmt'] = df['TotalCompensationFilingOrgAmt'].astype(
            'float64')
    if 'TotalCompensationRltdOrgsAmt' in df:
        df['TotalCompensationRltdOrgsAmt'] = df['TotalCompensationRltdOrgsAmt'].astype(
            'float64')

    info = generate_pay_gap_metric(df)
    if info == -1:
        return -1
    info['total_compensation'] = total_compensation
    info['web_address'] = web_address
    info['num_employees'] = total_employees
    info['total_revenue'] = revenue
    info['org_name'] = org_name

    # info = {"top_earners": employee_dicts, "total_compensation": total_compensation, "categories": employee_categories_dicts,
    #         "web_address": web_address, "num_employees": total_employees, "total_compensation": total_compensation, "total_revenue": revenue}
    return info


if __name__ == "__main__":
    info = get_990_info_for_company("205138278")
    for key, item in info.items():
        print(f"\n{key}: {item}")
