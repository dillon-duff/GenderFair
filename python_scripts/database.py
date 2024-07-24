import firebase_admin
from firebase_admin import firestore
from firebase_admin import credentials

cred = credentials.Certificate("gender-fair-82d21-firebase-adminsdk-xzaw3-9b1027afcf.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

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
