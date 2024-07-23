import firebase_admin
from firebase_admin import firestore
from firebase_admin import credentials
import csv
import os


import openpyxl

##WHAT TO DO WITH CREDENTIAL JSON?
# Insecure to store in public repository
#TODO: MAKE SECURE
cred = credentials.Certificate("/Users/afrodaddy/Downloads/gender-fair-82d21-firebase-adminsdk-xzaw3-1fcb30d6c4.json")

firebase_admin.initialize_app(cred)


db = firestore.client()
batch = db.batch()


def connect_to_database():
    #TODO: IMPLEMENT METHOD
    return
def add_company(company_json):
    #TODO: IMPLEMENT METHOD
    #ADD COMPANY TO FIREBASE
    return
def remove_company(company_id):
    #TODO: IMPLEMENT METHOD
    #REMOVE COMPANY FROM FIREBASE
    return

def populate_database():
    add_candid_data()
    add_990_data()
    return


def add_990_data():
    #LOOP THROUGH CSV ADDING TO FIREBASE
    # default_excel_file = "PercentageCalculated.xlsx"
    # workbook = openpyxl.load_workbook(default_excel_file)
    # sheet = workbook.active  # Gets the active sheet
    # header_row = sheet[1]
    # COLUMN_MAP = {cell.value: count for count,cell in enumerate(header_row)}
    files = os.listdir('split_csvs')

# Loop through each file in the folder
    for file_name in files:
        # Create the full file path
        file_path = os.path.join('split_csvs', file_name)
        with open(file_path) as f:
            reader = csv.DictReader(f)
            for row in enumerate(reader):
                docRef = db.collection("non-for-profits").document(); #automatically generate unique id
                entry = build_company_from_990_data(row[1])
                batch.set(docRef, entry);
        batch.commit()
    return


def get_company(company):
    #RETURN COMPANY FROM FIREBASE
    #TODO: IMPLEMENT METHOD
    return

def build_company_from_990_data(csv_row):
    csv_json = {"ein": csv_row["ein"],
                "name": csv_row["org_name"],
                "category": csv_row["category"],
                "metrics":{"average_female_salary" : csv_row["average_female_salary"],
                          "average_male_salary" : csv_row["average_male_salary"],
                          "pay_gap" : csv_row["pay_gap"],
                          "percent_male" : csv_row["percent_male"],
                          "percent_female" : csv_row["percent_female"],
                          "avg_employee_comp" : csv_row["avg_employee_comp"],
                          "highest_salary" : csv_row["highest_salary"],
                          "total_compensation" : csv_row["total_compensation"],
                          "web_address" : csv_row["web_address"],
                          "num_employees" : csv_row["num_employees"],
                          "total_revenue" : csv_row["total_revenue"],
                          "HighestCompensatedEmployeeInd_percent_female": csv_row["HighestCompensatedEmployeeInd_percent_female"],
                          "IndividualTrusteeOrDirectorInd_percent_female": csv_row["IndividualTrusteeOrDirectorInd_percent_female"],
                          "OfficerInd_percent_female":csv_row["OfficerInd_percent_female"],
                          "KeyEmployeeInd_percent_female": csv_row["KeyEmployeeInd_percent_female"],
                          "FormerOfcrDirectorTrusteeInd_percent_female":csv_row["FormerOfcrDirectorTrusteeInd_percent_female"]
                }        
    }
    return csv_json


