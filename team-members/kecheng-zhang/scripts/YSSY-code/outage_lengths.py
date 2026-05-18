import pandas as pd
import matplotlib.pyplot as plt
import os
import glob
import numpy as np
import matplotlib

# Attempt to set a non-GUI backend if saving is the primary goal.
try:
    matplotlib.use('Agg')
except ImportError:
    print("Warning: Could not set 'Agg' backend. Matplotlib will use default.")
    pass

# --- Configuration ---
PROCESSED_FILES_FOLDER = "InterpolatedData0.5"
OUTAGE_PLOT_OUTPUT_FOLDER = "OutageDistributionPlots_Grouped"
START_YEAR_FILTER = 2005  # Set to None or a year (e.g., 2005) to filter data

WEATHER_ELEMENTS_TO_ANALYZE = [
    "air_temp",
    "dew_point",
    "wind_speed",
    "wind_dir",
    "msl_pressure"
]
ELEMENT_COLORS = plt.cm.get_cmap('viridis', len(WEATHER_ELEMENTS_TO_ANALYZE)) # Or 'tab10', 'Set1' etc.

# Define outage duration bins and their labels (simplified)
OUTAGE_BINS_CONFIG = [
    (1, 2, "30 min"),
    (2, 3, "1 hr"),
    (3, 5, "1.5-2 hr"),
    (5, 13, "2-6 hr"),
    (13, 49, "6-24 hr"),
    (49, 337, "1-7 day"),
    (337, 1441, "7day-1mo"),
    (1441, 17521, "1mo-1yr"),
    (17521, float('inf'), ">1 yr")
]
OUTAGE_BIN_LABELS_SIMPLE = [b[2] for b in OUTAGE_BINS_CONFIG]

def find_outage_durations(series):
    """Identifies consecutive NaN blocks and returns their lengths (number of steps)."""
    outages = []
    is_na = series.isna()
    current_outage_length = 0
    for val_is_na in is_na:
        if val_is_na:
            current_outage_length += 1
        else:
            if current_outage_length > 0:
                outages.append(current_outage_length)
            current_outage_length = 0
    if current_outage_length > 0: # Account for outage at the end
        outages.append(current_outage_length)
    return outages

def categorize_outages(outage_durations_steps, bins_def):
    """Categorizes outage durations into predefined bins."""
    bin_counts = {b[2]: 0 for b in bins_def}
    for duration in outage_durations_steps:
        for lower, upper, label in bins_def:
            if lower <= duration < upper:
                bin_counts[label] += 1
                break
    return pd.Series(bin_counts, index=[b[2] for b in bins_def])

