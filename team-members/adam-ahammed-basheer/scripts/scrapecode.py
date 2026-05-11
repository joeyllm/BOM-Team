import pandas as pd

file_path = 'updated_file.parquet'
df = pd.read_parquet(file_path)

# 1. First, ensure Pandas reads the column as a proper datetime object.
# (If it is currently that giant number, pd.to_datetime will fix it)
df['Date'] = pd.to_datetime(df['Date'])

# 2. Convert the datetime object into a strict ISO-8601 text string.
# %Y-%m-%dT%H:%M:%SZ is the exact ISO-8601 standard layout.
df['Date'] = df['Date'].dt.strftime('%Y-%m-%dT%H:%M:%SZ')

# 3. Save it back to a Parquet file
output_path = 'iso_8601_file.parquet'
df.to_parquet(output_path, index=False)

print("Done! The dates are now saved as explicit ISO-8601 strings.")