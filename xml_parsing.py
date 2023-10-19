import xml.etree.ElementTree as ET
import requests
from scrape import *
import pandas as pd
from metrics import *


def efile_string(st):
    """Converts an XML tag name to those that match the
    XML tags that can be seen online. Just adds the irs
    url to the front
    """
    return "{http://www.irs.gov/efile}" + st


def get_990_info_for_company(ein):

    xml_url = get_xml_url_from_ein(ein)
    info = get_990_info_from_xml(xml_url)

    return info


def get_990_info_from_xml(xml_url):
    # Get xml file response
    resp = requests.get(xml_url)

    # Save the file
    filename = '990.xml'
    with open(filename, "wb") as f:
        f.write(resp.content)

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

    # Save data for each employee in this dictionary
    employee_categories_dicts = []

    for employee in key_employee_group:
        employee_dict = {}
        for child in employee:
            tag = child.tag.replace("{http://www.irs.gov/efile}", "")
            if (tag.__eq__("IndividualTrusteeOrDirectorInd") | tag.__eq__("OfficerInd") | tag.__eq__("HighestCompensatedEmployeeInd") | tag.__eq__("KeyEmployeeInd") | tag.__eq__("FormerOfcrDirectorTrusteeInd")):
                text = tag
                tag = "Category"
            else:
                text = child.text
            employee_dict[tag] = text
        employee_categories_dicts.append(employee_dict)

    web_address = root990.find(efile_string('WebsiteAddressTxt')).text
    total_employees = root990.find(efile_string('EmployeeCnt')).text
    total_compensation = root990.find(
        efile_string('CYSalariesCompEmpBnftPaidAmt')).text

    revenue_root = root.find(efile_string("IRS990"))
    revenue = int(revenue_root.find(
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
    info = get_990_info_for_company("363673599")
    for key, item in info.items():
        print(f"\n{key}: {item}")
