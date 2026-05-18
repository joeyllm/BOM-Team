import pandas as pd
import os
import glob
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import random
from scipy.interpolate import UnivariateSpline # For more control over splines
import matplotlib

# Attempt to set a non-GUI backend
try:
    matplotlib.use('Agg')
except ImportError:
    print("Warning: Could not set 'Agg' backend. Matplotlib will use default.")
    pass

# --- Configuration ---
UV_COMPONENT_DATA_FOLDER = "UVComponentData"
SPLINE_INTERPOLATED_DATA_OUTPUT_FOLDER = "SplineInterpolatedData"
SPLINE_INTERPOLATION_PLOTS_FOLDER = "SplineInterpolationSamplePlots"
ELEMENTS_TO_SPLINE_INTERPOLATE = ["air_temp", "dew_point", "msl_pressure", "u_component", "v_component"]
ALL_WEATHER_ELEMENTS_FOR_PLOT = ["air_temp", "dew_point", "msl_pressure", "u_component", "v_component", "wind_speed_recalc", "wind_dir_recalc"]
MAX_GAP_STEPS_FOR_SPLINE = 5
SPLINE_CONTEXT_POINTS = 6
SPLINE_ORDER = 3
SPLINE_SMOOTHING_FACTOR = 1
NUM_SAMPLE_PLOTS = 50
PLOT_CONTEXT_HOURS = 12
START_YEAR_FILTER = 2000

# Elements to include in the sample plots. MSLP is removed for scale reasons.
# wind_speed_recalc and wind_dir_recalc will be derived if U/V are present.
ELEMENTS_TO_DISPLAY_ON_PLOT = [
    "air_temp", "dew_point", "wind_speed_recalc", "wind_dir_recalc" # MSLP removed from direct plot
    #,"u_component", "v_component" # Keep U/V for the interpolated element if it's one of them
]

# Colors for plotting elements on the primary Y-axis and wind direction on secondary
PLOT_COLORS = {
    "air_temp": "red",
    "dew_point": "blue",
    "wind_speed_recalc": "black",
    #"u_component": "darkgreen", # If u/v itself was interpolated
    #"v_component": "darkorange",# If u/v itself was interpolated
    "wind_dir_recalc": "dimgray" # For wind direction on its own axis
    # "msl_pressure": "magenta" # Not plotted on primary axis
}

# Elements for primary Y-axis (similar scale)
PRIMARY_Y_AXIS_ELEMENTS = ["air_temp", "dew_point", "wind_speed_recalc"]#, "u_component", "v_component"]



def cubic_spline_interpolate_gap(series_with_gap, gap_start_iloc, gap_end_iloc, context_points, k=3, s=0):
    """
    Interpolates a specific NaN gap in a series using a cubic spline,
    fitted to a limited number of context points before and after the gap.
    Uses integer locations (iloc) for indexing.

    Args:
        series_with_gap (pd.Series): The series containing the NaN gap. Must have DatetimeIndex.
        gap_start_iloc (int): Integer location (iloc) of the start of the gap.
        gap_end_iloc (int): Integer location (iloc) of the end of the gap.
        context_points (int): Number of known data points before and after the gap to use.
        k (int): Degree of the spline.
        s (float): Smoothing factor for UnivariateSpline. s=0 for interpolation.

    Returns:
        pd.Series: A series of interpolated values for the gap (with original DatetimeIndex),
                   or None if interpolation fails.
    """
    n = len(series_with_gap)
    context_before_start_iloc = max(0, gap_start_iloc - context_points)
    context_before_end_iloc = gap_start_iloc - 1
    context_after_start_iloc = gap_end_iloc + 1
    context_after_end_iloc = min(n - 1, gap_end_iloc + context_points)
    x_known_ilocs = []
    y_known_values = []
    if context_before_end_iloc >= context_before_start_iloc:
        s_before = series_with_gap.iloc[context_before_start_iloc : context_before_end_iloc + 1]
        valid_before = s_before.dropna()
        if not valid_before.empty:
            x_known_ilocs.extend([series_with_gap.index.get_loc(idx) for idx in valid_before.index])
            y_known_values.extend(valid_before.values.tolist())
    if context_after_end_iloc >= context_after_start_iloc:
        s_after = series_with_gap.iloc[context_after_start_iloc : context_after_end_iloc + 1]
        valid_after = s_after.dropna()
        if not valid_after.empty:
            x_known_ilocs.extend([series_with_gap.index.get_loc(idx) for idx in valid_after.index])
            y_known_values.extend(valid_after.values.tolist())
    if len(x_known_ilocs) < k + 1:
        return None
    x_known_ilocs_arr = np.array(x_known_ilocs)
    y_known_values_arr = np.array(y_known_values)
    sort_order = np.argsort(x_known_ilocs_arr)
    x_known_ilocs_sorted = x_known_ilocs_arr[sort_order]
    y_known_values_sorted = y_known_values_arr[sort_order]
    unique_x_ilocs, unique_indices = np.unique(x_known_ilocs_sorted, return_index=True)
    if len(unique_x_ilocs) < k + 1:
        return None
    y_known_values_unique = y_known_values_sorted[unique_indices]
    try:
        spline = UnivariateSpline(unique_x_ilocs, y_known_values_unique, k=k, s=s)
        gap_ilocs_to_interpolate = np.arange(gap_start_iloc, gap_end_iloc + 1)
        interpolated_values = spline(gap_ilocs_to_interpolate)
        return pd.Series(interpolated_values, index=series_with_gap.index[gap_ilocs_to_interpolate])
    except Exception:
        return None



