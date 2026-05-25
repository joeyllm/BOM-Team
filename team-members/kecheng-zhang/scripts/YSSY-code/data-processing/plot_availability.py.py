import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import os
import glob
import matplotlib

# Attempt to set a non-GUI backend if saving is the primary goal.
# 'Agg' is good for saving to files without needing a display.
try:
    matplotlib.use('Agg')
except ImportError:
    print("Warning: Could not set 'Agg' backend. Matplotlib will use default.")
    pass

# Define the key weather elements to plot individually
WEATHER_ELEMENTS_TO_PLOT = [
    "air_temp",
    "dew_point",
    "wind_speed",
    "wind_dir",
    "msl_pressure"
    # "aws_flag" # Typically not plotted for availability like measurements
]

def plot_station_element_availability(folder_path, output_folder="StationPlots"):
    """
    Reads processed weather files, filters for full-hour data, calculates monthly
    availability for specific weather elements, and creates a separate plot
    for each station showing these availabilities.

    Args:
        folder_path (str): Path to the folder containing the processed .txt files.
        output_folder (str): Path to the folder where individual station plots will be saved.
    """
    search_pattern = os.path.join(folder_path, "*.txt")
    file_paths = glob.glob(search_pattern)

    if not file_paths:
        print(f"No .txt files found in '{folder_path}'. Please check the path.")
        return

    # Create output directory for plots if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        print(f"Created output directory for plots: {output_folder}")

    for filepath in file_paths:
        station_id = os.path.basename(filepath).split('.')[0]
        print(f"\n--- Processing Station: {station_id} ---")

        try:
            df = pd.read_csv(
                filepath,
                parse_dates=['timestamp'],
                na_values=['NaN']
            )

            if 'timestamp' not in df.columns:
                print(f"Skipping {station_id}: 'timestamp' column missing.")
                continue
            for element in WEATHER_ELEMENTS_TO_PLOT:
                if element not in df.columns:
                    print(f"Skipping {station_id}: Required element '{element}' column missing.")
                    # Continue to next file if a critical element is missing
                    # Or you could adapt to plot only available elements
                    raise FileNotFoundError(f"Missing {element}") # Force skip for this example

            if df.empty:
                print(f"Skipping {station_id}: File is empty after reading.")
                continue

            # 1. Filter for full-hour observations (minute == 0)
            df_full_hour = df[df['timestamp'].dt.minute == 0].copy() # Use .copy() to avoid SettingWithCopyWarning

            if df_full_hour.empty:
                print(f"Skipping {station_id}: No full-hour data found.")
                continue

            print(f"  Original records: {len(df)}, Full-hour records: {len(df_full_hour)}")

            # Create a 'year_month' period for grouping
            df_full_hour['year_month'] = df_full_hour['timestamp'].dt.to_period('M')

            # Initialize plot for the current station
            plt.figure(figsize=(15, 8))
            plot_has_data = False

            # 2. Calculate and plot availability for each weather element
            for element in WEATHER_ELEMENTS_TO_PLOT:
                # For each month:
                # - total_possible_full_hour_obs: count of all full-hour records in that month
                # - element_available_obs: count of full-hour records where 'element' is not NaN
                monthly_summary = df_full_hour.groupby('year_month').agg(
                    total_possible_full_hour_obs=('timestamp', 'count'), # Count any non-null column, like timestamp
                    element_available_obs=(element, lambda x: x.notna().sum())
                ).reset_index()

                if monthly_summary.empty:
                    print(f"  No monthly summary data for element '{element}' in {station_id}.")
                    continue

                # Calculate percentage of available observations for the element
                monthly_summary['percentage_available'] = 0.0
                monthly_summary.loc[monthly_summary['total_possible_full_hour_obs'] > 0, 'percentage_available'] = \
                    (monthly_summary['element_available_obs'] / monthly_summary['total_possible_full_hour_obs']) * 100

                # Convert 'year_month' Period back to timestamp for plotting
                monthly_summary['plot_date'] = monthly_summary['year_month'].dt.to_timestamp()

                if not monthly_summary.empty:
                    plt.plot(monthly_summary['plot_date'], monthly_summary['percentage_available'],
                             label=element.replace('_', ' ').title(), marker='.', linestyle='-')
                    plot_has_data = True
                else:
                    print(f"  No data to plot for element '{element}' in {station_id}.")


            if not plot_has_data:
                print(f"  No data plotted for station {station_id}. Skipping plot generation.")
                plt.close() # Close the empty figure
                continue

            # --- Final Plot Customization for this station's plot ---
            plt.title(f'Monthly Data Availability for Station: {station_id} (Full Hour Data)', fontsize=16)
            plt.xlabel('Month', fontsize=14)
            plt.ylabel('Percentage of Available Observations (%)', fontsize=14)
            plt.ylim(0, 105)
            plt.grid(True, which='major', linestyle='--', linewidth=0.5)
            plt.legend(loc='best', title='Weather Element')

            ax = plt.gca()
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
            ax.xaxis.set_major_locator(mdates.AutoDateLocator(minticks=8, maxticks=20))
            plt.xticks(rotation=45, ha='right')

            plt.tight_layout()

            # Save the plot for this station
            output_plot_filename = os.path.join(output_folder, f"{station_id}_element_availability.png")
            try:
                plt.savefig(output_plot_filename)
                print(f"  Plot for {station_id} saved to {output_plot_filename}")
            except Exception as e:
                print(f"  Error saving plot for {station_id} to {output_plot_filename}: {e}")
            plt.close() # Close the figure to free memory before the next station

        except FileNotFoundError as fnf_error: # Catch specific error for missing columns
            print(f"Skipping {station_id} due to missing data column: {fnf_error}")
            if plt.gcf().get_axes(): # If a figure was created but not used
                plt.close()
        except Exception as e:
            print(f"An unexpected error occurred processing file {filepath} for station {station_id}: {e}")
            import traceback
            traceback.print_exc()
            if plt.gcf().get_axes(): # If a figure was created but not used
                plt.close()

    print("\n--- All station processing complete. ---")

if __name__ == "__main__":
    # --- Configuration ---
    PROCESSED_FILES_FOLDER = "ProcessedData"  # Folder with your YBBN.txt, YBAF.txt etc.
    # Folder where individual station plots will be saved
    STATION_PLOT_OUTPUT_FOLDER = "StationElementPlots"

    # --- Create dummy files for testing (REMOVE OR COMMENT OUT FOR REAL USE) ---
    if not os.path.exists(PROCESSED_FILES_FOLDER):
        os.makedirs(PROCESSED_FILES_FOLDER)


    plot_station_element_availability(PROCESSED_FILES_FOLDER, output_folder=STATION_PLOT_OUTPUT_FOLDER)