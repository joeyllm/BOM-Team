import pandas as pd
import os
import glob

def filter_files_by_year_range(input_folder_path, output_folder_path, start_year, end_year):
    """
    Reads all .txt files from an input folder, filters rows based on a year range
    (inclusive) derived from the 'timestamp' column, and saves them to an output folder.

    Args:
        input_folder_path (str): Path to the folder containing input .txt files.
        output_folder_path (str): Path to the folder where filtered files will be saved.
        start_year (int): The first year to include in the data.
        end_year (int): The last year to include in the data.
    """

    # Ensure input folder exists
    if not os.path.isdir(input_folder_path):
        print(f"Error: Input folder '{input_folder_path}' not found.")
        return

    # Create output folder if it doesn't exist
    os.makedirs(output_folder_path, exist_ok=True)
    print(f"Filtered output will be saved to: '{os.path.abspath(output_folder_path)}'")

    # Define the date range boundaries
    # Ensure the entire end_year is included up to its last moment
    try:
        start_date_dt = pd.Timestamp(f"{start_year}-01-01 00:00:00")
        end_date_dt = pd.Timestamp(f"{end_year}-12-31 23:59:59")
    except ValueError as e:
        print(f"Error: Invalid start_year ({start_year}) or end_year ({end_year}). Please provide valid years. {e}")
        return

    if start_date_dt > end_date_dt:
        print(f"Error: START_YEAR ({start_year}) cannot be after END_YEAR ({end_year}).")
        return

    print(f"Filtering data from {start_date_dt.strftime('%Y-%m-%d')} to {end_date_dt.strftime('%Y-%m-%d')} (inclusive).")

    # Find all .txt files in the input folder
    search_pattern = os.path.join(input_folder_path, "*.txt")
    file_paths = glob.glob(search_pattern)

    if not file_paths:
        print(f"No .txt files found in '{input_folder_path}'.")
        return

    print(f"Found {len(file_paths)} .txt files to process.")

    for file_path in file_paths:
        try:
            file_name = os.path.basename(file_path)
            output_file_path = os.path.join(output_folder_path, file_name)

            print(f"\nProcessing '{file_name}'...")

            df = pd.read_csv(file_path)

            if df.empty:
                print("  File is empty. Saving an empty file.")
                df.to_csv(output_file_path, index=False)
                continue

            # Assume the first column is 'timestamp' or try to find it
            timestamp_col_name = 'timestamp' # Default assumption
            if timestamp_col_name not in df.columns:
                if df.columns[0]: # If there's at least one column
                    timestamp_col_name = df.columns[0]
                    print(f"  Warning: 'timestamp' column not found. Assuming first column '{timestamp_col_name}' is the timestamp.")
                else:
                    print(f"  Error: No columns found in '{file_name}'. Skipping.")
                    continue
            
            # Convert timestamp column to datetime objects
            # 'coerce' will turn unparseable dates into NaT (Not a Time)
            df[timestamp_col_name] = pd.to_datetime(df[timestamp_col_name], errors='coerce')

            # Drop rows where timestamp conversion failed
            original_rows = len(df)
            df.dropna(subset=[timestamp_col_name], inplace=True)
            if len(df) < original_rows:
                print(f"  Dropped {original_rows - len(df)} rows due to unparseable timestamps.")

            if df.empty:
                print(f"  File is empty after attempting to parse timestamps. Saving an empty file.")
                df.to_csv(output_file_path, index=False)
                continue

            # Filter rows based on the date range
            df_filtered = df[
                (df[timestamp_col_name] >= start_date_dt) &
                (df[timestamp_col_name] <= end_date_dt)
            ]

            if df_filtered.empty:
                print(f"  No data found within the specified year range ({start_year}-{end_year}). Saving an empty file.")
            else:
                print(f"  Filtered {len(df_filtered)} rows from original {original_rows} (after NaT drop).")

            df_filtered.to_csv(output_file_path, index=False)
            print(f"  Saved filtered file to '{output_file_path}'")

        except pd.errors.EmptyDataError:
            print(f"  Warning: '{file_name}' is empty or became empty after initial read. Skipping.")
        except Exception as e:
            print(f"  Error processing '{file_name}': {e}")

    print("\nYear filtering complete.")

if __name__ == "__main__":
    # --- Configuration: Specify your folders and year range here ---
    INPUT_SUBFOLDER_NAME = "FinalData"    # Subfolder for input (relative to script location)
    OUTPUT_SUBFOLDER_NAME = "FinalData2000" # Subfolder for output

    START_YEAR_CONFIG = 2000  # Inclusive start year
    END_YEAR_CONFIG = 2000    # Inclusive end year
    # --- End of Configuration ---

    script_dir = os.path.dirname(os.path.abspath(__file__))
    input_folder = os.path.join(script_dir, INPUT_SUBFOLDER_NAME)
    output_folder = os.path.join(script_dir, OUTPUT_SUBFOLDER_NAME)

    print(f"Script directory: {script_dir}")
    print(f"Input folder for year filtering: {input_folder}")
    print(f"Output folder for year filtering: {output_folder}")
    print(f"Filtering for years: {START_YEAR_CONFIG} to {END_YEAR_CONFIG} (inclusive)")

    filter_files_by_year_range(input_folder, output_folder, START_YEAR_CONFIG, END_YEAR_CONFIG)