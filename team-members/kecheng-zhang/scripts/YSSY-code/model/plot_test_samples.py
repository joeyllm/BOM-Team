import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as mticker
import joblib
from pathlib import Path
import random
from datetime import timedelta

# --- Configuration ---
MODEL_FILE = Path("output_quick_model") / "yssy_multi_output_model_24hr_quick.joblib"
TEST_DATA_FILE = Path("data24x0.1") / "test_dataset.txt" # Still needed for model input features and anchor times
YSSY_OBS_FILE = Path("data") / "YSSY.txt"         # New: For full observed data
PLOTS_OUTPUT_DIR = Path("output") / "prediction_plots_24_v1" # New output dir for these plots
PLOTS_OUTPUT_DIR.mkdir(exist_ok=True, parents=True)

TIMESTAMP_COL = "timestamp_t" # For test_dataset.txt
YSSY_TIMESTAMP_COL = "timestamp" # For YSSY.txt

# --- Helper Functions ---
def uv_to_speed_direction(u_input, v_input):
    """
    Converts U and V wind components to speed and direction.
    U_input: positive = wind from West (blowing to East) -> eastward component
    V_input: positive = wind from North (blowing to South) -> southward component
    """
    u_arr = np.asarray(u_input, dtype=float)
    v_arr = np.asarray(v_input, dtype=float)

    u_met = u_arr
    v_met = -v_arr

    wind_speed = np.sqrt(u_met**2 + v_met**2)
    wind_from_dir_deg = (270 - np.degrees(np.arctan2(v_met, u_met))) % 360
    wind_from_dir_deg[wind_speed < 0.1] = 0
    return wind_speed, wind_from_dir_deg

def get_column_names_for_model_input(df_columns):
    """Identifies target and columns to drop for model input preparation."""
    target_cols = [col for col in df_columns if col.startswith("YSSY_u_forecast_t+") or col.startswith("YSSY_v_forecast_t+")]
    target_cols = sorted(target_cols, key=lambda x: (int(x.split('+')[-1]), x.split('_')[1]))

    cols_to_drop_explicit = [
        "BELL_mslp_deriv_t_vs_t3", "BELL_mslp_deriv_t3_vs_t6", "BELL_mslp_deriv_t_vs_t6",
        "MTB_mslp_deriv_t_vs_t3", "MTB_mslp_deriv_t3_vs_t6", "MTB_mslp_deriv_t_vs_t6"
    ]
    cols_to_drop_from_x = [col for col in cols_to_drop_explicit if col in df_columns]
    return target_cols, cols_to_drop_from_x

