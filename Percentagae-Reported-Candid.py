import pandas as pd

# Load CSV file into a DataFrame
csv_file_path = 'Candid-Demographics-Top-4500.csv'
csv_df = pd.read_csv(csv_file_path)


percentage_non_empty = {}
total_rows = len(csv_df)

for column in csv_df.columns:
    non_empty_count = csv_df[column].count()
    percentage = (non_empty_count / total_rows) * 100
    percentage_non_empty[column] = percentage

# Display the result
print("Percentage of non-empty values in each column:")
for column, percentage in percentage_non_empty.items():
    print(f"{column}: {percentage:.2f}%")
