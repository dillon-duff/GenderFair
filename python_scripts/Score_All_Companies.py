from python_scripts.database_new import DatabaseManager
from python_scripts.score_calculator import ScoreCalculator
import csv
def main():
    db_manager = DatabaseManager()
    score_calculator = ScoreCalculator()

    all_companies = db_manager.get_all_companies()

    # Open a CSV file to write
    with open('company_scores.csv', mode='w', newline='') as file:
        writer = csv.writer(file)
        # Write the header
        writer.writerow(['Company Name', 'Score','Avg Salary', 'CEO Pay Ratio','Candid Reporting','Diversity Reporting', 'Highest Comp','Officers','Pay Gap','Trustees'])

        for company in all_companies:
            scores = score_calculator.calculate_scores(company)
            # Write the company name and its score
            writer.writerow([company['name'], scores["final_score"],scores["individual_scores"]["Average Salary"],scores["individual_scores"]["CEO Pay Ratio"],scores["individual_scores"]["Candid Reporting"],scores["individual_scores"]["Diversity Reporting"],scores["individual_scores"]["Highest Compensated"],scores["individual_scores"]["Officers"],scores["individual_scores"]["Pay Gap"],scores["individual_scores"]["Trustees"]])

        print("Scores have been written to company_scores.csv")

if __name__ == "__main__":
    main()