def plot_forecast_vs_actual(timestamp_anchor, model, model_input_features_row,
                            yssy_obs_df, x_cols_for_model, plot_idx=""):
    """Plots observed data (from yssy_obs_df) and forecasted future winds."""
    
    # --- Time Window for Plotting Observed Data ---
    # t-12h to t+12h (49 half-hourly steps: -24 to +24 relative to anchor's 0-step)
    plot_start_time_obs = timestamp_anchor - timedelta(hours=24)
    plot_end_time_obs = timestamp_anchor + timedelta(hours=24)
    
    #print(f"DEBUG: Plotting window for observed data: {plot_start_time_obs} to {plot_end_time_obs}")
    
    # Slice observed data from yssy_obs_df for this window
    obs_slice = yssy_obs_df[
        (yssy_obs_df[YSSY_TIMESTAMP_COL] >= plot_start_time_obs) &
        (yssy_obs_df[YSSY_TIMESTAMP_COL] <= plot_end_time_obs)
    ].copy()

    print(f"DEBUG: Shape of obs_slice: {obs_slice.shape}")
    if obs_slice.empty:
        print(f"DEBUG: obs_slice is EMPTY. No YSSY.txt data found for anchor {timestamp_anchor} in the window.")
        # You might want to return here or handle it, but for now, let's see if it proceeds
    else:
        print(f"DEBUG: First 3 rows of obs_slice:\n{obs_slice.head(3)}")
        print(f"DEBUG: Last 3 rows of obs_slice:\n{obs_slice.tail(3)}")
        # Check if expected columns exist
        expected_obs_cols = ['air_temp', 'dew_point', 'u_component', 'v_component']
        for col in expected_obs_cols:
            if col not in obs_slice.columns:
                print(f"DEBUG: CRITICAL - Column '{col}' not found in obs_slice columns: {obs_slice.columns.tolist()}")


    # Extract observed values from the slice
    # Add .get(col, default_value) to avoid KeyError if a column is missing, and fill with NaNs
    # This helps the plot proceed even if some data is missing, rather than crashing.
    # A better default might be an array of NaNs of the expected length.
    
    # Determine expected number of points for robust NaN array creation
    # This assumes YSSY.txt has regular 30-min intervals.
    # If not, obs_times will be the definitive source of length.
    
    if not obs_slice.empty:
        obs_times = obs_slice[YSSY_TIMESTAMP_COL].values
        obs_temp = obs_slice.get('air_temp', pd.Series(index=obs_slice.index, dtype=float)).values # Get column or Series of NaNs
        obs_dewp = obs_slice.get('dew_point', pd.Series(index=obs_slice.index, dtype=float)).values
        obs_u = obs_slice.get('u_component', pd.Series(index=obs_slice.index, dtype=float)).values
        obs_v = obs_slice.get('v_component', pd.Series(index=obs_slice.index, dtype=float)).values
    else:
        # If obs_slice is empty, create empty arrays or arrays of NaNs
        # to prevent errors later, though plots will be empty for observed data.
        # For plotting, it's better to have empty arrays if no data.
        obs_times = np.array([])
        obs_temp = np.array([])
        obs_dewp = np.array([])
        obs_u = np.array([])
        obs_v = np.array([])


    # Extract observed values from the slice
    obs_times = obs_slice[YSSY_TIMESTAMP_COL].values
    obs_temp = obs_slice['air_temp'].values
    obs_dewp = obs_slice['dew_point'].values
    obs_u = obs_slice['u_component'].values
    obs_v = obs_slice['v_component'].values
    
    obs_ws, obs_wd = uv_to_speed_direction(obs_u, obs_v)

    # --- Model Prediction ---
    # Model predicts for t+0.5h to t+6h (12 half-hourly steps)
    future_times_forecast = [timestamp_anchor + timedelta(minutes=30 * i) for i in range(1, 49)]
    
    # Prepare input for the model (this row comes from test_dataset.txt)
    X_sample = pd.DataFrame([model_input_features_row[x_cols_for_model]], columns=x_cols_for_model)
    pred_future_uv_flat = model.predict(X_sample)[0] # 24 outputs
    pred_future_u = pred_future_uv_flat[0::2]
    pred_future_v = pred_future_uv_flat[1::2]
    pred_future_ws, pred_future_wd = uv_to_speed_direction(pred_future_u, pred_future_v)

    # --- Plotting ---
    fig, ax1 = plt.subplots(figsize=(18, 10))
    fig.suptitle(f"YSSY Forecast (Anchor: {timestamp_anchor.strftime('%Y-%m-%d %H:%M')})", fontsize=16)

    # Plot observed Temp and Dewpoint
    ax1.plot(obs_times, obs_temp, 'r-', label='Observed Temp (°C)', solid_capstyle='round', zorder=3)
    #ax1.scatter(obs_times, obs_temp, c='red', s=30, zorder=5)
    ax1.plot(obs_times, obs_dewp, 'b-', label='Observed Dewpoint (°C)', solid_capstyle='round', zorder=3)
    #ax1.scatter(obs_times, obs_dewp, c='blue', s=30, zorder=5)

    # Plot observed Wind Speed
    ax1.plot(obs_times, obs_ws, '-', color='gray', label='Observed Wind Speed (kt)', linewidth=3, solid_capstyle='round', zorder=3)
    #ax1.scatter(obs_times, obs_ws, color='gray', s=30, zorder=5)
    
    # Plot forecasted Wind Speed
    ax1.plot(future_times_forecast, pred_future_ws, '', color='black', linewidth=4, label='Forecast Wind Speed (kt)', zorder=4)

    ax1.set_xlabel("Time")
    ax1.set_ylabel("Temperature (°C) / Wind Speed (knots)")
    ax1.tick_params(axis='y')
    ax1.grid(True, linestyle=':', alpha=0.7)

    # Configure Y-axis for Temp/Speed
    ax1.yaxis.set_major_locator(mticker.MultipleLocator(5))
    # Calculate min/max for Y-axis based on all plottable data
    all_ax1_data = np.concatenate([
        obs_temp[np.isfinite(obs_temp)], 
        obs_dewp[np.isfinite(obs_dewp)], 
        obs_ws[np.isfinite(obs_ws)], 
        pred_future_ws[np.isfinite(pred_future_ws)]
    ])
    min_val_ax1 = np.min(all_ax1_data) if all_ax1_data.size > 0 else 0
    max_val_ax1 = np.max(all_ax1_data) if all_ax1_data.size > 0 else 30
    
    ax1_bottom = min(0, np.floor(min_val_ax1 / 5) * 5)
    ax1_top = max(30, np.ceil(max_val_ax1 / 5) * 5)
    ax1.set_ylim(ax1_bottom, ax1_top)

    # Secondary Y-axis for Wind Direction
    ax2 = ax1.twinx()
    
    # Plot observed Wind Direction (scatter only)
    ax2.scatter(obs_times, obs_wd, marker='o', color='darkgray', s=50, label='Observed Wind Dir (°)', zorder=6)
    
    # Plot forecasted Wind Direction (scatter only, thick black crosses)
    ax2.scatter(future_times_forecast, pred_future_wd, marker='X', color='black', s=70, linewidth=1.5, label='Forecast Wind Dir (°)', zorder=7)

    ax2.set_ylabel("Wind Direction (degrees from North)")
    ax2.set_ylim(0, 360)
    ax2.yaxis.set_major_locator(mticker.MultipleLocator(45))
    ax2.tick_params(axis='y')

    # Configure X-axis for t-12h to t+12h
    ax1.set_xlim(plot_start_time_obs, plot_end_time_obs)
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M\n%d-%b'))
    ax1.xaxis.set_major_locator(mdates.HourLocator(interval=2)) # Ticks every 2 hours
    plt.xticks(rotation=0, ha='center')

    # Add a vertical line at the forecast anchor time
    ax1.axvline(timestamp_anchor, color='k', linestyle=':', linewidth=1, alpha=0.7, label='Forecast Anchor')

    # Combine legends
    lines, labels = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax2.legend(lines + lines2, labels + labels2, loc='upper center', bbox_to_anchor=(0.5, -0.15), ncol=3, frameon=False)

    plt.tight_layout(rect=[0, 0.05, 1, 0.95])
    
    plot_filename = PLOTS_OUTPUT_DIR / f"forecast_{timestamp_anchor.strftime('%Y%m%d_%H%M')}{plot_idx}.png"
    plt.savefig(plot_filename)
    print(f"Saved plot: {plot_filename}")
    plt.close(fig)


