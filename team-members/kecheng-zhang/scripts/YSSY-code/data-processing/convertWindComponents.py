import pandas as pd
import os
import glob
import numpy as np

# --- Configuration ---
INPUT_DATA_FOLDER = "InterpolatedData0.5"  # Or "ProcessedData" if starting from earlier stage
OUTPUT_UV_DATA_FOLDER = "UVComponentData"
START_YEAR_FILTER = None # Optional: Set to a year (e.g., 2005) or None

# Original column names for wind
WIND_SPEED_COL = "wind_speed"
WIND_DIR_COL = "wind_dir"

# New column names for U and V components
U_COMPONENT_COL = "u_component"
V_COMPONENT_COL = "v_component"

def convert_to_uv_and_save(input_folder, output_folder, start_year=None):
    """
    Reads data files, converts wind speed/direction to U/V components,
    and saves new files without original wind speed/direction.
    """
    search_pattern = os.path.join(input_folder, "*.txt") # Assuming .txt from previous steps
    file_paths = glob.glob(search_pattern)

    if not file_paths:
        print(f"No .txt files found in '{input_folder}'.")
        return

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        print(f"Created output directory: {output_folder}")

    for filepath in file_paths:
        filename = os.path.basename(filepath)
        station_id = filename.split('.')[0]
        print(f"\n--- Processing Station: {station_id} ---")
        print(f"  Reading file: {filepath}")

        try:
            df = pd.read_csv(
                filepath,
                parse_dates=['timestamp'],
                na_values=['NaN']
            )

            if df.empty:
                print(f"  Skipping {station_id}: File is empty.")
                continue

            if start_year:
                original_rows = len(df)
                df = df[df['timestamp'].dt.year >= start_year].copy()
                if df.empty:
                    print(f"  Skipping {station_id}: No data after start year filter ({start_year}). Original rows: {original_rows}")
                    continue
                print(f"  Applied start year filter: {start_year}. Rows: {len(df)} (from {original_rows})")

            # Check if wind columns exist
            if WIND_SPEED_COL not in df.columns or WIND_DIR_COL not in df.columns:
                print(f"  Warning: '{WIND_SPEED_COL}' or '{WIND_DIR_COL}' not found in {filename}. Skipping UV conversion for this file, saving as is.")
                output_filepath_no_change = os.path.join(output_folder, filename)
                df.to_csv(output_filepath_no_change, index=False, na_rep='NaN', float_format='%.2f')
                print(f"  File saved without UV conversion (wind columns missing): {output_filepath_no_change}")
                continue

            # Ensure wind columns are numeric
            df[WIND_SPEED_COL] = pd.to_numeric(df[WIND_SPEED_COL], errors='coerce')
            df[WIND_DIR_COL] = pd.to_numeric(df[WIND_DIR_COL], errors='coerce')

            # Convert wind direction (degrees) to radians for trigonometric functions
            # Handle NaNs before conversion to avoid warnings/errors
            dir_rad = np.deg2rad(df[WIND_DIR_COL].astype(float)) # Ensure float for np.deg2rad

            # Calculate U and V components
            # U component: positive for wind from the West (eastward wind)
            # V component: positive for wind from the South (northward wind)
            # Meteorological convention (wind FROM):
            # u = -speed * sin(direction_radians)
            # v = -speed * cos(direction_radians)
            df[U_COMPONENT_COL] = -df[WIND_SPEED_COL] * np.sin(dir_rad)
            df[V_COMPONENT_COL] = df[WIND_SPEED_COL] * np.cos(dir_rad)

            # If original speed or direction was NaN, U/V should also be NaN
            # This is naturally handled if NaNs in speed/dir_rad propagate through sin/cos
            # and multiplication. Pandas/Numpy usually do this.
            # Explicitly ensure this if needed:
            mask_nan_wind = df[WIND_SPEED_COL].isna() | df[WIND_DIR_COL].isna()
            df.loc[mask_nan_wind, U_COMPONENT_COL] = np.nan
            df.loc[mask_nan_wind, V_COMPONENT_COL] = np.nan


            print(f"  Calculated U/V components. Sample U: {df[U_COMPONENT_COL].head(3).values}, Sample V: {df[V_COMPONENT_COL].head(3).values}")

            # Prepare DataFrame for saving: drop original wind speed/direction
            columns_to_keep = [col for col in df.columns if col not in [WIND_SPEED_COL, WIND_DIR_COL]]
            df_to_save = df[columns_to_keep]

            # Ensure U and V are at the end or in a sensible order if desired (optional)
            # For now, they will be added as the last columns.

            # Save the DataFrame with U/V components
            output_filepath = os.path.join(output_folder, filename)
            try:
                df_to_save.to_csv(output_filepath, index=False, na_rep='NaN', float_format='%.2f') # Save floats with 2 decimal places
                print(f"  File with U/V components saved: {output_filepath}")
            except Exception as e:
                print(f"    Error saving file {output_filepath}: {e}")

        except Exception as e:
            print(f"  An unexpected error occurred processing file {filepath}: {e}")
            import traceback
            traceback.print_exc()

    print("\n--- U/V component conversion complete. ---")

if __name__ == "__main__":
    # Ensure the output directory exists
    if not os.path.exists(OUTPUT_UV_DATA_FOLDER):
        os.makedirs(OUTPUT_UV_DATA_FOLDER)
        print(f"Created output directory: {OUTPUT_UV_DATA_FOLDER}")

    convert_to_uv_and_save(INPUT_DATA_FOLDER,
                           output_folder=OUTPUT_UV_DATA_FOLDER,
                           start_year=START_YEAR_FILTER)