def apply_spline_interpolation_to_series(series_original, series_name="series"):
    series = series_original.copy()
    is_na_original = series_original.isna()
    n = len(series)
    interpolation_events_info = []
    current_gap_start_iloc = -1
    for i in range(n):
        if is_na_original.iloc[i] and current_gap_start_iloc == -1:
            current_gap_start_iloc = i
        elif (not is_na_original.iloc[i] or i == n - 1) and current_gap_start_iloc != -1:
            gap_end_iloc = (i - 1) if not is_na_original.iloc[i] else i
            gap_len = gap_end_iloc - current_gap_start_iloc + 1
            if 0 < gap_len <= MAX_GAP_STEPS_FOR_SPLINE:
                interpolated_gap_values = cubic_spline_interpolate_gap(
                    series_original,
                    current_gap_start_iloc, gap_end_iloc,
                    SPLINE_CONTEXT_POINTS, k=SPLINE_ORDER, s=SPLINE_SMOOTHING_FACTOR
                )
                if interpolated_gap_values is not None and not interpolated_gap_values.empty:
                    series.loc[interpolated_gap_values.index] = interpolated_gap_values.values
                    gap_start_timestamp = series_original.index[current_gap_start_iloc]
                    gap_end_timestamp = series_original.index[gap_end_iloc]
                    # print(f"    Spline interpolated '{series_name}' gap len {gap_len} from {gap_start_timestamp} to {gap_end_timestamp}.") # Less verbose
                    interpolation_events_info.append({
                        'time_start_gap': gap_start_timestamp,
                        'time_end_gap': gap_end_timestamp,
                        'method': f'spline(k={SPLINE_ORDER},s={SPLINE_SMOOTHING_FACTOR},ctx={SPLINE_CONTEXT_POINTS})',
                        'len_steps': gap_len
                    })
            elif gap_len > MAX_GAP_STEPS_FOR_SPLINE:
                pass # print(f"    Gap for '{series_name}' len {gap_len} from {series_original.index[current_gap_start_iloc]} is > MAX_GAP_STEPS_FOR_SPLINE. Skipped.")
            current_gap_start_iloc = -1
    return series, interpolation_events_info



