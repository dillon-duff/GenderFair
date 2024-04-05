import numpy as np
import firebase_admin
from firebase_admin import credentials, firestore
class ScoreCalculator:

    # def avgOffset(self,ratio):
    #     return abs(50 - ratio)

    def calculate_scores(self, company_data, percentiles):

        if not company_data or 'metrics' not in company_data:
            return None

        metrics = company_data['metrics']


        scores = {

            "trustees_Sscore": self.trustees(metrics['IndividualTrusteeOrDirectorInd_percent_female'],percentiles),
            "highest_compensated_score": self.highest_comp(metrics['HighestCompensatedEmployeeInd_percent_female'],percentiles),
            "officers_score": self.officers(metrics['OfficerInd_percent_female'],percentiles),
            "pay_gap_score": self.pay_gap(metrics['pay_gap'],percentiles),
            "average_salary_score": self.avg_salary(metrics['salary_revenue_ratio'],percentiles),
            "CEO_pay_ratio_score": self.pay_ratio(metrics['CEO_pay_ratio'],percentiles),
            "Candid_Reporting_score": self.has_populated_fields(company_data,percentiles),
            "diversity_reporting_score": self.white_staff(company_data,percentiles)


        }

        scores['final_score'] = self.aggregate_scores(scores)
        return scores

    def white_staff(self,json_data,percentiles):
        staff_race = json_data.get("staff_race", {})

        # Calculate the total number of staff
        total_staff = sum(float(value) for key, value in staff_race.items() if value not in ["", None])

        # Return 0 if there are no staff details
        if total_staff == 0:
            return 0

        # Get the number of white staff
        if staff_race.get("white",0) == '':
            return 0 #LOOK INTO THIS ASWELL
        white_staff = float(staff_race.get("white", 0))

        # Calculate the percentage of white staff
        percentage_white = (white_staff / total_staff) * 100

        if percentage_white <= 61: #average amount for nonprofits
            return 5
        else: return 0 #Maybe change it so do we sum POC instead of do it this way

    def has_populated_fields(self,json_data,percentiles):
        fields_to_check = [
            "staff_race", "staff_gender", "senior_staff_race", "senior_staff_gender", "board_race", "board_gender"
        ]

        for field in fields_to_check:
            if field in json_data:
                # If any subfield has a non-empty, non-zero value, return True immediately
                if any(value for value in json_data[field].values() if value not in ["", None]):
                    return 5

        # If no populated fields are found, return False
        return 0
    def trustees(self, ratio,percentiles):
        # Logic for score 1
        if ratio:  # placeholder

            ratio = float(ratio)


            # if ratio == self.avgOffset(50):
            #     return 10

            if ratio > 50:
                return 10
            elif ratio > 45:
                return 8

            elif ratio > 40:
                return 6

            elif ratio > percentiles['IndividualTrusteeOrDirectorInd_percent_female'][40]:
                return 4

            elif ratio > percentiles['IndividualTrusteeOrDirectorInd_percent_female'][20]:
                return 2

            else:
                return 0


        else: return 0


    def highest_comp(self, ratio,percentiles):
        # Logic for score 1
        if ratio:  # placeholder

            ratio = float(ratio)

            if ratio > 50:
                return 10
            elif ratio > 46:
                return 8

            elif ratio > 42:
                return 6

            elif ratio > percentiles['HighestCompensatedEmployeeInd_percent_female'][40]:
                return 4

            elif ratio > percentiles['HighestCompensatedEmployeeInd_percent_female'][20]:
                return 2

            else:
                return 0


        else: return 0

        # ... Implement other scoring methods here

    def officers(self,ratio,percentiles):
        if ratio:  # placeholder
            ratio = float(ratio)


            # if ratio == self.avgOffset(50):
            #     return 10

            if ratio > 50:
                return 10
            elif ratio > 42:
                return 8

            elif ratio > 34:
                return 6

            elif ratio > percentiles['OfficerInd_percent_female'][40]:
                return 4

            elif ratio > percentiles['OfficerInd_percent_female'][20]:
                return 2

            else:
                return 0


        else: return 0

    def pay_gap(self,ratio,percentiles):
        if ratio:  # placeholder
            ratio = float(ratio)
            if ratio > 99:
                return 0

            elif ratio > 70:
                return 2

            elif ratio > percentiles['pay_gap'][60]:
                return 4

            elif ratio > percentiles['pay_gap'][40]:
                return 6

            elif ratio > percentiles['pay_gap'][20]:
                return 8

            else:
                return 10


        else: return 0


    def avg_salary(self,ratio,percentiles):
        if ratio:  # placeholder
            ratio = float(ratio)
            if ratio > percentiles['salary_revenue_ratio'][90]:
                return 5

            elif ratio > percentiles['salary_revenue_ratio'][80]:
                return 4

            elif ratio > percentiles['salary_revenue_ratio'][60]:
                return 3

            elif ratio > percentiles['salary_revenue_ratio'][40]:
                return 2

            elif ratio > percentiles['salary_revenue_ratio'][20]:
                return 1

            else:
                return 0


        else: return 0

    def pay_ratio(self,ratio,percentiles):
        if ratio:  # placeholder#COME BACK AND REVISE

            # if ratio =='' or ratio1 =='' or float(ratio1) == 0:
            #     return 0 #YOU NEED TO CHECK WHY THIS HAPPENS
            ratio = float(ratio)
            if ratio < percentiles['CEO_pay_ratio'][20]:
                return 5

            elif ratio < percentiles['CEO_pay_ratio'][40]:
                return 4

            elif ratio < percentiles['CEO_pay_ratio'][60]:
                return 3

            elif ratio < percentiles['CEO_pay_ratio'][80]:
                return 2

            elif ratio < percentiles['CEO_pay_ratio'][90]:
                return 1

            else:
                return 0


        else: return 0



    def aggregate_scores(self, scores):
        total_score = sum(scores.values())
        # normalized_score = (total_score / 13) * (100 / 10)
        return total_score



