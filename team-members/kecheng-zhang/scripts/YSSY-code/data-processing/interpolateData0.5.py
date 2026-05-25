import pandas as pd
import os
import glob
import numpy as np

# --- Configuration ---
PROCESSED_DATA_FOLDER = "ProcessedData"  # Input folder
INTERPOLATED_DATA_FOLDER = "InterpolatedData0.5" # Output folder
START_YEAR_FILTER = None # Optional: Set to a year (e.g., 2005) or None

# Weather elements to interpolate
# Ensure these match the column names in your processed files
ELEMENTS_TO_INTERPOLATE = [
    "air_temp",
    "dew_point",
    "wind_speed",
    "wind_dir",
    "max_gust_speed",
    "msl_pressure"
    # "aws_flag" is typically categorical and not suitable for linear interpolation
]

def interpolate_single_step_gaps(series):
    """
    Linearly interpolates single-timestep NaN gaps in a pandas Series.

    Args:
        series (pd.Series): The input series with potential NaN values.

    Returns:
        pd.Series: The series with single-step gaps interpolated.
    """
    interpolated_series = series.copy()
    is_na = series.isna()
    n = len(series)
    gaps_interpolated_count = 0

    for i in range(1, n - 1): # Iterate from the second to the second-to-last element
        # Check for a single NaN: value[i-1] is not NaN, value[i] is NaN, value[i+1] is not NaN
        if not is_na.iloc[i-1] and is_na.iloc[i] and not is_na.iloc[i+1]:
            # Perform linear interpolation
            interpolated_value = (series.iloc[i-1] + series.iloc[i+1]) / 2.0
            interpolated_series.iloc[i] = interpolated_value
            gaps_interpolated_count += 1
            # print(f"Interpolated at index {i}: {series.iloc[i-1]} + {series.iloc[i+1]} / 2 = {interpolated_value}")


    # Check for a single NaN at the very beginning (index 0) - cannot interpolate
    # Check for a single NaN at the very end (index n-1) - cannot interpolate
    # The loop range 1 to n-1 naturally handles this.

    # Special case: if the series has only two points and one is NaN in the middle (e.g. of length 3)
    # This is covered by the loop.

    if gaps_interpolated_count > 0:
        print(f"    Interpolated {gaps_interpolated_count} single-step gaps for '{series.name}'.")
    return interpolated_series

def process_and_interpolate_files(input_folder, output_folder, start_year=None):
    """
    Reads processed data files, interpolates single-step gaps, and saves them.
    """
    search_pattern = os.path.join(input_folder, "*.txt") # Assuming .txt from previous step
    file_paths = glob.glob(search_pattern)

    if not file_paths:
        print(f"No .txt files found in '{input_folder}'.")
        return

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        print(f"Created output directory: {output_folder}")

    for filepath in file_paths:
        filename = os.path.basename(filepath)
        station_id = filename.split('.')[0] # Assuming filename is like 'STATIONID.txt'
        print(f"\n--- Processing Station: {station_id} ---")
        print(f"  Reading file: {filepath}")

        try:
            # Read the CSV-like .txt file
            df = pd.read_csv(
                filepath,
                parse_dates=['timestamp'],
                na_values=['NaN'] # Ensure 'NaN' strings are read as np.nan
            )

            if df.empty:
                print(f"  Skipping {station_id}: File is empty.")
                continue

            # Apply start year filter if specified
            if start_year:
                original_rows = len(df)
                df = df[df['timestamp'].dt.year >= start_year].copy()
                if df.empty:
                    print(f"  Skipping {station_id}: No data after start year filter ({start_year}). Original rows: {original_rows}")
                    continue
                print(f"  Applied start year filter: {start_year}. Rows: {len(df)} (from {original_rows})")

            # Interpolate for each specified element
            for element in ELEMENTS_TO_INTERPOLATE:
                if element in df.columns:
                    print(f"  Interpolating '{element}'...")
                    # Ensure element column is numeric before interpolation
                    if not pd.api.types.is_numeric_dtype(df[element]):
                        df[element] = pd.to_numeric(df[element], errors='coerce')

                    df[element] = interpolate_single_step_gaps(df[element])
                else:
                    print(f"  Warning: Element '{element}' not found in {filename}. Skipping interpolation for this element.")

            # Recalculate data_completeness (optional, but good practice)
            # If interpolation filled some gaps, the original 'data_completeness' might be outdated for those rows.
            # The definition of completeness here depends on ALL elements in ELEMENTS_TO_INTERPOLATE being present.
            if 'data_completeness' in df.columns:
                print("  Recalculating 'data_completeness' flag...")
                # Check for NaNs in the elements that were subject to interpolation, plus timestamp.
                # `aws_flag` might or might not be part of this check depending on definition.
                # Let's assume completeness requires all elements in ELEMENTS_TO_INTERPOLATE to be non-NaN.
                cols_for_completeness_check = [el for el in ELEMENTS_TO_INTERPOLATE if el in df.columns]
                if cols_for_completeness_check: # only if there are columns to check
                    df['data_completeness'] = df[cols_for_completeness_check].notna().all(axis=1) & df['timestamp'].notna()
                    df['data_completeness'] = df['data_completeness'].astype(int)
                else:
                    print("    No elements found to check for completeness recalculation.")

            # Save the interpolated DataFrame
            output_filepath = os.path.join(output_folder, filename)
            try:
                # Ensure numeric columns are saved with appropriate precision if needed,
                # pandas to_csv usually handles this well.
                df.to_csv(output_filepath, index=False, na_rep='NaN', float_format='%.1f') # Save floats with 1 decimal place
                print(f"  Interpolated file saved: {output_filepath}")
            except Exception as e:
                print(f"    Error saving interpolated file {output_filepath}: {e}")

        except Exception as e:
            print(f"  An unexpected error occurred processing file {filepath}: {e}")
            import traceback
            traceback.print_exc()

    print("\n--- Interpolation process complete. ---")

if __name__ == "__main__":
    # Ensure the output directory exists (moved here for clarity)
    if not os.path.exists(INTERPOLATED_DATA_FOLDER):
        os.makedirs(INTERPOLATED_DATA_FOLDER)
        print(f"Created output directory: {INTERPOLATED_DATA_FOLDER}")

    process_and_interpolate_files(PROCESSED_DATA_FOLDER,
                                   output_folder=INTERPOLATED_DATA_FOLDER,
                                   start_year=START_YEAR_FILTER)