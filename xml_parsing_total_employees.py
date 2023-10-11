import xml.etree.ElementTree as ET
import requests
import csv


def efile_string(st):
    """Converts an XML tag name to those that match the
    XML tags that can be seen online. Just adds the irs
    url to the front
    """
    return "{http://www.irs.gov/efile}" + st


def save_num_employees_from_xml(xml_url, company_name):

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

    total_employees = root990.find(efile_string('EmployeeCnt'))

    # Write data to text file
    filename = f"total_compensation_{company_name}.txt"  
    f = open(filename, "w")
    f.write(total_employees.text)