def plot_interpolation_sample_spline_v2(df_plot_context, station_id, interpolated_element_name, gap_event_info, output_folder):
    """Plots a sample of spline interpolated data with context, updated y-axis handling and connected thick lines."""
    fig, ax1 = plt.subplots(figsize=(16, 8)) # ax1 for primary elements

    gap_start_time_orig_nan = gap_event_info['time_start_gap'] # Start of original NaN sequence
    gap_end_time_orig_nan = gap_event_info['time_end_gap']     # End of original NaN sequence

    # --- Derive wind speed/direction if U/V were interpolated, or use existing ---
    if "u_component" in df_plot_context.columns and "v_component" in df_plot_context.columns:
        if "wind_speed_recalc" not in df_plot_context.columns:
            df_plot_context["wind_speed_recalc"] = np.sqrt(df_plot_context["u_component"]**2 + df_plot_context["v_component"]**2)
        if "wind_dir_recalc" not in df_plot_context.columns:
            dir_rad_recalc = np.arctan2(-df_plot_context["u_component"], -df_plot_context["v_component"])
            df_plot_context["wind_dir_recalc"] = (np.rad2deg(dir_rad_recalc) + 360) % 360
            if "wind_speed_recalc" in df_plot_context.columns: # Check if it was created
                 df_plot_context["wind_dir_recalc"] = df_plot_context["wind_dir_recalc"].where(df_plot_context["wind_speed_recalc"] > 0.01, np.nan)
            else: # Fallback if wind_speed_recalc somehow wasn't created
                 df_plot_context["wind_dir_recalc"] = np.nan


    lines_ax1_legend = []
    labels_ax1_legend = []
    ax2 = None # Initialize ax2

    # --- Plotting Loop ---
    for el_name in ELEMENTS_TO_DISPLAY_ON_PLOT:
        if el_name not in df_plot_context.columns:
            continue

        series_to_plot = df_plot_context[el_name]
        color = PLOT_COLORS.get(el_name, 'gray')
        current_label_base = el_name.replace('_',' ').title()
        ax_to_use = ax1

        is_target_or_derived_from_interp = (
            el_name == interpolated_element_name or
            (el_name == "wind_speed_recalc" and interpolated_element_name in ["u_component", "v_component"]) or
            (el_name == "wind_dir_recalc" and interpolated_element_name in ["u_component", "v_component"])
        )

        # --- Define anchor times for thick line/highlighted scatter ---
        # These anchors are the last known point before the original NaN gap and first known point after.
        time_anchor_before = gap_start_time_orig_nan # Default to original gap start
        time_anchor_after = gap_end_time_orig_nan   # Default to original gap end
        
        try:
            if not df_plot_context.index.is_monotonic_increasing:
                df_plot_context = df_plot_context.sort_index()

            start_iloc_candidate_gap = df_plot_context.index.searchsorted(gap_start_time_orig_nan, side='left')
            if start_iloc_candidate_gap < len(df_plot_context.index) and df_plot_context.index[start_iloc_candidate_gap] >= gap_start_time_orig_nan:
                gap_start_iloc_in_context = start_iloc_candidate_gap
            elif gap_start_time_orig_nan in df_plot_context.index:
                 gap_start_iloc_in_context = df_plot_context.index.get_loc(gap_start_time_orig_nan)
            else: # Fallback: find closest if not exact
                temp_abs_diff_start = (df_plot_context.index - gap_start_time_orig_nan).to_series().abs()
                closest_ts_start = temp_abs_diff_start.idxmin()
                gap_start_iloc_in_context = df_plot_context.index.get_loc(closest_ts_start)


            end_iloc_candidate_gap = df_plot_context.index.searchsorted(gap_end_time_orig_nan, side='right')
            if end_iloc_candidate_gap > 0 and df_plot_context.index[end_iloc_candidate_gap-1] <= gap_end_time_orig_nan:
                gap_end_iloc_in_context = end_iloc_candidate_gap - 1
            elif gap_end_time_orig_nan in df_plot_context.index:
                gap_end_iloc_in_context = df_plot_context.index.get_loc(gap_end_time_orig_nan)
            else: # Fallback
                temp_abs_diff_end = (df_plot_context.index - gap_end_time_orig_nan).to_series().abs()
                closest_ts_end = temp_abs_diff_end.idxmin()
                gap_end_iloc_in_context = df_plot_context.index.get_loc(closest_ts_end)


            if not (0 <= gap_start_iloc_in_context < len(df_plot_context.index) and \
                    0 <= gap_end_iloc_in_context < len(df_plot_context.index) and \
                    gap_start_iloc_in_context <= gap_end_iloc_in_context):
                raise ValueError("Calculated original gap ilocs are invalid for context.")

            anchor_before_iloc = max(0, gap_start_iloc_in_context - 1)
            anchor_after_iloc = min(len(df_plot_context) - 1, gap_end_iloc_in_context + 1)
            
            time_anchor_before = df_plot_context.index[anchor_before_iloc]
            time_anchor_after = df_plot_context.index[anchor_after_iloc]
        
        except (KeyError, ValueError) as e_anchor:
            print(f"Warning: Error determining precise anchors for {el_name} ('{str(e_anchor)}'). Using original gap times as anchors.")
            # time_anchor_before and time_anchor_after will remain as gap_start/end_time_orig_nan

        # --- Wind Direction plotting on ax2 ---
        if el_name == "wind_dir_recalc":
            if ax2 is None: # Create ax2 only if wind_dir is being plotted
                ax2 = ax1.twinx()
                ax2.set_ylabel("Wind Direction (°)", fontsize=10, color=PLOT_COLORS.get(el_name, "dimgray"))
                ax2.tick_params(axis='y', labelcolor=PLOT_COLORS.get(el_name, "dimgray"))
                ax2.set_ylim(0, 360)
                ax2.set_yticks(np.arange(0, 361, 45))
            ax_to_use = ax2

            if is_target_or_derived_from_interp: # Wind dir influenced by U/V interpolation
                thin_segment_before_wd = series_to_plot.loc[series_to_plot.index < time_anchor_before]
                if not thin_segment_before_wd.empty: ax_to_use.scatter(thin_segment_before_wd.index, thin_segment_before_wd.values, color=color, marker='.', s=15, alpha=0.6)

                thin_segment_after_wd = series_to_plot.loc[series_to_plot.index > time_anchor_after]
                if not thin_segment_after_wd.empty: ax_to_use.scatter(thin_segment_after_wd.index, thin_segment_after_wd.values, color=color, marker='.', s=15, alpha=0.6)

                influenced_segment_wd = series_to_plot.loc[time_anchor_before : time_anchor_after]
                if not influenced_segment_wd.empty:
                    handle = ax_to_use.scatter(influenced_segment_wd.index, influenced_segment_wd.values, color=color, marker='o', s=35, label=current_label_base + " (from Interp. U/V)")
                    lines_ax1_legend.append(handle)
                    labels_ax1_legend.append(current_label_base + " (from Interp. U/V)")
            else: # Context wind direction
                handle = ax_to_use.scatter(series_to_plot.index, series_to_plot.values, color=color, marker='.', s=15, alpha=0.6, label=current_label_base + " (context)")
                lines_ax1_legend.append(handle)
                labels_ax1_legend.append(current_label_base + " (context)")

        # --- Plotting for elements on PRIMARY Y-axis (ax1) ---
        else: # Not wind_dir_recalc
            ax_to_use = ax1
            if is_target_or_derived_from_interp:


                series_before_anchor = series_to_plot.loc[series_to_plot.index <= time_anchor_before]
                if not series_before_anchor.empty:
                    ax_to_use.plot(series_before_anchor.index, series_before_anchor.values,
                                color=color, linewidth=1.5, linestyle='-')

                # Segment 2: The thick line, from the point just BEFORE the gap,
                # through the interpolated values, to the point just AFTER the gap.
                # This segment (time_anchor_before to time_anchor_after) includes both anchors.
                segment_for_thick_line = series_to_plot.loc[time_anchor_before : time_anchor_after]
                if not segment_for_thick_line.empty:
                    line_thick, = ax_to_use.plot(segment_for_thick_line.index, segment_for_thick_line.values,
                                        color=color, linewidth=3.0, linestyle='-', 
                                        label=current_label_base + " (Interpolated Section)")
                    lines_ax1_legend.append(line_thick)
                    labels_ax1_legend.append(current_label_base + " (Interpolated Section)")
                else:
                    print(f"Warning: Thick segment (with anchors) for {el_name} is empty. Anchors: {time_anchor_before} to {time_anchor_after}")

                # Segment 3: Original data from and including the point just AFTER the gap
                # This point (time_anchor_after) was the last point of the thick line
                # AND will be the first point of this thin line.
                series_after_anchor = series_to_plot.loc[series_to_plot.index >= time_anchor_after]
                if not series_after_anchor.empty:
                    ax_to_use.plot(series_after_anchor.index, series_after_anchor.values,
                                color=color, linewidth=1.5, linestyle='-')
                

                # thin_segment_before = series_to_plot.loc[series_to_plot.index < time_anchor_before]
                # if not thin_segment_before.empty: ax_to_use.plot(thin_segment_before.index, thin_segment_before.values, color=color, linewidth=1.5, linestyle='-')

                # thin_segment_after = series_to_plot.loc[series_to_plot.index > time_anchor_after]
                # if not thin_segment_after.empty: ax_to_use.plot(thin_segment_after.index, thin_segment_after.values, color=color, linewidth=1.5, linestyle='-')
                
                # thick_segment_data_with_anchors = series_to_plot.loc[time_anchor_before : time_anchor_after]
                # if not thick_segment_data_with_anchors.empty:
                #     line_thick, = ax_to_use.plot(thick_segment_data_with_anchors.index, thick_segment_data_with_anchors.values,
                #                            color=color, linewidth=3.0, linestyle='-', label=current_label_base + " (Interpolated Section)")
                #     lines_ax1_legend.append(line_thick)
                #     labels_ax1_legend.append(current_label_base + " (Interpolated Section)")
                # else:
                #      print(f"Warning: Thick segment for {el_name} is empty. Anchors: {time_anchor_before} to {time_anchor_after}")
            else: # Context elements on primary axis
                line, = ax_to_use.plot(series_to_plot.index, series_to_plot.values,
                                       color=color, linewidth=1.0, linestyle='-', alpha=0.6, label=current_label_base + " (context)")
                lines_ax1_legend.append(line)
                labels_ax1_legend.append(current_label_base + " (context)")

    ax1.set_xlabel("Timestamp", fontsize=10)
    ax1.set_ylabel("Temp (°C), Dewpt (°C), Speed (kts)", fontsize=10)

    fig.suptitle(f"Spline Interpolation: {interpolated_element_name.replace('_',' ').title()} for {station_id}\nGap: {gap_start_time_orig_nan} to {gap_end_time_orig_nan} (Method: {gap_event_info['method']})", fontsize=12, y=0.98)
    ax1.grid(True, linestyle='--', alpha=0.7)
    fig.autofmt_xdate()

    if lines_ax1_legend:
        fig.legend(lines_ax1_legend, labels_ax1_legend, loc='center left', bbox_to_anchor=(1.0, 0.5), fontsize=8)
        plt.subplots_adjust(right=0.80, top=0.90)
    else:
        plt.subplots_adjust(top=0.90)

    plot_filename = os.path.join(output_folder, f"{station_id}_{interpolated_element_name}_spline_sample_{gap_event_info['sample_num']}.png")
    try:
        plt.savefig(plot_filename)
    except Exception as e:
        print(f"    Error saving sample plot {plot_filename}: {e}")
    plt.close(fig)