def build_company_from_candid_data(csv_row):
    csv_json = {"ein": csv_row['ein'],
                "name": csv_row["org_name"],
                "city": csv_row["city"],
                "state": csv_row["state_code"],
                "category": csv_row["category"],
                "web": csv_row["web_address"],
                "total_board_members": csv_row["total_board"],

                "board_race":{"asian": csv_row["asian_board"],
                            "black": csv_row["black_board"],
                            "hispanic": csv_row["hispanic_board"],
                            "middle_eastern": csv_row["middle_eastern_board"],
                            "multi_racial": csv_row["multi_racial_board"],
                            "native_american": csv_row["native_american_board"],
                            "pacific_islander": csv_row["pacific_islander_board"],
                            "white": csv_row["white_board"],
                            "other": csv_row["other_ethnicity_board"],
                            "unknown": csv_row["race_unknown_board"],
                            "declined": csv_row["race_decline_to_state_board"]},

                "board_gender":{"female": csv_row["female_board"],
                                 "male": csv_row["male_board"],
                                 "transgender": csv_row["trans_board"],
                                 "cis": csv_row["cis_board"],
                                 "non_binary": csv_row["non_binary_board"],
                "unknown": csv_row["gender_unknown_board"] if csv_row["gender_unknown_board"] != None else 0 + 
                            csv_row["gender2_unknown_board"] if csv_row["gender2_unknown_board"]  != None else 0,
                "declined": csv_row["gender_decline_to_state_board"] if csv_row["gender_decline_to_state_board"] !=None else 0
                                   + csv_row["gender2_decline_to_state_board"] if csv_row["gender2_decline_to_state_board"] !=None else 0},

                "total_senior_staff_members": csv_row["total_senior_staff"],

                "senior_staff_race":{"asian": csv_row["asian_senior_staff"],
                            "black": csv_row["black_senior_staff"],
                            "hispanic": csv_row["hispanic_senior_staff"],
                            "middle_eastern": csv_row["middle_eastern_senior_staff"],
                            "multi_racial": csv_row["multi_racial_senior_staff"],
                            "native_american": csv_row["native_american_senior_staff"],
                            "pacific_islander": csv_row["pacific_islander_senior_staff"],
                            "white": csv_row["white_senior_staff"],
                            "other": csv_row["other_ethnicity_senior_staff"],
                            "unknown": csv_row["race_unknown_senior_staff"],
                            "declined": csv_row["race_decline_to_state_senior_staff"]},

                "senior_staff_gender":{"female": csv_row["female_senior_staff"],
                                 "male": csv_row["male_senior_staff"],
                                 "transgender": csv_row["trans_senior_staff"],
                                 "cis": csv_row["cis_senior_staff"],
                                 "non_binary": csv_row["non_binary_senior_staff"],
                                 "unknown": csv_row["gender_unknown_senior_staff"] if csv_row["gender_unknown_senior_staff"] != None else 0 + 
                            csv_row["gender2_unknown_senior_staff"] if csv_row["gender2_unknown_senior_staff"]  != None else 0,
                "declined": csv_row["gender_decline_to_state_senior_staff"] if csv_row["gender_decline_to_state_senior_staff"] !=None else 0
                                   + csv_row["gender2_decline_to_state_senior_staff"] if csv_row["gender2_decline_to_state_senior_staff"] !=None else 0},


                "total_staff_members": csv_row["total_staff"],

                "staff_race":{"asian": csv_row["asian_staff"],
                            "black": csv_row["black_staff"],
                            "hispanic": csv_row["hispanic_staff"],
                            "middle_eastern": csv_row["middle_eastern_staff"],
                            "multi_racial": csv_row["multi_racial_staff"],
                            "native_american": csv_row["native_american_staff"],
                            "pacific_islander": csv_row["pacific_islander_staff"],
                            "white": csv_row["white_staff"],
                            "other": csv_row["other_ethnicity_staff"],
                            "unknown": csv_row["race_unknown_staff"],
                            "declined": csv_row["race_decline_to_state_staff"]},

                "staff_gender":{"female": csv_row["female_staff"],
                                 "male": csv_row["male_staff"],
                                 "transgender": csv_row["trans_staff"],
                                 "cis": csv_row["cis_staff"],
                                 "non_binary": csv_row["non_binary_staff"],
                                 "unknown": csv_row["gender_unknown_staff"] if csv_row["gender_unknown_staff"] != None else 0 + 
                            csv_row["gender2_unknown_staff"] if csv_row["gender2_unknown_staff"]  != None else 0,
                "declined": csv_row["gender_decline_to_state_staff"] if csv_row["gender_decline_to_state_staff"] !=None else 0
                                   + csv_row["gender2_decline_to_state_staff"] if csv_row["gender2_decline_to_state_staff"] !=None else 0},

                "metrics":{"average_female_salary" : csv_row["average_female_salary"],
                          "average_male_salary" : csv_row["average_male_salary"],
                          "pay_gap" : csv_row["pay_gap"],
                          "percent_male" : csv_row["percent_male"],
                          "percent_female" : csv_row["percent_female"],
                          "avg_employee_comp" : csv_row["avg_employee_comp"],
                          "highest_salary" : csv_row["highest_salary"],
                          "total_compensation" : csv_row["total_compensation"],
                          "web_address" : csv_row["web_address"],
                          "num_employees" : csv_row["num_employees"],
                          "total_revenue" : csv_row["total_revenue"],
                          "HighestCompensatedEmployeeInd_percent_female": csv_row["HighestCompensatedEmployeeInd_percent_female"],
                          "IndividualTrusteeOrDirectorInd_percent_female": csv_row["IndividualTrusteeOrDirectorInd_percent_female"],
                          "OfficerInd_percent_female":csv_row["OfficerInd_percent_female"],
                          "KeyEmployeeInd_percent_female": csv_row["KeyEmployeeInd_percent_female"],
                          "FormerOfcrDirectorTrusteeInd_percent_female":csv_row["FormerOfcrDirectorTrusteeInd_percent_female"],
                }        
    }
    return csv_json

def add_candid_data():
    with open('Candid-Top-2-3.csv','r') as f:
        reader = csv.DictReader(f)
        for row in enumerate(reader):
            docRef = db.collection("non-for-profits").document(); #automatically generate unique id
            entry = build_company_from_candid_data(row[1])
            batch.set(docRef, entry);
    batch.commit()
    return

populate_database()
