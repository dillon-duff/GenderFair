import pandas as pd


def calculate_percentages(input_file, output_file, control_column_pairs):
    # Read the Excel file into a pandas DataFrame
    df = pd.read_csv(input_file)

    for pair in control_column_pairs:
        control_column = pair['control_column']
        columns_to_process = pair['columns']

        # Check if the control column is present in the DataFrame
        if control_column not in df.columns:
            print(
                f"Control column '{control_column}' not found in the Excel sheet. Skipping.")
            continue

        # Filter out columns that do not exist in the DataFrame
        valid_columns = [
            col for col in columns_to_process if col in df.columns]

        # Check if any valid columns are found
        if not valid_columns:
            print(
                f"No valid columns found for control column '{control_column}'. Skipping.")
            continue

        # Calculate the percentage for each valid column
        for col in valid_columns:
            df[col] = (df[col] / df[control_column]) * 100

    # Save the modified DataFrame to a new Excel file
    df.to_excel(output_file, index=False)
    print(f"Percentage calculation completed. Results saved to {output_file}")


# Example usage:
# Replace with your input Excel file
input_file = 'Candid-Demographics-Top-60000.csv'
# Replace with your desired output Excel file
output_file = 'PercentageCalculated.xlsx'

# Define multiple pairs of control columns and associated columns
control_column_pairs = [
    {'control_column': 'total_senior_staff', 'columns': ['asian_senior_staff', 'black_senior_staff', 'hispanic_senior_staff', 'middle_eastern_senior_staff', 'native_american_senior_staff', 'pacific_islander_senior_staff', 'white_senior_staff', 'multi_racial_senior_staff',
                                                         'other_ethnicity_senior_staff', 'race_decline_to_state_senior_staff', 'race_unknown_senior_staff', 'female_senior_staff', 'male_senior_staff', 'non_binary_senior_staff', 'gender_decline_to_state_senior_staff', 'gender_unknown_senior_staff', 'trans_senior_staff', 'cis_senior_staff']},
    {'control_column': 'total_board', 'columns': ['female_board', 'male_board', 'non_binary_board', 'gender_decline_to_state_board', 'gender_unknown_board', 'trans_board', 'cis_board',
                                                  'asian_board', 'black_board', 'hispanic_board', 'middle_eastern_board', 'native_american_board', 'pacific_islander_board', 'white_board', 'multi_racial_board', 'other_ethnicity_board']},
    {'control_column': 'total_staff', 'columns': ['asian_staff', 'black_staff', 'hispanic_staff', 'middle_eastern_staff', 'native_american_staff', 'pacific_islander_staff', 'white_staff', 'multi_racial_staff',
                                                  'other_ethnicity_staff', 'race_decline_to_state_staff', 'race_unknown_staff', 'female_staff', 'male_staff', 'non_binary_staff', 'gender_decline_to_state_staff', 'gender_unknown_staff', 'trans_staff', 'cis_staff']}
]

calculate_percentages(input_file, output_file, control_column_pairs)
