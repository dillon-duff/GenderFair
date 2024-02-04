from flask import Flask, jsonify, request

from python_scripts.database_new import DatabaseManager


app = Flask(__name__)

class ScoreCalculator:
    def calculate_scores(self, company_data):
        if not company_data or 'metrics' not in company_data:
            return None

        metrics = company_data['metrics']


        scores = {

            "Trustees": self.trustees(metrics['IndividualTrusteeOrDirectorInd_percent_female']),
            "Highest Compensated": self.highest_comp(metrics['HighestCompensatedEmployeeInd_percent_female']),
            "Officers": self.officers(metrics['OfficerInd_percent_female']),
            "Pay Gap": self.pay_gap(metrics['pay_gap']),
            "Average Salary" : self.avg_salary(metrics['avg_employee_comp']),
            "CEO Pay Ratio": self.pay_ratio(metrics['highest_salary'],metrics['avg_employee_comp']),
            "Candid Reporting": self.has_populated_fields(company_data),
            "Diversity Reporting": self.white_staff(company_data)


        }

        final_score = self.aggregate_scores(scores)
        return { "Name" : company_data['name'], "final_score": final_score, "individual_scores": scores}

    def white_staff(self,json_data):
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

        if percentage_white < 50:
            return 5
        elif percentage_white < 71:
            return 3
        else: return 0
    def has_populated_fields(self,json_data):
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
    def trustees(self, ratio):
        # Logic for score 1
        if ratio:  # placeholder
            ratio = float(ratio)
            if ratio > 99:
                return 10

            elif ratio > 60:
                return 8

            elif ratio > 45:
                return 6

            elif ratio > 33:
                return 4

            elif ratio > 20:
                return 2

            else:
                return 0


        else: return 0


    def highest_comp(self, ratio):
        # Logic for score 1
        if ratio:  # placeholder
            ratio = float(ratio)
            if ratio > 99:
                return 10

            elif ratio > 75:
                return 8

            elif ratio > 40:
                return 6

            elif ratio > 20:
                return 4

            elif ratio > 0:
                return 2

            else:
                return 0


        else: return 0

            # ... Implement other scoring methods here

    def officers(self,ratio):
        if ratio:  # placeholder
            ratio = float(ratio)
            if ratio > 99:
                return 10

            elif ratio > 60:
                return 8

            elif ratio > 50:
                 return 6

            elif ratio > 33:
                return 4

            elif ratio > 20:
                 return 2

            else:
                 return 0


        else: return 0


    def pay_gap(self,ratio):
        if ratio:  # placeholder
            ratio = float(ratio)
            if ratio > 99:
                return 0

            elif ratio > 90:
                return 2

            elif ratio > 28.83:
                return 4

            elif ratio > 3.6:
                return 6

            elif ratio > -1.0:
                return 8

            else:
                return 10


        else: return 0


    def avg_salary(self,ratio):
        if ratio:  # placeholder
            ratio = float(ratio)
            if ratio > 181781:
                return 5

            elif ratio > 64639:
                return 4

            elif ratio > 47331:
                return 3

            elif ratio > 34584:
                return 2

            elif ratio > 20164:
                return 1

            else:
                return 0


        else: return 0

    def pay_ratio(self,ratio, ratio1):
        if ratio:  # placeholder
            if ratio =='' or ratio1 =='':
                return 0 #YOU NEED TO CHECK WHY THIS HAPPENS
            ratio = float(ratio) / float(ratio1)
            if ratio < 4.37:
                return 5

            elif ratio < 6.01:
                return 4

            elif ratio < 8.28:
                return 3

            elif ratio < 13.44:
                return 2

            elif ratio < 20.17:
                return 1

            else:
                return 0


        else: return 0



    def aggregate_scores(self, scores):
        total_score = sum(scores.values())
        # normalized_score = (total_score / 13) * (100 / 10)
        return total_score
@app.route('/calculate_scores', methods=['GET'])
def calculate_scores():
    eid = request.args.get('eid')
    if not eid:
        return jsonify({"error": "Company eid is required"}), 400

    db_manager = DatabaseManager()
    company_data = db_manager.get_company_by_eid(eid)

    # If multiple companies are found, consider the first one, or implement a logic to choose
#    company_data = company_data[0] if company_data else None



    score_calculator = ScoreCalculator()
    scores = score_calculator.calculate_scores(company_data)

    if scores is not None:
        return jsonify(scores)
    else:
        return jsonify({"error": "Company not found or invalid data"}), 404
if __name__ == '__main__':
    app.run()