def plot_station_grouped_outage_summary(folder_path, output_folder, start_year=None):
    """
    Analyzes outage distributions and saves a grouped bar chart for each station.
    Also calculates and displays uptime for each element.
    """
    search_pattern = os.path.join(folder_path, "*.txt")
    file_paths = glob.glob(search_pattern)

    if not file_paths:
        print(f"No .txt files found in '{folder_path}'.")
        return

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        print(f"Created output directory for plots: {output_folder}")

    num_elements = len(WEATHER_ELEMENTS_TO_ANALYZE)
    num_bins = len(OUTAGE_BIN_LABELS_SIMPLE)
    bar_width = 0.8 / num_elements  # Width of each individual bar in a group

    for filepath in file_paths:
        station_id = os.path.basename(filepath).split('.')[0]
        print(f"\n--- Analyzing Station: {station_id} ---")

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
                df_filtered = df[df['timestamp'].dt.year >= start_year].copy()
                if df_filtered.empty:
                    print(f"  Skipping {station_id}: No data after start year filter ({start_year}). Original: {original_rows}")
                    continue
                print(f"  Applied start year filter: {start_year}. Rows: {len(df_filtered)} (from {original_rows})")
            else:
                df_filtered = df.copy()

            total_possible_observations = len(df_filtered)
            if total_possible_observations == 0:
                print(f"  Skipping {station_id}: No observations after filtering.")
                continue

            # Data for plotting (bin counts for each element)
            all_elements_binned_outages = pd.DataFrame(index=OUTAGE_BIN_LABELS_SIMPLE)
            uptime_stats = {}
            at_least_one_element_has_outages = False

            for element in WEATHER_ELEMENTS_TO_ANALYZE:
                if element not in df_filtered.columns:
                    print(f"    Skipping element '{element}': Column not found.")
                    all_elements_binned_outages[element] = 0 # Fill with zeros for plotting consistency
                    uptime_stats[element] = "N/A (No Data)"
                    continue

                # Calculate Uptime
                non_missing_count = df_filtered[element].notna().sum()
                uptime_percentage = (non_missing_count / total_possible_observations) * 100 if total_possible_observations > 0 else 0
                uptime_stats[element] = f"{uptime_percentage:.1f}%"

                # Calculate Outage Distribution
                outage_lengths = find_outage_durations(df_filtered[element])
                if outage_lengths:
                    at_least_one_element_has_outages = True
                    binned = categorize_outages(outage_lengths, OUTAGE_BINS_CONFIG)
                    all_elements_binned_outages[element] = binned
                else:
                    all_elements_binned_outages[element] = 0 # No outages, fill with zeros

            if not at_least_one_element_has_outages and all(val == 0 for col in all_elements_binned_outages.columns for val in all_elements_binned_outages[col]):
                 print(f"  No outages found for any element in {station_id}. Skipping plot.")
                 continue


            # --- Plotting ---
            fig, ax = plt.subplots(figsize=(16, 8)) # Single Axes for the grouped bar chart

            x = np.arange(num_bins)  # x locations for the groups

            # Determine y-axis limit, excluding the "30 min" bin for scaling across all elements
            max_y_val_excluding_30min_all_elements = 0
            if num_bins > 0 and not all_elements_binned_outages.empty:
                # Get max of all elements for bins other than the first one ("30 min")
                # The first row of all_elements_binned_outages corresponds to "30 min"
                if len(all_elements_binned_outages.index) > 1:
                    max_y_val_excluding_30min_all_elements = all_elements_binned_outages.iloc[1:].max().max()

            dynamic_y_lim_upper = max(10, max_y_val_excluding_30min_all_elements * 1.25)
            ax.set_ylim(0, dynamic_y_lim_upper)

            for i, element in enumerate(WEATHER_ELEMENTS_TO_ANALYZE):
                if element not in all_elements_binned_outages.columns: # Element column might not exist if skipped
                    continue

                element_outage_counts = all_elements_binned_outages[element].values
                # Calculate position for this element's bars within each group
                # Total width of a group of bars is num_elements * bar_width
                # The first bar in a group starts at x_pos - (total_group_width / 2) + bar_width / 2
                # Then each subsequent bar is bar_width to the right.
                # Simpler: x_pos - (num_elements / 2 * bar_width) + (i * bar_width) + (bar_width / 2 if num_elements is odd else 0 for centering)
                # Corrected:
                offset = bar_width * (i - num_elements / 2 + 0.5)
                positions = x + offset

                bars = ax.bar(positions, element_outage_counts, bar_width,
                              label=element.replace("_", " ").title(),
                              color=ELEMENT_COLORS(i / num_elements)) # Use colormap

                # Add counts on top of bars
                for bar_idx, bar_obj in enumerate(bars):
                    yval = bar_obj.get_height()
                    if yval > 0:
                        # If bar is the "30 min" bar for this element AND it's clipped
                        is_30min_bar_clipped = (bar_idx == 0 and yval > dynamic_y_lim_upper)

                        if is_30min_bar_clipped:
                            ax.text(bar_obj.get_x() + bar_obj.get_width()/2.0, dynamic_y_lim_upper * 0.95,
                                    f'{int(yval)}\n↑', ha='center', va='top', fontsize=7, color='red',
                                    bbox=dict(facecolor='white', alpha=0.6, pad=0.5, edgecolor='none'))
                        else:
                            ax.text(bar_obj.get_x() + bar_obj.get_width()/2.0, yval,
                                    int(yval), ha='center', va='bottom', fontsize=7)

            # --- Plot Customization ---
            title_str = f'Outage Length Distribution - Station: {station_id}'
            if start_year:
                title_str += f' (Since {start_year})'
            ax.set_title(title_str, fontsize=16, pad=20) # Add padding for uptime text

            ax.set_xlabel('Outage Duration Category', fontsize=12)
            ax.set_ylabel('Number of Outages', fontsize=12)
            ax.set_xticks(x)
            ax.set_xticklabels(OUTAGE_BIN_LABELS_SIMPLE, rotation=45, ha="right", fontsize=10)
            ax.tick_params(axis='y', labelsize=10)
            ax.grid(axis='y', linestyle='--', alpha=0.6)
            ax.legend(title="Weather Element", bbox_to_anchor=(1.02, 1), loc='upper left', fontsize=9)

            # --- Add Uptime Statistics to the Plot ---
            uptime_text = "Average Uptime:\n" + "\n".join([f"{el.replace('_', ' ').title()}: {uptime_stats.get(el, 'N/A')}" for el in WEATHER_ELEMENTS_TO_ANALYZE])
            # Place text box. Adjust x, y, ha, va as needed.
            fig.text(0.01, 0.98, uptime_text, transform=fig.transFigure, fontsize=8,
                     verticalalignment='top', horizontalalignment='left',
                     bbox=dict(boxstyle='round,pad=0.5', fc='lightyellow', alpha=0.7))


            plt.tight_layout(rect=[0.05, 0, 0.85, 0.95]) # Adjust rect for legend and uptime text
            plot_filename = os.path.join(output_folder, f"{station_id}_grouped_outages.png")
            try:
                plt.savefig(plot_filename)
                print(f"  Grouped plot saved: {plot_filename}")
            except Exception as e:
                print(f"    Error saving grouped plot {plot_filename}: {e}")
            plt.close(fig)

        except Exception as e:
            print(f"  An unexpected error occurred processing file {filepath} for station {station_id}: {e}")
            import traceback
            traceback.print_exc()
            if 'fig' in locals() and plt.fignum_exists(fig.number):
                 plt.close(fig)

    print("\n--- Grouped outage summary analysis complete. ---")


if __name__ == "__main__":
    if not os.path.exists(OUTAGE_PLOT_OUTPUT_FOLDER):
        os.makedirs(OUTAGE_PLOT_OUTPUT_FOLDER)
        print(f"Created output directory: {OUTAGE_PLOT_OUTPUT_FOLDER}")

    plot_station_grouped_outage_summary(PROCESSED_FILES_FOLDER,
                                          output_folder=OUTAGE_PLOT_OUTPUT_FOLDER,
                                          start_year=START_YEAR_FILTER)