import pandas as pd

def calculate_percentages(input_file, output_file, control_column_pairs):
    # Read the Excel file into a pandas DataFrame
    df = pd.read_excel(input_file)

    for pair in control_column_pairs:
        control_column = pair['control_column']
        columns_to_process = pair['columns']

        # Check if the control column is present in the DataFrame
        if control_column not in df.columns:
            print(f"Control column '{control_column}' not found in the Excel sheet. Skipping.")
            continue

        # Filter out columns that do not exist in the DataFrame
        valid_columns = [col for col in columns_to_process if col in df.columns]

        # Check if any valid columns are found
        if not valid_columns:
            print(f"No valid columns found for control column '{control_column}'. Skipping.")
            continue

        # Calculate the percentage for each valid column
        for col in valid_columns:
            df[col] = (df[col] / df[control_column]) * 100

    # Save the modified DataFrame to a new Excel file
    df.to_excel(output_file, index=False)
    print(f"Percentage calculation completed. Results saved to {output_file}")

# Example usage:
input_file = 'PercentageCalculated.xlsx'  # Replace with your input Excel file
output_file = 'PercentageCalculated1.xlsx'  # Replace with your desired output Excel file

# Define multiple pairs of control columns and associated columns
control_column_pairs = [
    {'control_column': 'total_senior_staff', 'columns': ['black_senior_staff']}

]

calculate_percentages(input_file, output_file, control_column_pairs)