# --- (run_spline_interpolation_pipeline and __main__ remain THE SAME as the previously corrected version) ---
# --- Make sure to use the corrected cubic_spline_interpolate_gap and apply_spline_interpolation_to_series from above ---
# --- in your full script. ---
def run_spline_interpolation_pipeline(input_uv_folder, output_spline_folder, plot_output_folder, start_year=None):
    search_pattern = os.path.join(input_uv_folder, "*.txt")
    file_paths = glob.glob(search_pattern)

    if not file_paths:
        print(f"No .txt files found in '{input_uv_folder}'. Ensure UV conversion was run.")
        return

    if not os.path.exists(output_spline_folder): os.makedirs(output_spline_folder)
    if not os.path.exists(plot_output_folder): os.makedirs(plot_output_folder)

    master_interpolation_events_log = []

    for filepath in file_paths:
        filename = os.path.basename(filepath)
        station_id = filename.split('.')[0]
        print(f"\n--- Processing Station for Spline Interpolation: {station_id} ---")

        try:
            df_original_uv = pd.read_csv(filepath, parse_dates=['timestamp'], na_values=['NaN'])
            if df_original_uv.empty: continue

            df = df_original_uv.copy()
            if start_year:
                df = df[df['timestamp'].dt.year >= start_year].copy()
                if df.empty: continue

            df = df.set_index('timestamp')
            df_to_save = df.copy()

            station_events_for_plotting = []

            for element in ELEMENTS_TO_SPLINE_INTERPOLATE: # This list now includes u_component and v_component
                if element not in df.columns:
                    print(f"  Element '{element}' not found in {station_id}. Skipping.")
                    continue

                print(f"  Spline interpolating '{element}' for {station_id}...")
                if not pd.api.types.is_numeric_dtype(df[element]):
                    df[element] = pd.to_numeric(df[element], errors='coerce')
                    if df[element].isnull().all() and not df_original_uv[element].isnull().all():
                         print(f"    Warning: Column '{element}' became all NaNs after to_numeric coercion. Check data.")

                interpolated_series, interp_info_list_element = apply_spline_interpolation_to_series(df[element], series_name=element)
                df_to_save[element] = interpolated_series

                for info in interp_info_list_element:
                    info['station_id'] = station_id
                    info['element'] = element # Record which base element (or component) was interpolated
                    station_events_for_plotting.append(info)

            if 'u_component' in df_to_save.columns and 'v_component' in df_to_save.columns:
                print(f"  Recalculating wind_speed and wind_dir from interpolated U/V for {station_id}")
                df_to_save['wind_speed_recalc'] = np.sqrt(df_to_save['u_component']**2 + df_to_save['v_component']**2)
                dir_rad_recalc = np.arctan2(-df_to_save['u_component'], -df_to_save['v_component'])
                df_to_save['wind_dir_recalc'] = (np.rad2deg(dir_rad_recalc) + 360) % 360
                df_to_save['wind_dir_recalc'] = df_to_save['wind_dir_recalc'].where(df_to_save['wind_speed_recalc'].notna() & (df_to_save['wind_speed_recalc'] > 0.01), np.nan)

            if 'data_completeness' in df_to_save.columns:
                print(f"  Recalculating 'data_completeness' for {station_id}...")
                # For completeness, consider original elements, not U/V directly, but rather the derived speed/dir.
                # However, the interpolation was on U/V. A pragmatic choice is to check all non-derived interpolated elements + derived wind.
                temp_cols_for_completeness = ["air_temp", "dew_point", "msl_pressure"]
                if 'wind_speed_recalc' in df_to_save.columns: temp_cols_for_completeness.append('wind_speed_recalc')
                if 'wind_dir_recalc' in df_to_save.columns: temp_cols_for_completeness.append('wind_dir_recalc')
                
                cols_present_for_completeness = [el for el in temp_cols_for_completeness if el in df_to_save.columns]
                if cols_present_for_completeness:
                    df_to_save['data_completeness'] = df_to_save[cols_present_for_completeness].notna().all(axis=1).astype(int)


            output_filepath = os.path.join(output_spline_folder, filename)
            df_to_save.reset_index().to_csv(output_filepath, index=False, na_rep='NaN', float_format='%.3f')
            print(f"  Spline interpolated file saved: {output_filepath}")

            master_interpolation_events_log.extend(station_events_for_plotting)

        except Exception as e:
            print(f"  Error processing {station_id} for spline interpolation: {e}")
            import traceback
            traceback.print_exc()

    print("\n--- Generating Random Sample Spline Interpolation Plots ---")
    if not master_interpolation_events_log:
        print("  No interpolation events recorded. No sample plots to generate.")
        return

    num_total_samples_to_plot = min(NUM_SAMPLE_PLOTS, len(master_interpolation_events_log))
    if num_total_samples_to_plot == 0:
        print("  No interpolation events to sample for plotting.")
        return

    sampled_events_for_plotting = random.sample(master_interpolation_events_log, num_total_samples_to_plot)
    print(f"  Selected {num_total_samples_to_plot} random interpolation events for plotting.")
    context_delta = pd.Timedelta(hours=PLOT_CONTEXT_HOURS)

    for i, event_info in enumerate(sampled_events_for_plotting):
        station_id_plot = event_info['station_id']
        element_interpolated = event_info['element'] # This is the element (or U/V component) that triggered the event
        plot_file_path = os.path.join(output_spline_folder, f"{station_id_plot}.txt")
        if not os.path.exists(plot_file_path):
            print(f"    Plot source file not found: {plot_file_path}. Skipping this sample plot.")
            continue

        df_plot_final_interp = pd.read_csv(plot_file_path, parse_dates=['timestamp'], na_values=['NaN'])
        df_plot_final_interp = df_plot_final_interp.set_index('timestamp')

        plot_start_time = event_info['time_start_gap'] - context_delta
        plot_end_time = event_info['time_end_gap'] + context_delta
        try:
            min_data_time, max_data_time = df_plot_final_interp.index.min(), df_plot_final_interp.index.max()
            actual_plot_start = max(min_data_time, plot_start_time)
            actual_plot_end = min(max_data_time, plot_end_time)
            df_context_slice = df_plot_final_interp.loc[actual_plot_start : actual_plot_end]
        except Exception as slice_err: # More generic exception for slicing
            print(f"    Error slicing data for plot ({station_id_plot}, {element_interpolated}): {slice_err}. Skipping.")
            continue
        if df_context_slice.empty:
            print(f"    Context slice empty for plot ({station_id_plot}, {element_interpolated}). Skipping.")
            continue

        event_info_for_plot = event_info.copy()
        event_info_for_plot['sample_num'] = i + 1
        # Pass the name of the element that was originally interpolated to guide highlighting
        plot_interpolation_sample_spline_v2(df_context_slice, station_id_plot, element_interpolated, event_info_for_plot, plot_output_folder)


    print("\n--- Spline interpolation and plotting pipeline complete. ---")


if __name__ == "__main__":
    run_spline_interpolation_pipeline(
        UV_COMPONENT_DATA_FOLDER, # Takes output from UV conversion script as input
        SPLINE_INTERPOLATED_DATA_OUTPUT_FOLDER,
        SPLINE_INTERPOLATION_PLOTS_FOLDER,
        start_year=START_YEAR_FILTER
    )