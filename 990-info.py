from main import *
from xml_parsing import *
import requests


def populate_990_fields(filename):
    pass


def get_990_info_for_company(company_name):
    ordered_eins = get_best_matching_eins_from_company_name(company_name)
    if len(ordered_eins) == 0:
        print(
            f"Failed to find any company with name similar to: {company_name}")

    url_for_xml = None
    done = False
    for e, name in ordered_eins:
        url_for_xml = None
        next_xml_url = get_xml_url_from_ein(e)
        if next_xml_url != -1:
            url_for_xml = next_xml_url
            info = get_990_info_from_xml(url_for_xml)
            if info != -1:
                done = True
                break
                
    if not done:
        print(f"No valid 990s could be found for {company_name}")
        return -1

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

    # The root currently has ReturnHeader and ReturnData as children.
    # We are only concerned with the ReturnData so we can
    # redefine the root from being the parents of both of these
    # to being ReturnData
    root = root[1]

    # Find the root for the Schedule J Data (Compensation Information)
    root990 = root.find(efile_string('IRS990'))

    if not root990:
        print("Invalid XML file. Could be submitted under protest")
        return -1
        
    # Find the root for the Schedule J Data (Compensation Information)
    schedule_j_root = root.find(efile_string('IRS990ScheduleJ'))

    if not schedule_j_root:
        print("Invalid XML file. Could be submitted under protest")
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

    total_compensation = root990.find(
        efile_string('CYSalariesCompEmpBnftPaidAmt')).text
    
    key_employee_group = root990.findall(efile_string('Form990PartVIISectionAGrp'))

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
    total_compensation = root990.find(efile_string('CYSalariesCompEmpBnftPaidAmt')).text

    info = {"top_earners": employee_dict, "total_compensation": total_compensation, "categories": employee_categories_dicts,
            "web_address": web_address, "num_employees": total_employees, "total_compensation": total_compensation}

    return info
    


if __name__ == "__main__":
    print(get_990_info_for_company("Feeding America"))