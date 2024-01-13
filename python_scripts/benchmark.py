import pandas as pd


top_990 = pd.read_csv("990-Top-12-6.csv")
candid_top = pd.read_csv("Candid-Top-12-6.csv")
candid_top_percentages = pd.read_csv("Candid-Top-12-6-Percentages.csv")

merged_df = pd.merge(
    top_990, candid_top, on="ein", how="outer", suffixes=("_990", "_candid")
)

for column in top_990.columns:
    if column in candid_top.columns and column != "ein":
        merged_df[column] = merged_df[column + "_candid"].combine_first(
            merged_df[column + "_990"]
        )

        merged_df.drop([column + "_990", column + "_candid"], axis=1, inplace=True)

benchmarkable_stats = [
    "total_revenue",
    "percent_male",
    "percent_female",
    "avg_employee_comp",
    "HighestCompensatedEmployeeInd_percent_female",
    "IndividualTrusteeOrDirectorInd_percent_female",
    "OfficerInd_percent_female",
    "KeyEmployeeInd_percent_female",
    "FormerOfcrDirectorTrusteeInd_percent_female",
]

percentage_columns = [
    "asian_senior_staff",
    "black_senior_staff",
    "hispanic_senior_staff",
    "middle_eastern_senior_staff",
    "native_american_senior_staff",
    "pacific_islander_senior_staff",
    "white_senior_staff",
    "multi_racial_senior_staff",
    "other_ethnicity_senior_staff",
    "race_decline_to_state_senior_staff",
    "race_unknown_senior_staff",
    "female_senior_staff",
    "male_senior_staff",
    "non_binary_senior_staff",
    "gender_decline_to_state_senior_staff",
    "gender_unknown_senior_staff",
    "trans_senior_staff",
    "cis_senior_staff",
    "female_board",
    "male_board",
    "non_binary_board",
    "gender_decline_to_state_board",
    "gender_unknown_board",
    "trans_board",
    "cis_board",
    "asian_board",
    "black_board",
    "hispanic_board",
    "middle_eastern_board",
    "native_american_board",
    "pacific_islander_board",
    "white_board",
    "multi_racial_board",
    "other_ethnicity_board",
    "asian_staff",
    "black_staff",
    "hispanic_staff",
    "middle_eastern_staff",
    "native_american_staff",
    "pacific_islander_staff",
    "white_staff",
    "multi_racial_staff",
    "other_ethnicity_staff",
    "race_decline_to_state_staff",
    "race_unknown_staff",
    "female_staff",
    "male_staff",
    "non_binary_staff",
    "gender_decline_to_state_staff",
    "gender_unknown_staff",
    "trans_staff",
    "cis_staff",
]


averages = merged_df[benchmarkable_stats].mean()

averages_df = averages.to_frame(name="Average")
averages_df.to_csv("benchmark_averages.csv")

candid_averages = candid_top_percentages[percentage_columns].mean()

candid_averages.to_csv("candid_benchmark_averages.csv")