# --- Main Script ---
if __name__ == "__main__":
    # --- File Checks ---
    if not MODEL_FILE.exists():
        print(f"Error: Model file not found at {MODEL_FILE}"); exit()
    if not TEST_DATA_FILE.exists():
        print(f"Error: Test data file not found at {TEST_DATA_FILE}"); exit()
    if not YSSY_OBS_FILE.exists():
        print(f"Error: YSSY observation file not found at {YSSY_OBS_FILE}"); exit()

    # --- Load Model ---
    print(f"Loading model from {MODEL_FILE}...")
    try:
        model = joblib.load(MODEL_FILE)
        print("Model loaded successfully.")
    except Exception as e:
        print(f"Error loading model: {e}"); exit()

    # --- Load Test Data (for model input features and anchor times) ---
    print(f"Loading test data (for model inputs) from {TEST_DATA_FILE}...")
    try:
        test_df_features = pd.read_csv(TEST_DATA_FILE)
        test_df_features[TIMESTAMP_COL] = pd.to_datetime(test_df_features[TIMESTAMP_COL])
        print(f"Test data for features loaded. Shape: {test_df_features.shape}")
    except Exception as e:
        print(f"Error loading test data for features: {e}"); exit()

    # --- Load YSSY Full Observations Data ---
    print(f"Loading YSSY observation data from {YSSY_OBS_FILE}...")
    try:
        yssy_full_obs_df = pd.read_csv(YSSY_OBS_FILE)
        yssy_full_obs_df[YSSY_TIMESTAMP_COL] = pd.to_datetime(yssy_full_obs_df[YSSY_TIMESTAMP_COL])
        # Set timestamp as index for easier slicing if needed, though direct boolean indexing also works
        yssy_full_obs_df.set_index(YSSY_TIMESTAMP_COL, inplace=True, drop=False)
        yssy_full_obs_df.sort_index(inplace=True) # Ensure it's sorted by time
        print(f"YSSY observation data loaded. Shape: {yssy_full_obs_df.shape}")
    except Exception as e:
        print(f"Error loading YSSY observation data: {e}"); exit()

    # --- Get Column Names for Model Input ---
    # These are derived from the test_df_features (which has the same structure as training data)
    _, COLS_TO_DROP_FROM_X = get_column_names_for_model_input(test_df_features.columns)
    
    # Determine X_COLUMN_ORDER (features model expects)
    # All columns from test_df_features MINUS target columns (which aren't in test_df_features anyway for X)
    # MINUS the timestamp column, MINUS the explicitly dropped columns.
    # The target columns are defined by their prefix, but for X, we just exclude them.
    # A simpler way is to take all columns that are NOT timestamp_t and NOT the BELL/MTB pressure derivs.
    
    # If model has feature_names_in_, use that as the definitive source
    if hasattr(model, 'feature_names_in_'):
        X_COLUMN_ORDER = model.feature_names_in_
        print(f"Using feature names from loaded model: {len(X_COLUMN_ORDER)} features.")
    else:
        # Reconstruct if not available (less robust)
        print("Warning: Model does not have 'feature_names_in_'. Reconstructing feature order.")
        temp_target_cols_for_exclusion = [col for col in test_df_features.columns if col.startswith("YSSY_u_forecast_t+") or col.startswith("YSSY_v_forecast_t+")]
        cols_to_remove_for_x = temp_target_cols_for_exclusion + [TIMESTAMP_COL] + COLS_TO_DROP_FROM_X
        X_COLUMN_ORDER = [col for col in test_df_features.columns if col not in cols_to_remove_for_x]
        print(f"Reconstructed feature order: {len(X_COLUMN_ORDER)} features.")


    # --- Plot for Random Samples ---
    num_random_samples = 100
    if len(test_df_features) == 0:
        print("Test data (for features) is empty. Cannot generate plots."); exit()
    
    if len(test_df_features) < num_random_samples:
        num_random_samples = len(test_df_features)
        print(f"Warning: Requested {num_random_samples} samples, but test set only has {len(test_df_features)}. Plotting all.")

    random_indices = random.sample(range(len(test_df_features)), num_random_samples)

    print(f"\nGenerating {num_random_samples} random sample plots...")
    for i, idx in enumerate(random_indices):
        # This row contains the input features for the model and the anchor timestamp
        model_input_row = test_df_features.iloc[idx]
        anchor_ts = model_input_row[TIMESTAMP_COL]
        
        print(f"\nPlotting for sample {i+1}/{num_random_samples}, anchor time: {anchor_ts}")
        
        plot_forecast_vs_actual(anchor_ts, model, model_input_row,
                                yssy_full_obs_df, # Pass the full YSSY obs DataFrame
                                X_COLUMN_ORDER, plot_idx=f"_rand{i+1}")
    
    anchor_ts = '2024-09-25 14:00:00'

    anchor_ts = pd.to_datetime(anchor_ts)
    #row = df[df['timestamp'] == target_time]

    print(f"\nPlotting for specific time anchor time: {anchor_ts}")
    
    plot_forecast_vs_actual(anchor_ts, model, model_input_row,
                            yssy_full_obs_df, # Pass the full YSSY obs DataFrame
                            X_COLUMN_ORDER, plot_idx=f"_manual")
                                
    print(f"\nAll plots saved to: {PLOTS_OUTPUT_DIR.resolve()}")