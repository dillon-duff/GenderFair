import firebase_admin
from firebase_admin import credentials, firestore
import math
from multiprocess.pool import Pool
import os

cred = credentials.Certificate("gender-fair-82d21-firebase-adminsdk-xzaw3-9b1027afcf.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

class ScoreCalculator:

    def calculate_scores(self, company_data):
        if not company_data or "metrics" not in company_data:
            return None

        metrics = company_data["metrics"]

        scores = {
            "Trustees": self.trustees(
                metrics["IndividualTrusteeOrDirectorInd_percent_female"]
            ),
            "Highest Compensated": self.highest_comp(
                metrics["HighestCompensatedEmployeeInd_percent_female"]
            ),
            "Officers": self.officers(metrics["OfficerInd_percent_female"]),
            "Pay Gap": self.pay_gap(metrics["pay_gap"]),
            "Average Salary": self.avg_salary(metrics["avg_employee_comp"]),
            "CEO Pay Ratio": self.pay_ratio(
                metrics["highest_salary"], metrics["avg_employee_comp"]
            ),
            "Candid Reporting": self.has_populated_fields(company_data),
            "Diversity Reporting": self.white_staff(company_data),
        }

        final_score = self.aggregate_scores(scores)
        return {
            "Name": company_data["name"],
            "final_score": final_score,
            "individual_scores": scores,
            "Company Data": company_data,
        }

    def white_staff(self, json_data):
        staff_race = json_data.get("staff_race", {})

        # Calculate the total number of staff
        total_staff = sum(
            float(value) for key, value in staff_race.items() if value not in ["", None]
        )

        # Return 0 if there are no staff details
        if total_staff == 0:
            return 0

        # Get the number of white staff
        if staff_race.get("white", 0) == "":
            return 0
        white_staff = float(staff_race.get("white", 0))

        # Calculate the percentage of white staff
        percentage_white = (white_staff / total_staff) * 100

        if percentage_white <= 61:
            return 8
        else:
            return round(8 - 8 * ((percentage_white - 61) / 39))

    def has_populated_fields(self, json_data):
        fields_to_check = [
            "staff_race",
            "staff_gender",
            "senior_staff_race",
            "senior_staff_gender",
            "board_race",
            "board_gender",
        ]

        for field in fields_to_check:
            if field in json_data:
                if any(
                    value
                    for value in json_data[field].values()
                    if value not in ["", None]
                ):
                    return 8

        return 0

    def trustees(self, ratio):
        if ratio:

            percent_women = float(ratio)

            if percent_women >= 50:
                return 17
            elif percent_women < 0:
                return 0
            else:
                return round((percent_women / 50) * 17)

        else:
            return 0

    def highest_comp(self, ratio):
        if ratio:

            percent_women = float(ratio)

            if percent_women >= 50:
                return 17
            elif percent_women < 0:
                return 0
            else:
                return round((percent_women / 50) * 17)

        else:
            return 0

    def officers(self, ratio):
        if ratio:

            percent_women = float(ratio)

            if percent_women >= 50:
                return 17
            elif percent_women < 0:
                return 0
            else:
                return round((percent_women / 50) * 17)

        else:
            return 0

    def pay_gap(self, ratio):
        if ratio:
            ratio = float(ratio)

            p_gap = max(-100, min(100, ratio))

            if p_gap <= 0:
                # For pay gap from -100 to 0, score decreases from 17 to 12
                score = 12 + (abs(p_gap) / 100) * 5
            else:
                # For pay gap from 0 to 100, score decreases from 12 to 0
                score = 12 - (p_gap / 100) * 12

            return round(score)

        else:
            return 0

    def avg_salary(self, ratio):
        if ratio:
            ratio = float(ratio)
            if ratio > 84320:
                return 8

            elif ratio > 64639:
                return 6

            elif ratio > 47331:
                return 4

            elif ratio > 34584:
                return 3

            elif ratio > 20164:
                return 2

            else:
                return 0

        return 0

    def pay_ratio(self, ratio, ratio1):
        if ratio:

            if ratio == "" or ratio1 == "" or float(ratio1) == 0:
                return 0  # YOU NEED TO CHECK WHY THIS HAPPENS
            ratio = float(ratio) / float(ratio1)
            if ratio < 4.37:
                return 8

            elif ratio < 6.01:
                return 6

            elif ratio < 8.28:
                return 4

            elif ratio < 13.44:
                return 3

            elif ratio < 20.17:
                return 2

            else:
                return 0

        else:
            return 0

    def aggregate_scores(self, scores):
        total_score = sum(scores.values())
        return total_score





def calculate_scores(doc_id):
    company_data = clean_nan_values(db.collection("non-for-profits").document(doc_id).get().to_dict())

    score_calculator = ScoreCalculator()
    scores = score_calculator.calculate_scores(company_data)
    
    return scores


def clean_nan_values(data, replace_with=""):
    if isinstance(data, dict):
        return {k: clean_nan_values(v, replace_with) for k, v in data.items()}
    elif isinstance(data, list):
        return [clean_nan_values(v, replace_with) for v in data]
    elif isinstance(data, float) and math.isnan(data):
        return replace_with
    else:
        return data


def get_document_ids():
    collection_ref = db.collection("non-for-profits")
    docs = collection_ref.stream()

    doc_ids = [doc.id for doc in docs]
    return doc_ids


def get_documents_with_scores():
    collection_ref = db.collection("non-for-profits")
    docs = collection_ref.stream()
    return [{'id': doc.id, **doc.to_dict()} for doc in docs]


def handle_doc_id(doc_id):
    result = calculate_scores(doc_id)
    scores = result['individual_scores']

    scores_cleaned = {"CEO_pay_ratio_score": scores['CEO Pay Ratio'],
                        "Candid_Reporting_score": scores['Candid Reporting'],
                        "average_salary_score": scores["Average Salary"],
                        "diversity_reporting_score": scores['Diversity Reporting'],
                        "highest_compensated_score": scores['Highest Compensated'],
                        "officers_score": scores['Officers'],
                        "pay_gap_score": scores['Pay Gap'],
                        "trustees_score": scores['Trustees'],
                        "final_score": sum(scores.values())
                        }

    update_doc(doc_id, scores_cleaned)


def rerank_docs():
    documents = get_documents_with_scores()
    
    sorted_documents = sorted(documents, key=lambda x: x['final_score'], reverse=True)
    
    for rank, doc in enumerate(sorted_documents, start=1):
        doc['rank'] = rank

    with Pool(os.cpu_count() - 2) as pool:
        pool.map(update_document_rank, sorted_documents)


def update_doc(doc_id, scores):
    db.collection("non-for-profits").document(doc_id).update(scores)


def update_document_rank(doc):
    doc_ref = db.collection("non-for-profits").document(doc['id'])
    doc_ref.update({'rank': doc['rank']})


if __name__ == "__main__":
    doc_ids = get_document_ids()
    with Pool(os.cpu_count() - 2) as pool:
        pool.map(handle_doc_id, doc_ids)
    rerank_docs()