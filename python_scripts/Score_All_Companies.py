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
        writer.writerow(['Company Name', 'Score'])

        for company in all_companies:
            scores = score_calculator.calculate_scores(company)
            # Write the company name and its score
            writer.writerow([company['name'], scores["final_score"]])

        print("Scores have been written to company_scores.csv")

if __name__ == "__main__":
    main()