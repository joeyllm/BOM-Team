import pandas as pd
import os
import glob

def process_files(input_folder_path, output_folder_path, columns_to_drop):
    """
    Reads all .txt files from an input folder, drops specified columns,
    and saves them to an output folder with the same name.

    Args:
        input_folder_path (str): Path to the folder containing input .txt files.
        output_folder_path (str): Path to the folder where processed files will be saved.
        columns_to_drop (list): A list of column names to drop.
    """

    # Ensure input folder exists
    if not os.path.isdir(input_folder_path):
        print(f"Error: Input folder '{input_folder_path}' not found.")
        return

    # Create output folder if it doesn't exist
    os.makedirs(output_folder_path, exist_ok=True)
    print(f"Output will be saved to: '{os.path.abspath(output_folder_path)}'")

    # Find all .txt files in the input folder
    search_pattern = os.path.join(input_folder_path, "*.txt")
    file_paths = glob.glob(search_pattern)

    if not file_paths:
        print(f"No .txt files found in '{input_folder_path}'.")
        return

    print(f"Found {len(file_paths)} .txt files to process.")

    for file_path in file_paths:
        try:
            # Get the base filename
            file_name = os.path.basename(file_path)
            output_file_path = os.path.join(output_folder_path, file_name)

            print(f"\nProcessing '{file_name}'...")

            # Read the .txt file as a pandas DataFrame
            df = pd.read_csv(file_path)

            # Identify columns that actually exist in the DataFrame to avoid errors
            existing_columns_to_drop = [col for col in columns_to_drop if col in df.columns]

            if not existing_columns_to_drop:
                print(f"  None of the specified columns to drop {columns_to_drop} were found in this file. Saving as is.")
            else:
                print(f"  Dropping columns: {existing_columns_to_drop}")

            # Drop the specified columns
            df_modified = df.drop(columns=existing_columns_to_drop, errors='ignore')

            # Save the modified DataFrame to the output folder
            df_modified.to_csv(output_file_path, index=False)
            print(f"  Saved modified file to '{output_file_path}'")

        except pd.errors.EmptyDataError:
            print(f"  Warning: '{file_name}' is empty. Skipping.")
        except Exception as e:
            print(f"  Error processing '{file_name}': {e}")

    print("\nProcessing complete.")

if __name__ == "__main__":
    # --- Configuration: Specify your folders and columns here ---
    INPUT_SUBFOLDER_NAME = "SplineInterpolatedData"  # Name of the subfolder for input
    OUTPUT_SUBFOLDER_NAME = "FinalData" # Name of the subfolder for output

    INPUT_SUBFOLDER_NAME = "FinalData"    # Subfolder for input (relative to script location)
    OUTPUT_SUBFOLDER_NAME = "FinalData" # Subfolder for output

    COLUMNS_TO_DROP_LIST = [
        "max_gust_speed",
        "aws_flag",
        "wind_dir_recalc"
    ]
    # --- End of Configuration ---

    # Get the directory where the script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Construct full paths for input and output folders relative to the script's location
    input_folder = os.path.join(script_dir, INPUT_SUBFOLDER_NAME)
    output_folder = os.path.join(script_dir, OUTPUT_SUBFOLDER_NAME)

    print(f"Script directory: {script_dir}")
    print(f"Input folder: {input_folder}")
    print(f"Output folder: {output_folder}")
    print(f"Columns to drop: {COLUMNS_TO_DROP_LIST}")

    process_files(input_folder, output_folder, COLUMNS_TO_DROP_LIST)