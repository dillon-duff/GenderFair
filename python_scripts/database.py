import firebase_admin
from firebase_admin import firestore
from firebase_admin import credentials




import openpyxl

##WHAT TO DO WITH CREDENTIAL JSON?
# Insecure to store in public repository
cred = credentials.Certificate("cred.json")

firebase_admin.initialize_app(cred)
db = firestore.client()
batch = db.batch()

def connect_to_database():
    return
def add_company(company_json):
    #ADD COMPANY TO FIREBASE
    return
def remove_company(company_id):
    #REMOVE COMPANY FROM FIREBASE
    return
def add_all_companies_from_xl():
    #LOOP THROUGH CSV ADDING TO FIREBASE
    default_excel_file = "PercentageCalculated.xlsx"
    workbook = openpyxl.load_workbook(default_excel_file)
    sheet = workbook.active  # Gets the active sheet
    header_row = sheet[1]
    COLUMN_MAP = {cell.value: count for count,cell in enumerate(header_row)}
    for count,row in enumerate(sheet.iter_rows(values_only=True)):
        if(count>1):
            docRef = db.collection("non-for-profits").doc(); #automatically generate unique id
            batch.set(docRef, build_company_from_xl(row));
    batch.commit()
    return
def get_company(company):
    #RETURN COMPANY FROM FIREBASE
    return

