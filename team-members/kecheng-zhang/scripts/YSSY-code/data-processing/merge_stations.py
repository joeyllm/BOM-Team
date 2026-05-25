import pandas as pd
import os

# Define the weather observation parameters (and aws_flag)
# These are the columns (without _f1 or _f2 suffixes) we'll be working with for merging values
# and for recalculating data_completeness.
WEATHER_PARAMS = [
    "air_temp",
    "dew_point",
    "wind_speed",
    "wind_dir",
    "max_gust_speed",
    "msl_pressure",
    "aws_flag" # aws_flag should also follow the merge logic
]

def read_processed_file(filepath):
    """Reads a processed weather data file into a pandas DataFrame."""
    try:
        # Specify dtypes to ensure correct parsing, especially for timestamp
        # and to handle potential 'NaN' strings for numeric columns
        df = pd.read_csv(
            filepath,
            na_values=['NaN'], # Treat string 'NaN' as actual NaN
            parse_dates=['timestamp'],
            infer_datetime_format=True
        )
        print(f"Successfully read: {filepath}, shape: {df.shape}")
        # Ensure numeric columns are indeed numeric, if not already handled by na_values
        for col in WEATHER_PARAMS:
            if col in df.columns and df[col].dtype == 'object':
                df[col] = pd.to_numeric(df[col], errors='coerce')
        return df
    except FileNotFoundError:
        print(f"Error: File not found - {filepath}")
        return None
    except Exception as e:
        print(f"Error reading file {filepath}: {e}")
        return None

def merge_weather_data(file1_path, file2_path, output_filepath):
    """
    Merges two processed weather data files based on specified rules.

    Args:
        file1_path (str): Path to the first processed weather file (older station).
        file2_path (str): Path to the second processed weather file (newer station).
        output_filepath (str): Path to save the merged data.
    """
    print(f"Starting merge process for:\n  File 1: {file1_path}\n  File 2: {file2_path}")

    df1 = read_processed_file(file1_path)
    df2 = read_processed_file(file2_path)

    if df1 is None or df2 is None:
        print("One or both input files could not be read. Aborting merge.")
        return

    # Perform an outer merge on the timestamp to keep all records from both files
    # Suffixes are added to distinguish columns from df1 and df2
    merged_df = pd.merge(df1, df2, on="timestamp", how="outer", suffixes=("_f1", "_f2"))
    print(f"Shape after outer merge: {merged_df.shape}")

    # Apply the merging logic for each weather parameter
    for param in WEATHER_PARAMS:
        param_f1 = f"{param}_f1"
        param_f2 = f"{param}_f2"

        # Create the final merged column for the parameter
        # Rule: If file2 has data, use it. Else if file1 has data, use it. Else NaN.
        # pandas' combine_first is perfect for this:
        # It uses the value from the first series (param_f2) if not NaN,
        # otherwise it uses the value from the second series (param_f1).
        if param_f2 in merged_df.columns and param_f1 in merged_df.columns:
            merged_df[param] = merged_df[param_f2].combine_first(merged_df[param_f1])
        elif param_f2 in merged_df.columns: # Only data from file 2 for this param
            merged_df[param] = merged_df[param_f2]
            print(f"Warning: Parameter '{param_f1}' not found in merged data from file1. Using only file2 data for '{param}'.")
        elif param_f1 in merged_df.columns: # Only data from file 1 for this param
            merged_df[param] = merged_df[param_f1]
            print(f"Warning: Parameter '{param_f2}' not found in merged data from file2. Using only file1 data for '{param}'.")
        else:
            print(f"Warning: Neither '{param_f1}' nor '{param_f2}' found for parameter '{param}'. Column '{param}' will be all NaN.")
            merged_df[param] = pd.NA # Or float('nan') if preferred for numeric


    # Recalculate 'data_completeness' based on the newly merged WEATHER_PARAMS
    # Exclude 'aws_flag' from completeness check if it's not considered a measurement
    # For this example, I'll assume all WEATHER_PARAMS (including aws_flag) are checked.
    # If 'aws_flag' should not be part of completeness, remove it from this list:
    params_for_completeness = [p for p in WEATHER_PARAMS if p in merged_df.columns]

    merged_df['data_completeness'] = merged_df[params_for_completeness].notna().all(axis=1)
    merged_df['data_completeness'] = merged_df['data_completeness'].astype(int)

    # Define the final columns for the output file
    # We want 'timestamp', the merged weather parameters, and the new 'data_completeness'
    final_columns = ['timestamp'] + WEATHER_PARAMS + ['data_completeness']
    
    # Ensure all final columns actually exist in merged_df before selecting
    final_columns_present = [col for col in final_columns if col in merged_df.columns]
    if len(final_columns_present) != len(final_columns):
        missing_cols = set(final_columns) - set(final_columns_present)
        print(f"Warning: Some final columns are missing from the merged DataFrame: {missing_cols}. They will not be in the output.")

    output_df = merged_df[final_columns_present]

    # Sort by timestamp for consistency
    output_df = output_df.sort_values(by="timestamp").reset_index(drop=True)

    # Save the merged data
    try:
        # Ensure the output directory exists
        output_dir = os.path.dirname(output_filepath)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
            print(f"Created output directory: {output_dir}")

        output_df.to_csv(output_filepath, index=False, na_rep='NaN')
        print(f"Successfully merged data and saved to: {output_filepath}")
        print(f"Final merged data shape: {output_df.shape}")
        if not output_df.empty:
            print("First 5 rows of merged data:")
            print(output_df.head().to_string())

    except Exception as e:
        print(f"Error saving merged file to {output_filepath}: {e}")

if __name__ == "__main__":
    # --- Configuration for the merge ---
    # You MUST change these paths to point to your actual PROCESSED files
    # and specify your desired output path.

    # Example:
    # Assuming your processed files are in a 'ProcessedData' subdirectory
    # relative to where this script is run.

    processed_data_folder = "ProcessedData Manual" # Or wherever your processed files are

    # FILE 1: Data from the older/first station
    file1_name = "YSRI.txt" # Replace with actual filename
    # FILE 2: Data from the newer/second station (data from this file is prioritized)
    file2_name = "YSRI Old.txt" # Replace with actual filename

    # OUTPUT FILE: Name for the combined data
    output_file_name = "YSRI_merged.txt"

    # Construct full paths
    path_to_file1 = os.path.join(processed_data_folder, file1_name)
    path_to_file2 = os.path.join(processed_data_folder, file2_name)
    path_to_output_file = os.path.join(processed_data_folder, output_file_name) # Or a different output folder

    # --- Create dummy processed files for testing (REMOVE OR COMMENT OUT FOR REAL USE) ---
    # This section is only for making the script runnable for demonstration.
    # In your real use case, you'll have actual files from the previous script.
    if not os.path.exists(processed_data_folder):
        os.makedirs(processed_data_folder)

    # --- Run the merge ---
    if os.path.exists(path_to_file1) and os.path.exists(path_to_file2):
        merge_weather_data(path_to_file1, path_to_file2, path_to_output_file)
    else:
        print("\nOne or both specified input files do not exist. Please check paths and filenames.")
        print(f"Expected File 1: {path_to_file1}")
        print(f"Expected File 2: {path_to_file2}")
        if not os.path.exists(processed_data_folder):
            print(f"The folder '{processed_data_folder}' does not exist.")