# Initialize Firebase Admin SDK
cred = credentials.Certificate('gender-fair-82d21-firebase-adminsdk-xzaw3-9e24d547ea.json')  # Update the path with your JSON file
firebase_admin.initialize_app(cred)

# Access Firestore
db = firestore.client()

# Specify the collection
collection_ref = db.collection('non-for-profits')  # Update with your collection name

# Retrieve documents from the collection
docs = collection_ref.stream()

# Convert documents to a list of tuples (doc_id, doc_dict)
docs_list = [(doc.id, doc.to_dict()) for doc in docs]

for doc_id, doc_data in docs_list:
    # Retrieve 'average_salary' and 'total_revenue', defaulting to 0 if they are not present
    skip_revenue = 0
    skip_salary = 0

    try:
        average_salary = float(doc_data['metrics']['avg_employee_comp'])
    except ValueError:
        doc_data['metrics']['salary_revenue_ratio'] = 0
        doc_data['metrics']['CEO_pay_ratio'] = 0
        continue
    try:
        total_revenue = float(doc_data['metrics']['total_revenue'])
    except ValueError:
        doc_data['metrics']['salary_revenue_ratio'] = 0
        skip_revenue = 1

    try:
        highest_salary = float(doc_data['metrics']['highest_salary'])
    except ValueError:
        doc_data['metrics']['CEO_pay_ratio'] = 0
        skip_salary =1
        # Ensure that 'total_revenue' is not zero to avoid division by zero error
    if skip_revenue != 1:
        if total_revenue != 0:
            salary_to_revenue_ratio = average_salary / total_revenue
            doc_data['metrics']['salary_revenue_ratio'] = salary_to_revenue_ratio
        else:
            # Handle the case where 'total_revenue' is zero, to avoid division by zero
            # You might want to set the ratio to None or some other indicative value
            doc_data['metrics']['salary_revenue_ratio'] = 0  # or 0, or any other value you deem appropriate

    if skip_salary != 1:
        if highest_salary != 0 and average_salary != 0:
            doc_data['metrics']['CEO_pay_ratio'] = highest_salary / average_salary
        elif highest_salary == 0 and average_salary == 0:
            doc_data['metrics']['CEO_pay_ratio'] = 8
        else:
            doc_data['metrics']['CEO_pay_ratio'] = 100



fields = [
    'average_female_salary', 'average_male_salary', 'pay_gap',
    'percent_male', 'percent_female', 'avg_employee_comp',
    'highest_salary', 'total_compensation', 'num_employees',
    'total_revenue', 'HighestCompensatedEmployeeInd_percent_female',
    'IndividualTrusteeOrDirectorInd_percent_female',
    'OfficerInd_percent_female', 'KeyEmployeeInd_percent_female',
    'FormerOfcrDirectorTrusteeInd_percent_female','salary_revenue_ratio','CEO_pay_ratio'
    ]  # Replace with your actual field names
percentiles = [20, 40, 60, 80, 90]
percentile_data = {}


# Calculate and print percentiles for each field
for field in fields:
    print(field)
    # Extract the values for the field from all documents, ensuring values are not None
    values = [
        float(doc[1]['metrics'][field]) for doc in docs_list if field in doc[1]['metrics'] and doc[1]['metrics'][field] is not None and doc[1]['metrics'][field]!='']

    if not values:  # Check if the 'values' list is empty
        print(f"No data available for field '{field}'. Skipping percentile calculation.")
        continue  # Skip the rest of the loop and move to the next field

    # Calculate percentiles since 'values' is not empty
    percentile_values = np.percentile(values, percentiles)
    percentile_data[field] = {percentile: value for percentile, value in zip(percentiles, percentile_values)}

    # Print the results
    # print(f"Percentiles for {field}:")
    # for percentile, value in zip(percentiles, percentile_values):
    #     print(f"  {percentile}th percentile: {value}")

print(percentile_data)

score_calculator = ScoreCalculator()
for doc_id, doc_data in docs_list:
    new_scores = score_calculator.calculate_scores(doc_data,percentile_data)

    for key, value in new_scores.items():
        doc_data[key] = value


# Sort the list based on your ranking criteria, e.g., a 'score' field
# Change 'score' to your actual field name and sorting logic as needed
sorted_docs = sorted(docs_list, key=lambda x: x[1]['final_score'], reverse=True)

# Assign ranks and update documents
for rank, (doc_id, doc_dict) in enumerate(sorted_docs, start=1):
    # Update the document with its rank
    # collection_ref.document(doc_id).update({'rank': rank})
    doc_dict['rank'] = rank
    # if rank ==1:
    collection_ref.document(doc_id).update(doc_dict)
        # print(f"Updated doc {doc_id} with rank {rank}, data {doc_dict}")



