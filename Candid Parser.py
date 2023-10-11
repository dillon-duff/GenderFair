import pandas as pd
import xml.etree.ElementTree as ET

def to_xml(row, root):
    company = ET.SubElement(root, "company")
    for col in row.index:
        if pd.notna(row[col]):
            ET.SubElement(company, col).text = str(row[col])
    return ET.tostring(root, encoding='unicode')


# Load spreadsheet
xl = pd.ExcelFile('Candid-Demographics-Monthly-Report (1).xlsx')

# Load a sheet into a DataFrame
df = xl.parse(xl.sheet_names[2])  # assuming the data is in the first sheet


def get_company_info():
    company_name = input("Enter the company name: ")
    if company_name in df['org_name'].values:  # assuming 'Company' is the column with company names
        company_info = df.loc[df['org_name'] == company_name]
        for col in company_info.columns:
            if pd.notna(company_info[col].values[0]):  # check if the value is not NaN
                print(f"{col}: {company_info[col].values[0]}")
        company_info.to_csv(f"{company_name}.csv", index=False)
    else:
        print("Company not found.")

while True:
    get_company_info()