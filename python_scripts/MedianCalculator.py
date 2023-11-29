import pandas as pd

def calculate_median(input_file, cutoff_value, sorting_column, columns_to_calculate):
    # Read the Excel file into a pandas DataFrame
    df = pd.read_excel(input_file)

    # Sort the DataFrame by the specified sorting column
    df.sort_values(by=sorting_column, inplace=True)

    # Filter rows where the sorting column value is higher than the cutoff value
    subset_df = df[df[sorting_column] > cutoff_value]

    # Calculate the median for each specified column in the subset
    median_values = {}
    for col in columns_to_calculate:
        median_values[col] = subset_df[col].median()

    return median_values

# Example usage:
input_file = 'PercentageCalculated.xlsx'  # Replace with your input Excel file
cutoff_value = 50  # Replace with your desired cutoff value
sorting_column = 'total_staff'  # Replace with your sorting column name
columns_to_calculate = ['asian_staff','black_staff','hispanic_staff','middle_eastern_staff','native_american_staff','pacific_islander_staff','white_staff','multi_racial_staff','other_ethnicity_staff','race_decline_to_state_staff','race_unknown_staff','female_staff','male_staff','non_binary_staff','gender_decline_to_state_staff','gender_unknown_staff','trans_staff','cis_staff','female_board', 'male_board', 'non_binary_board', 'gender_decline_to_state_board', 'gender_unknown_board', 'trans_board', 'cis_board', 'asian_board', 'black_board', 'hispanic_board', 'middle_eastern_board', 'native_american_board', 'pacific_islander_board', 'white_board', 'multi_racial_board', 'other_ethnicity_board','black_senior_staff','asian_senior_staff', 'black_senior_staff', 'hispanic_senior_staff', 'middle_eastern_senior_staff', 'native_american_senior_staff', 'pacific_islander_senior_staff', 'white_senior_staff', 'multi_racial_senior_staff', 'other_ethnicity_senior_staff', 'race_decline_to_state_senior_staff', 'race_unknown_senior_staff','female_senior_staff','male_senior_staff','non_binary_senior_staff','gender_decline_to_state_senior_staff','gender_unknown_senior_staff','trans_senior_staff','cis_senior_staff']  # Replace with your list of columns

result = calculate_median(input_file, cutoff_value, sorting_column, columns_to_calculate)

print("Median values:")
for col, median in result.items():
    print(f"{col}: {median}")
