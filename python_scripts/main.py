import os
import random
from io import BytesIO, StringIO
from multiprocessing import Pool
import pandas as pd
import requests
import xml.etree.ElementTree as ET
from typing import Dict, List, Optional, Union
from pydantic import BaseModel
import argparse
from tqdm import tqdm
import traceback
import sqlite3
from main_logger import MultiprocessSafeLogger, with_logging


class Config:
    INDEX_FOLDER = "indexes"
    ARCHIVE_FOLDER = "990_xml_archive"
    START_YEAR = 2021
    END_YEAR = 2023
    CANDID_DEMOGRAPHICS_URL = "https://info.candid.org/candid-demographics"
    IRS_BASE_URL = "https://www.irs.gov/pub/irs-soi/"
    IRS_FILE_NAMES = ["eo1.csv", "eo2.csv", "eo3.csv", "eo4.csv"]
    GENDER_CSV_PATH = "first_name_gender_probabilities.csv"
    LOG_FILE = "npo_rankings_pipeline.log"
    RESULTS_FOLDER = "results"

class IRS990Extractor:
    def __init__(self):
        self.db_path = 'irs990_index.db'
        self.initialize_database()

    def initialize_database(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS irs990_index (
                ein INTEGER,
                year INTEGER,
                object_id TEXT,
                file_path TEXT,
                PRIMARY KEY (ein, year)
            )
        ''')
        conn.commit()
        conn.close()

    def populate_database(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        for year in range(Config.START_YEAR, Config.END_YEAR + 1):
            index_file = f"{Config.INDEX_FOLDER}/index_{year}.csv"
            if os.path.exists(index_file):
                df = pd.read_csv(index_file)
                for _, row in df.iterrows():
                    ein = int(str(row['EIN']).replace("-", ""))
                    object_id = row['OBJECT_ID']
                    year_folder = f"{Config.ARCHIVE_FOLDER}/{year}"
                    for subdir in os.listdir(year_folder):
                        subdir_path = os.path.join(year_folder, subdir)
                        if os.path.isdir(subdir_path):
                            xml_filename = f"{object_id}_public.xml"
                            xml_file_path = os.path.join(subdir_path, xml_filename)
                            if os.path.exists(xml_file_path):
                                cursor.execute('''
                                    INSERT OR REPLACE INTO irs990_index (ein, year, object_id, file_path)
                                    VALUES (?, ?, ?, ?)
                                ''', (ein, year, object_id, xml_file_path))
                                break
        
        conn.commit()
        conn.close()

    def find_and_extract_990(self, ein: str) -> Union[str, int]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        ein = int(str(ein).replace("-", ""))
        cursor.execute('''
            SELECT file_path FROM irs990_index
            WHERE ein = ?
            ORDER BY year DESC
            LIMIT 1
        ''', (ein,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            file_path = result[0]
            with open(file_path, 'r') as file:
                return file.read()
        return -1

extractor = IRS990Extractor()
logger = MultiprocessSafeLogger('logs/npo_rankings_pipeline.log')


class Employee(BaseModel):
    name: str
    gender: str
    compensation: float
    category: str

class OrganizationInfo(BaseModel):
    ein: str
    org_name: str
    web_address: str
    num_employees: int
    total_revenue: float
    total_compensation: float
    highest_salary: float
    avg_employee_comp: float
    pay_gap: float
    percent_male: float
    percent_female: float
    category_gender_percentages: Dict[str, float]



def efile_string(st: str) -> str:
    return "{http://www.irs.gov/efile}" + st


gender_df = pd.read_csv(Config.GENDER_CSV_PATH)
gender_df['Name'] = gender_df['Name'].str.lower()
gender_dict = dict(zip(gender_df['Name'], gender_df['female_prob']))

def guess_gender(name: str) -> str:
    name = name.lower().split()[0]
    prob = gender_dict.get(name, 0.5)
    return 'F' if random.random() < prob else 'M'

@with_logging(logger)
def get_candid_top_df() -> pd.DataFrame:
    logger.info("Fetching Candid data...")
    resp = requests.get(Config.CANDID_DEMOGRAPHICS_URL)
    resp.raise_for_status()
    df = pd.read_excel(BytesIO(resp.content), sheet_name="Organizations")
    df = df[df["total_staff"] >= 50].reset_index(drop=True)
    logger.info(f"Fetched {len(df)} organizations from Candid")
    return df.apply(lambda col: pd.to_numeric(col, errors="ignore"))

@with_logging(logger)
def get_990_top_df(min_revenue: float) -> pd.DataFrame:
    logger.info(f"Fetching 990 data for organizations with revenue >= ${min_revenue:,.2f}")
    dataframes = []
    for file_name in tqdm(Config.IRS_FILE_NAMES, desc="Fetching IRS files"):
        response = requests.get(Config.IRS_BASE_URL + file_name)
        response.raise_for_status()
        df = pd.read_csv(StringIO(response.text))
        dataframes.append(df)

    combined_df = pd.concat(dataframes, ignore_index=True)
    combined_df = combined_df.dropna(subset=["INCOME_AMT"])
    result_df = combined_df[combined_df["INCOME_AMT"] >= min_revenue]
    logger.info(f"Fetched {len(result_df)} organizations from 990 data")
    return result_df

class XML990ParseError(Exception):
    """Base exception for 990 XML parsing errors"""
    pass

class Missing990RootError(XML990ParseError):
    """Raised when the 990 root is missing"""
    pass

class MissingScheduleJRootError(XML990ParseError):
    """Raised when the Schedule J root is missing"""
    pass

class MissingEmployeesError(XML990ParseError):
    """Raised when no employees are found"""
    pass

@with_logging(logger)
def parse_990_xml(xml_string: str) -> Optional[OrganizationInfo]:
    try:
        root = ET.fromstring(xml_string)
        business_name = root[0].find(efile_string("Filer")).find(efile_string("BusinessName"))
        org_name = "".join(c.text for c in business_name)

        root990 = root[1].find(efile_string("IRS990"))
        schedule_j_root = root[1].find(efile_string("IRS990ScheduleJ"))

        if not root990:
            raise Missing990RootError("Missing 990 root in XML")

        if not schedule_j_root:
            raise MissingScheduleJRootError("Missing Schedule J root in XML")

        employees = parse_employees(schedule_j_root, root990)
        if not employees:
            raise MissingEmployeesError("No employees found in XML")
                
        total_compensation = float(root990.find(efile_string("CYSalariesCompEmpBnftPaidAmt")).text)
        web_address = root990.find(efile_string("WebsiteAddressTxt"))
        web_address = web_address.text if web_address is not None else "N/A"
        total_employees = int(root990.find(efile_string("EmployeeCnt")).text)
        revenue = float(root990.find(efile_string("CYTotalRevenueAmt")).text)
        
        return calculate_organization_metrics(employees, total_compensation, web_address, total_employees, revenue, org_name)

    except (Missing990RootError, MissingScheduleJRootError, MissingEmployeesError) as e:
        logger.error(f"Error parsing 990 XML: {str(e)}")
        return None
    except ET.ParseError as e:
        logger.error(f"ET XML parsing error: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error parsing 990 XML: {traceback.format_exc()}")
        return None

def parse_employees(schedule_j_root: ET.Element, root990: ET.Element) -> List[Employee]:
    key_employee_group = schedule_j_root.findall(efile_string("RltdOrgOfficerTrstKeyEmplGrp"))
    key_employee_group_categories = root990.findall(efile_string("Form990PartVIISectionAGrp"))

    employees = []
    for emp_data, emp_category in zip(key_employee_group, key_employee_group_categories):
        name = emp_data.find(efile_string("PersonNm")).text
        compensation = float(emp_data.find(efile_string("TotalCompensationFilingOrgAmt")).text)
        category = next(cat for cat in emp_category if cat.tag.endswith("Ind")).tag.replace("{http://www.irs.gov/efile}", "")
        employees.append(Employee(name=name, gender=guess_gender(name), compensation=compensation, category=category))

    return employees

def calculate_organization_metrics(employees: List[Employee], total_compensation: float, web_address: str, 
                                   total_employees: int, revenue: float, org_name: str) -> OrganizationInfo:
    for emp in employees:
        emp.gender = guess_gender(emp.name.split()[0])

    df = pd.DataFrame([emp.model_dump() for emp in employees])
    gender_metrics = calculate_gender_metrics(df)
    category_gender_percentages = calculate_category_gender_percentages(df)

    highest_paid_cumulative_comp = df["compensation"].sum()
    num_highest_comp_employees = len(employees)

    num_non_highest_comp_employees = total_employees - num_highest_comp_employees
    avg_employee_comp = (total_compensation - highest_paid_cumulative_comp) / num_non_highest_comp_employees if num_non_highest_comp_employees != 0 else 0

    return OrganizationInfo(
        ein="",
        org_name=org_name,
        web_address=web_address,
        num_employees=total_employees,
        total_revenue=revenue,
        total_compensation=total_compensation,
        highest_salary=df["compensation"].max(),
        avg_employee_comp=avg_employee_comp,
        pay_gap=gender_metrics["pay_gap"],
        percent_male=gender_metrics["percent_male"],
        percent_female=gender_metrics["percent_female"],
        category_gender_percentages=category_gender_percentages
    )

@with_logging(logger)
def calculate_gender_metrics(df: pd.DataFrame) -> Dict[str, float]:
    try:
        gender_grouped = df.groupby("gender").agg({"compensation": ["sum", "count"]})
        gender_grouped.columns = ["total_comp", "count"]
        male_data = gender_grouped.loc["M"] if "M" in gender_grouped.index else pd.Series({"total_comp": 0, "count": 0})
        female_data = gender_grouped.loc["F"] if "F" in gender_grouped.index else pd.Series({"total_comp": 0, "count": 0})
        
        total_count = male_data["count"] + female_data["count"]
        
        if total_count == 0:
            logger.warning("No gender data available")
            return {"pay_gap": -1, "percent_male": 0, "percent_female": 0}
        
        avg_male_salary = male_data["total_comp"] / male_data["count"] if male_data["count"] > 0 else 0
        avg_female_salary = female_data["total_comp"] / female_data["count"] if female_data["count"] > 0 else 0
        
        if avg_male_salary > 0 and avg_female_salary > 0:
            pay_gap = ((avg_male_salary - avg_female_salary) / avg_male_salary * 100)
        elif avg_male_salary > 0:
            pay_gap = 100 
        elif avg_female_salary > 0:
            pay_gap = -100
        else:
            pay_gap = -1
        
        percent_male = (male_data["count"] / total_count * 100)
        percent_female = (female_data["count"] / total_count * 100)
        
        return {
            "pay_gap": pay_gap,
            "percent_male": percent_male,
            "percent_female": percent_female
        }
    except Exception as e:
        logger.error(f"Unexpected error in calculate_gender_metrics: {traceback.format_exc()}")
        return {"pay_gap": -1, "percent_male": 0, "percent_female": 0}

@with_logging(logger)
def calculate_category_gender_percentages(df: pd.DataFrame) -> Dict[str, float]:
    try:
        category_gender = df.groupby(["category", "gender"]).size().unstack(fill_value=0)
        
        if 'M' not in category_gender.columns:
            category_gender['M'] = 0
        if 'F' not in category_gender.columns:
            category_gender['F'] = 0
        
        category_gender_percentage = category_gender.div(category_gender.sum(axis=1), axis=0) * 100
        
        result = {}
        for category, percentage in category_gender_percentage.iterrows():
            female_percentage = percentage.get('F', 0)
            result[f"{category}_percent_female"] = female_percentage
        
        return result
    except Exception as e:
        logger.error(f"Error in calculate_category_gender_percentages: {traceback.format_exc()}")
        return {}

@with_logging(logger)
def process_organization(row: pd.Series) -> Optional[OrganizationInfo]:
    try:
        ein = row["ein"]
        xml_string = extractor.find_and_extract_990(ein)
        if xml_string == -1:
            logger.warning(f"No XML data found for EIN {ein}")
            return None
        info = parse_990_xml(xml_string)
        if info:
            info.ein = ein
            logger.info(f"Successfully processed organization with EIN {ein}")
            return info
        else:
            logger.warning(f"Failed to parse XML data for EIN {ein}")
    except Exception as e:
        logger.error(f"Error processing organization with EIN {row['ein']}: {traceback.format_exc()}")
    return None

@with_logging(logger)
def save_results(df: pd.DataFrame, filename: str):
    os.makedirs(Config.RESULTS_FOLDER, exist_ok=True)
    file_path = os.path.join(Config.RESULTS_FOLDER, filename)
    df.to_csv(file_path, index=False)
    logger.info(f"Results saved to {file_path}")

@with_logging(logger)
def main(args):
    logger.info("Starting NPO Rankings Pipeline")

    candid_top_df = get_candid_top_df()

    logger.info("Processing Candid organizations...")
    with Pool(os.cpu_count() - 1) as pool:
        candid_results = list(tqdm(
            pool.imap(process_organization, [row for _, row in candid_top_df.iterrows()]),
            total=len(candid_top_df),
            desc="Processing Candid orgs"
        ))

    candid_top_df = pd.DataFrame([r.model_dump() for r in candid_results if r is not None])
    save_results(candid_top_df, "Candid-Top-Results.csv")

    min_revenue = candid_top_df["total_revenue"].min()
    logger.info(f"Minimum revenue threshold: ${min_revenue:,.2f}")

    irs990_top_df = get_990_top_df(min_revenue=min_revenue).rename(columns={"EIN": "ein"}).loc[:, ["ein"]]

    logger.info("Processing 990 organizations...")
    with Pool(os.cpu_count() - 1) as pool:
        irs990_results = list(tqdm(
            pool.imap(process_organization, [row for _, row in irs990_top_df.iterrows()]),
            total=len(irs990_top_df),
            desc="Processing 990 orgs"
        ))

    irs990_top_df = pd.DataFrame([r.model_dump() for r in irs990_results if r is not None])
    save_results(irs990_top_df, "IRS990-Top-Results.csv")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="NPO Rankings Pipeline")
    args = parser.parse_args()
    main(args)