def build_company_from_xl(xl_row):
    csv_json = {"ein": xl_row[COLUMN_MAP["ein"]],
                "name": xl_row[COLUMN_MAP["org_name"]],
                "city": xl_row[COLUMN_MAP["city"]],
                "state": xl_row[COLUMN_MAP["state_code"]],

                "leaders": {"gender": xl_row[COLUMN_MAP["gender1_leader"]],
                            "race": xl_row[COLUMN_MAP["race_leader"]],
                            "orientation": xl_row[COLUMN_MAP["orientation_leader"]],
                            "disability": xl_row[COLUMN_MAP["disability_status_leader"]]},

                "total_board_members": xl_row[COLUMN_MAP["total_board"]],

                "board_race":{"asian": xl_row[COLUMN_MAP["asian_board"]],
                            "black": xl_row[COLUMN_MAP["black_board"]],
                            "hispanic": xl_row[COLUMN_MAP["hispanic_board"]],
                            "middle_eastern": xl_row[COLUMN_MAP["middle_eastern_board"]],
                            "multi_racial": xl_row[COLUMN_MAP["multi_racial_board"]],
                            "native_american": xl_row[COLUMN_MAP["native_american_board"]],
                            "pacific_islander": xl_row[COLUMN_MAP["pacific_islander_board"]],
                            "white": xl_row[COLUMN_MAP["white_board"]],
                            "other": xl_row[COLUMN_MAP["other_ethnicity_board"]],
                            "unknown": xl_row[COLUMN_MAP["race_unknown_board"]],
                            "declined": xl_row[COLUMN_MAP["race_decline_to_state_board"]]},

                "board_gender":{"female": xl_row[COLUMN_MAP["female_board"]],
                                 "male": xl_row[COLUMN_MAP["male_board"]],
                                 "transgender": xl_row[COLUMN_MAP["trans_board"]],
                                 "cis": xl_row[COLUMN_MAP["cis_board"]],
                                 "non_binary": xl_row[COLUMN_MAP["non_binary_board"]],
                "unknown": xl_row[COLUMN_MAP["gender_unknown_board"]] if xl_row[COLUMN_MAP["gender_unknown_board"]] != None else 0 + 
                            xl_row[COLUMN_MAP["gender2_unknown_board"]] if xl_row[COLUMN_MAP["gender2_unknown_board"]]  != None else 0,
                "declined": xl_row[COLUMN_MAP["gender_decline_to_state_board"]] if xl_row[COLUMN_MAP["gender_decline_to_state_board"]] !=None else 0
                                   + xl_row[COLUMN_MAP["gender2_decline_to_state_board"]] if xl_row[COLUMN_MAP["gender2_decline_to_state_board"]] !=None else 0},

                "board_orientation":{"straight": xl_row[COLUMN_MAP["straight_board"]],
                                    "lgbtqia": xl_row[COLUMN_MAP["lgbtqia_board"]],
                                    "unknown": xl_row[COLUMN_MAP["orientation_unknown_board"]],
                                    "declined": xl_row[COLUMN_MAP["orientation_decline_to_state_board"]] },
                
                "board_disability":{"with_disability": xl_row[COLUMN_MAP["with_disability_board"]],
                                    "without_disability": xl_row[COLUMN_MAP["without_disability_board"]],
                                    "unknown": xl_row[COLUMN_MAP["disability_unknown_board"]],
                                    "declined": xl_row[COLUMN_MAP["disability_decline_to_state_board"]]},

                "total_senior_staff_members": xl_row[COLUMN_MAP["total_senior_staff"]],

                "senior_staff_race":{"asian": xl_row[COLUMN_MAP["asian_senior_staff"]],
                            "black": xl_row[COLUMN_MAP["black_senior_staff"]],
                            "hispanic": xl_row[COLUMN_MAP["hispanic_senior_staff"]],
                            "middle_eastern": xl_row[COLUMN_MAP["middle_eastern_senior_staff"]],
                            "multi_racial": xl_row[COLUMN_MAP["multi_racial_senior_staff"]],
                            "native_american": xl_row[COLUMN_MAP["native_american_senior_staff"]],
                            "pacific_islander": xl_row[COLUMN_MAP["pacific_islander_senior_staff"]],
                            "white": xl_row[COLUMN_MAP["white_senior_staff"]],
                            "other": xl_row[COLUMN_MAP["other_ethnicity_senior_staff"]],
                            "unknown": xl_row[COLUMN_MAP["race_unknown_senior_staff"]],
                            "declined": xl_row[COLUMN_MAP["race_decline_to_state_senior_staff"]]},

                "senior_staff_gender":{"female": xl_row[COLUMN_MAP["female_senior_staff"]],
                                 "male": xl_row[COLUMN_MAP["male_senior_staff"]],
                                 "transgender": xl_row[COLUMN_MAP["trans_senior_staff"]],
                                 "cis": xl_row[COLUMN_MAP["cis_senior_staff"]],
                                 "non_binary": xl_row[COLUMN_MAP["non_binary_senior_staff"]],
                                 "unknown": xl_row[COLUMN_MAP["gender_unknown_senior_staff"]] if xl_row[COLUMN_MAP["gender_unknown_senior_staff"]] != None else 0 + 
                            xl_row[COLUMN_MAP["gender2_unknown_senior_staff"]] if xl_row[COLUMN_MAP["gender2_unknown_senior_staff"]]  != None else 0,
                "declined": xl_row[COLUMN_MAP["gender_decline_to_state_senior_staff"]] if xl_row[COLUMN_MAP["gender_decline_to_state_senior_staff"]] !=None else 0
                                   + xl_row[COLUMN_MAP["gender2_decline_to_state_senior_staff"]] if xl_row[COLUMN_MAP["gender2_decline_to_state_senior_staff"]] !=None else 0},

                "senior_staff_orientation":{"straight": xl_row[COLUMN_MAP["straight_senior_staff"]],
                                    "lgbtqia": xl_row[COLUMN_MAP["lgbtqia_senior_staff"]],
                                    "unknown": xl_row[COLUMN_MAP["orientation_unknown_senior_staff"]],
                                    "declined": xl_row[COLUMN_MAP["orientation_decline_to_state_senior_staff"]] },
                
                "senior_staff_disability":{"with_disability": xl_row[COLUMN_MAP["with_disability_senior_staff"]],
                                    "without_disability": xl_row[COLUMN_MAP["without_disability_senior_staff"]],
                                    "unknown": xl_row[COLUMN_MAP["disability_unknown_senior_staff"]],
                                    "declined": xl_row[COLUMN_MAP["disability_decline_to_state_senior_staff"]]} ,

                "total_staff_members": xl_row[COLUMN_MAP["total_staff"]],

                "staff_race":{"asian": xl_row[COLUMN_MAP["asian_staff"]],
                            "black": xl_row[COLUMN_MAP["black_staff"]],
                            "hispanic": xl_row[COLUMN_MAP["hispanic_staff"]],
                            "middle_eastern": xl_row[COLUMN_MAP["middle_eastern_staff"]],
                            "multi_racial": xl_row[COLUMN_MAP["multi_racial_staff"]],
                            "native_american": xl_row[COLUMN_MAP["native_american_staff"]],
                            "pacific_islander": xl_row[COLUMN_MAP["pacific_islander_staff"]],
                            "white": xl_row[COLUMN_MAP["white_staff"]],
                            "other": xl_row[COLUMN_MAP["other_ethnicity_staff"]],
                            "unknown": xl_row[COLUMN_MAP["race_unknown_staff"]],
                            "declined": xl_row[COLUMN_MAP["race_decline_to_state_staff"]]},

                "staff_gender":{"female": xl_row[COLUMN_MAP["female_staff"]],
                                 "male": xl_row[COLUMN_MAP["male_staff"]],
                                 "transgender": xl_row[COLUMN_MAP["trans_staff"]],
                                 "cis": xl_row[COLUMN_MAP["cis_staff"]],
                                 "non_binary": xl_row[COLUMN_MAP["non_binary_staff"]],
                                 "unknown": xl_row[COLUMN_MAP["gender_unknown_staff"]] if xl_row[COLUMN_MAP["gender_unknown_staff"]] != None else 0 + 
                            xl_row[COLUMN_MAP["gender2_unknown_staff"]] if xl_row[COLUMN_MAP["gender2_unknown_staff"]]  != None else 0,
                "declined": xl_row[COLUMN_MAP["gender_decline_to_state_staff"]] if xl_row[COLUMN_MAP["gender_decline_to_state_staff"]] !=None else 0
                                   + xl_row[COLUMN_MAP["gender2_decline_to_state_staff"]] if xl_row[COLUMN_MAP["gender2_decline_to_state_staff"]] !=None else 0},

                "staff_orientation":{"straight": xl_row[COLUMN_MAP["straight_staff"]],
                                    "lgbtqia": xl_row[COLUMN_MAP["lgbtqia_staff"]],
                                    "unknown": xl_row[COLUMN_MAP["orientation_unknown_staff"]],
                                    "declined": xl_row[COLUMN_MAP["orientation_decline_to_state_staff"]] },
                
                "staff_disability":{"with_disability": xl_row[COLUMN_MAP["with_disability_staff"]],
                                    "without_disability": xl_row[COLUMN_MAP["without_disability_staff"]],
                                    "unknown": xl_row[COLUMN_MAP["disability_unknown_staff"]],
                                    "declined": xl_row[COLUMN_MAP["disability_decline_to_state_staff"]]}            
    }
    return csv_json

