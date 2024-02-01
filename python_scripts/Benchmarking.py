import pandas as pd

# Path to your CSV file
file_path = '990-Top-1-18.csv'

# Load the CSV file
try:
    data = pd.read_csv(file_path)
except Exception as e:
    print(f"Error loading the file: {e}")
    # Exit if the file cannot be loaded
    exit()

# List of columns to calculate percentiles for
columns_to_analyze = [
    'average_female_salary', 'average_male_salary', 'pay_gap',
    'percent_male', 'percent_female', 'avg_employee_comp',
    'highest_salary', 'total_compensation', 'num_employees',
    'total_revenue', 'HighestCompensatedEmployeeInd_percent_female',
    'IndividualTrusteeOrDirectorInd_percent_female',
    'OfficerInd_percent_female', 'KeyEmployeeInd_percent_female',
    'FormerOfcrDirectorTrusteeInd_percent_female'
]

# Percentiles to calculate
percentiles = [20, 40, 60, 80, 99]

# Create a DataFrame to store the percentile values
percentile_values = pd.DataFrame(index=columns_to_analyze, columns=percentiles)

# Calculate and store the percentiles for each column
for column in columns_to_analyze:
    if column in data.columns:
        # Fill missing values with 0 or another value appropriate for your analysis
        filled_data = data[column].fillna(0)
        percentile_values.loc[column] = [filled_data.quantile(p / 100) for p in percentiles]
    else:
        print(f"Column '{column}' not found in the data.")

# Print the calculated percentiles
print(percentile_values)

file1 = open("BENCH.txt","w")
file1.write(percentile_values.to_string())
# import pandas as pd
#
# # Load your data
# data = pd.read_csv('990-Top-1-18.csv')
#
# # Ensure 'avg_employee_comp' is not zero to avoid division by zero errors
# data['highest_salary_to_avg_comp_ratio'] = data.apply(
#     lambda row: row['highest_salary'] / row['avg_employee_comp'] if row['avg_employee_comp'] > 0 else None,
#     axis=1
# )
#
# # Calculate the specified percentiles for the new ratio field
# percentiles = [20, 40, 60, 80, 90]
# percentile_values = {
#     percentile: data['highest_salary_to_avg_comp_ratio'].dropna().quantile(percentile / 100)
#     for percentile in percentiles
# }
#
# # Print the results
# print("Percentiles for the ratio of highest salary to average employee compensation:")
# for p, value in percentile_values.items():
#     print(f"{p}th Percentile: {value}")
