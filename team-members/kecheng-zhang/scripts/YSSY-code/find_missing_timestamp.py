import pandas as pd
import os

DATA_FOLDER = "FinalData" # Adjust if your script is in a different location
FILE1_NAME = "YSNW.txt"
FILE2_NAME = "YSCN.txt" # A reference file assumed to be complete

DATA_START_DATE = pd.Timestamp("2000-01-01 00:00:00")
DATA_END_DATE = pd.Timestamp("2024-12-31 23:30:00")
TIMESTEP_MINUTES = 30

print(f"Comparing {FILE1_NAME} with {FILE2_NAME}")

# Load file 1 (the one with potential missing rows)
try:
    df1 = pd.read_csv(os.path.join(DATA_FOLDER, FILE1_NAME))
    df1['timestamp'] = pd.to_datetime(df1['timestamp'])
    df1 = df1.set_index('timestamp')
    print(f"Loaded {FILE1_NAME}, shape: {df1.shape}")
except Exception as e:
    print(f"Error loading {FILE1_NAME}: {e}")
    exit()

# Load file 2 (reference)
try:
    df2 = pd.read_csv(os.path.join(DATA_FOLDER, FILE2_NAME))
    df2['timestamp'] = pd.to_datetime(df2['timestamp'])
    df2 = df2.set_index('timestamp')
    print(f"Loaded {FILE2_NAME}, shape: {df2.shape}")
except Exception as e:
    print(f"Error loading {FILE2_NAME}: {e}")
    exit()

# Create the expected full date range
expected_range = pd.date_range(start=DATA_START_DATE, end=DATA_END_DATE, freq=f"{TIMESTEP_MINUTES}T")
expected_timestamps = set(expected_range)

print(f"\nNumber of expected timestamps in full range: {len(expected_timestamps)}")

# Timestamps present in df1
df1_timestamps = set(df1.index)
print(f"Number of unique timestamps in {FILE1_NAME}: {len(df1_timestamps)}")

# Timestamps present in df2 (for reference, should be close to expected_timestamps if complete)
df2_timestamps = set(df2.index)
print(f"Number of unique timestamps in {FILE2_NAME}: {len(df2_timestamps)}")


# Find timestamps in expected_range but NOT in df1
missing_in_df1 = sorted(list(expected_timestamps - df1_timestamps))
print(f"\nTimestamps missing in {FILE1_NAME} (compared to full expected range): {len(missing_in_df1)}")
if missing_in_df1:
    print("First 20 missing timestamps in YSNW:")
    for ts in missing_in_df1[:20]:
        print(ts)
    if len(missing_in_df1) > 20:
        print("...")
        print("Last 20 missing timestamps in YSNW:")
        for ts in missing_in_df1[-20:]:
            print(ts)

# As a sanity check, find timestamps in df1 but not in expected_range (should be none)
extra_in_df1 = sorted(list(df1_timestamps - expected_timestamps))
if extra_in_df1:
    print(f"\nWARNING: Timestamps present in {FILE1_NAME} but NOT in expected range: {len(extra_in_df1)}")
    print("First 20 extra timestamps:")
    for ts in extra_in_df1[:20]:
        print(ts)

# Direct comparison with df2 (YSCN)
# Timestamps in df2 but not in df1
missing_in_df1_vs_df2 = sorted(list(df2_timestamps - df1_timestamps))
print(f"\nTimestamps in {FILE2_NAME} but missing in {FILE1_NAME}: {len(missing_in_df1_vs_df2)}")
if missing_in_df1_vs_df2:
    print(f"First 20 timestamps in {FILE2_NAME} but not in {FILE1_NAME}:")
    for ts in missing_in_df1_vs_df2[:20]:
        print(ts)

# Timestamps in df1 but not in df2
missing_in_df2_vs_df1 = sorted(list(df1_timestamps - df2_timestamps))
print(f"\nTimestamps in {FILE1_NAME} but missing in {FILE2_NAME}: {len(missing_in_df2_vs_df1)}")
if missing_in_df2_vs_df1:
    print(f"First 20 timestamps in {FILE1_NAME} but not in {FILE2_NAME}:")
    for ts in missing_in_df2_vs_df1[:20]:
        print(ts)