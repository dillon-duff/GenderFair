import xml.etree.ElementTree as ET
import requests
import csv


def efile_string(st):
    """Converts an XML tag name to those that match the
    XML tags that can be seen online. Just adds the irs
    url to the front
    """
    return "{http://www.irs.gov/efile}" + st


def save_top_earners_from_xml(xml_url, company_name):

    ein = xml_url.split("object_id=")[1]

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

    # Write data to csv file
    fields = [tag for tag in employee_dicts[0].keys()]

    csv_filename = f"top_earners_{company_name}.csv"

    with open(csv_filename, 'w') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fields)

        writer.writeheader()
        writer.writerows(employee_dicts)
    print(f"CSV Saved for {company_name}")
