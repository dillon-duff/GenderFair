import pandas as pd
import numpy as np
pd.set_option('display.max_columns', None)
def calculate_percentage(input_file, output_file, columns, control_column, output_text_file):
    # Read the Excel file into a pandas DataFrame
    df = pd.read_excel(input_file)

    # Check data types
    with open(output_text_file, 'a') as f:
        print("Data Types:", file=f)
        print(df.dtypes, file=f)

    # Check for NaN and zero values in the control column
    with open(output_text_file, 'a') as f:
        print("NaN and Zero Values in Control Column:", file=f)
        print(df[control_column].isna().sum(), file=f)
        print((df[control_column] == 0).sum(), file=f)

    # Print data before calculation
    with open(output_text_file, 'a') as f:
        print("Data Before Calculation:", file=f)
        print(df[columns + [control_column]], file=f)

    # Filter out rows with zero or NaN values in the control column
    df = df[df[control_column] != 0]
    df = df.dropna(subset=[control_column])

    # Check if all specified columns are present in the DataFrame
    missing_columns = [col for col in columns if col not in df.columns]
    if missing_columns:
        with open(output_text_file, 'a') as f:
            print(f"Columns {missing_columns} not found in the Excel sheet.", file=f)
        return

    # Calculate the percentage for each specified column
    for col in columns:
        # Avoid division by zero or NaN
        df[col] = (df[col] / df[control_column]) * 100

    # Handle NaN and infinite values by replacing them with 0
    df = df.replace([np.inf, -np.inf, np.nan], 0)

    # Print data after calculation
    with open(output_text_file, 'a') as f:
        print("Data After Calculation:", file=f)
        print(df[columns + [control_column]], file=f)

    # Save the modified DataFrame to a new Excel file
    df.to_excel(output_file, index=False)
    print(f"Percentage calculation completed. Results saved to {output_file}")

# Example usage:
input_file = 'PercentageCalculated.xlsx'  # Replace with your input Excel file
output_file = 'PercentageCalculated2.xlsx'  # Replace with your desired output Excel file
columns_to_process = ['black_senior_staff']  # Replace with your column names
control_column_name = 'total_senior_staff'  # Replace with your control column name
output_text_file = 'output_text.txt'  # Replace with your desired output text file

calculate_percentage(input_file, output_file, columns_to_process, control_column_name, output_text_file)
