import csv
import pandas as pd

def split_csv(input_file, output_prefix, chunk_size):
    # Read the CSV file into a Pandas DataFrame
    df = pd.read_csv(input_file)
    df['ein'] = df['ein'].astype(int)
    # Determine the total number of rows in the DataFrame
    total_rows = len(df)

    # Calculate the number of chunks needed
    num_chunks = (total_rows + chunk_size - 1) // chunk_size

    # Split the DataFrame into chunks and save each chunk to a separate CSV file
    for i in range(num_chunks):
        start_index = i * chunk_size
        end_index = min((i + 1) * chunk_size, total_rows)
        chunk_data = df.iloc[start_index:end_index]

        # Create the output file name
        output_file = f"{output_prefix}_part_{i + 1}.csv"

        # Save the chunk to a new CSV file
        chunk_data.to_csv(output_file, index=False)

        print(f"Saved {output_file}")

# Specify your input CSV file, output prefix, and chunk size
input_csv_file = '990-Top-2-3.csv'
output_prefix = 'split_csvs/990203'
chunk_size = 1000

# Split the CSV file
split_csv(input_csv_file, output_prefix, chunk_size)
