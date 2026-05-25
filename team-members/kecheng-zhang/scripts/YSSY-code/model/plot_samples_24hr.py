import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as mticker
import joblib
from pathlib import Path
import random
from datetime import timedelta
import glob # For finding model files

# --- Configuration ---
MODELS_DIR_BASE = Path("output_final_models") # Directory where u_models and v_models subfolders are
TEST_DATA_FILE = Path("data24") / "test_dataset.txt"
YSSY_OBS_FILE = Path("data") / "YSSY.txt" # Ensure this path is correct for your current YSSY obs file
PLOTS_OUTPUT_DIR = Path("Jan-2024 plots")
PLOTS_OUTPUT_DIR.mkdir(exist_ok=True, parents=True)

TIMESTAMP_COL = "timestamp_t" # For test_dataset.txt (anchor times and features)
YSSY_TIMESTAMP_COL = "timestamp" # For YSSY.txt (observed data)

NUM_FORECAST_STEPS = 48 # For 24-hour forecast (t+1 to t+48)
TARGET_STATION_PREFIX = "YSSY"

# --- Helper Functions ---
def uv_to_speed_direction(u_input, v_input):
    u_arr = np.asarray(u_input, dtype=float)
    v_arr = np.asarray(v_input, dtype=float)
    u_met = u_arr
    v_met = -v_arr # Meteorological v is positive for northerly wind (from North)
    wind_speed = np.sqrt(u_met**2 + v_met**2)
    wind_from_dir_deg = (270 - np.degrees(np.arctan2(v_met, u_met))) % 360
    wind_from_dir_deg[wind_speed < 0.1] = 0 # Calm or near-calm is often reported as 0 degrees
    return wind_speed, wind_from_dir_deg

def load_individual_models(models_base_dir):
    """Loads all .joblib models from u_models and v_models subdirectories."""
    loaded_models = {}
    feature_names_from_model = None
    
    for component in ['u', 'v']:
        component_dir = models_base_dir / f"{component}_models"
        if not component_dir.exists():
            print(f"Warning: Directory not found, skipping: {component_dir}")
            continue
            
        model_files = list(component_dir.glob("*.joblib"))
        print(f"Found {len(model_files)} models in {component_dir}")
        
        for model_file in model_files:
            target_name = model_file.stem # e.g., YSSY_u_forecast_t_plus_1
            try:
                model_obj = joblib.load(model_file)
                loaded_models[target_name] = model_obj
                print(f"  Loaded: {target_name}")

                # Try to get feature names from the first successfully loaded model
                if feature_names_from_model is None:
                    if hasattr(model_obj, 'feature_name_'): # For LGBM Scikit-Learn API
                        feature_names_from_model = model_obj.feature_name_
                    elif hasattr(model_obj, 'booster_') and hasattr(model_obj.booster_, 'feature_name'): # For LGBM core API
                         feature_names_from_model = model_obj.booster_.feature_name()
                    if feature_names_from_model is not None:
                        print(f"    Got feature names (count: {len(feature_names_from_model)}) from model {target_name}")

            except Exception as e:
                print(f"Error loading model {model_file}: {e}")
    
    if not loaded_models:
        print("Warning: No individual models were loaded.")
    if feature_names_from_model is None and loaded_models:
        print("Warning: Could not extract feature names from any loaded model.")
        
    return loaded_models, feature_names_from_model

def get_predictions_from_individual_models(
    loaded_models_dict, X_sample_df, num_fcst_steps, station_prefix
):
    """
    Generates u and v predictions by querying individual models.
    Fills with NaN if a specific model is not available.
    """
    pred_u = np.full(num_fcst_steps, np.nan)
    pred_v = np.full(num_fcst_steps, np.nan)

    for step in range(1, num_fcst_steps + 1):
        # U-component
        target_name_u = f"{station_prefix}_u_forecast_t_plus_{step}"
        if target_name_u in loaded_models_dict:
            model_u = loaded_models_dict[target_name_u]
            pred_u[step-1] = model_u.predict(X_sample_df)[0]
        else:
            # print(f"Debug: Model for {target_name_u} not found. Using NaN.")
            pass


        # V-component
        target_name_v = f"{station_prefix}_v_forecast_t_plus_{step}"
        if target_name_v in loaded_models_dict:
            model_v = loaded_models_dict[target_name_v]
            pred_v[step-1] = model_v.predict(X_sample_df)[0]
        else:
            # print(f"Debug: Model for {target_name_v} not found. Using NaN.")
            pass
            
    return pred_u, pred_v


def plot_forecast_vs_actual(timestamp_anchor, loaded_models_dict, model_input_features_row,
                            yssy_obs_df, x_cols_for_model, plot_idx=""):
    """Plots observed data and forecasted future winds using individual models."""
    
    plot_start_time_obs = timestamp_anchor - timedelta(hours=24)
    plot_end_time_obs = timestamp_anchor + timedelta(hours=24)
    
    obs_slice = yssy_obs_df[
        (yssy_obs_df[YSSY_TIMESTAMP_COL] >= plot_start_time_obs) &
        (yssy_obs_df[YSSY_TIMESTAMP_COL] <= plot_end_time_obs)
    ].copy()

    if obs_slice.empty:
        print(f"Warning: No YSSY observation data found for anchor {timestamp_anchor} in the window {plot_start_time_obs} to {plot_end_time_obs}.")
        obs_times, obs_temp, obs_dewp, obs_u, obs_v = np.array([]), np.array([]), np.array([]), np.array([]), np.array([])
    else:
        obs_times = obs_slice[YSSY_TIMESTAMP_COL].values
        obs_temp = obs_slice.get('air_temp', pd.Series(np.nan, index=obs_slice.index)).values
        obs_dewp = obs_slice.get('dew_point', pd.Series(np.nan, index=obs_slice.index)).values
        obs_u = obs_slice.get('u_component', pd.Series(np.nan, index=obs_slice.index)).values
        obs_v = obs_slice.get('v_component', pd.Series(np.nan, index=obs_slice.index)).values
    
    obs_ws, obs_wd = uv_to_speed_direction(obs_u, obs_v)

    # --- Model Prediction ---
    future_times_forecast = [timestamp_anchor + timedelta(minutes=30 * i) for i in range(1, NUM_FORECAST_STEPS + 1)]
    
    X_sample = pd.DataFrame([model_input_features_row[x_cols_for_model]], columns=x_cols_for_model)
    
    pred_future_u, pred_future_v = get_predictions_from_individual_models(
        loaded_models_dict, X_sample, NUM_FORECAST_STEPS, TARGET_STATION_PREFIX
    )
    pred_future_ws, pred_future_wd = uv_to_speed_direction(pred_future_u, pred_future_v)

    # --- Plotting (remains largely the same) ---
    fig, ax1 = plt.subplots(figsize=(18, 10))
    fig.suptitle(f"YSSY Forecast (Anchor: {timestamp_anchor.strftime('%Y-%m-%d %H:%M')}) - Individual Models", fontsize=16)

    ax1.plot(obs_times, obs_temp, 'r-', label='Observed Temp (°C)', solid_capstyle='round', zorder=3)
    ax1.plot(obs_times, obs_dewp, 'b-', label='Observed Dewpoint (°C)', solid_capstyle='round', zorder=3)
    ax1.plot(obs_times, obs_ws, '-', color='gray', label='Observed Wind Speed (kt)', linewidth=3, solid_capstyle='round', zorder=3)
    
    # Plot forecasted Wind Speed (handle NaNs by not connecting gaps if any)
    # Plotting with NaNs will naturally create gaps if 'pred_future_ws' contains them.
    ax1.plot(future_times_forecast, pred_future_ws, '-', color='black', linewidth=4, label='Forecast Wind Speed (kt)', zorder=4)

    ax1.set_xlabel("Time")
    ax1.set_ylabel("Temperature (°C) / Wind Speed (knots)")
    ax1.tick_params(axis='y')
    ax1.grid(True, linestyle=':', alpha=0.7)

    ax1.yaxis.set_major_locator(mticker.MultipleLocator(5))
    all_ax1_data = np.concatenate([
        obs_temp[np.isfinite(obs_temp)], 
        obs_dewp[np.isfinite(obs_dewp)], 
        obs_ws[np.isfinite(obs_ws)], 
        pred_future_ws[np.isfinite(pred_future_ws)] # Only use non-NaN forecast values for limits
    ])
    ax1_bottom = 0
    ax1_top = 40
    ax1.set_ylim(ax1_bottom, ax1_top)

    ax2 = ax1.twinx()
    ax2.scatter(obs_times, obs_wd, marker='o', color='darkgray', s=50, label='Observed Wind Dir (°)', zorder=6)
    # For forecasted wind direction, NaNs in pred_future_wd will mean those points are not plotted by scatter.
    ax2.scatter(future_times_forecast, pred_future_wd, marker='X', color='black', s=70, linewidth=1, label='Forecast Wind Dir (°)', zorder=7)

    ax2.set_ylabel("Wind Direction (degrees from North)")
    ax2.set_ylim(0, 360)
    ax2.yaxis.set_major_locator(mticker.MultipleLocator(45))
    ax2.tick_params(axis='y')

    ax1.set_xlim(plot_start_time_obs, plot_end_time_obs)
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M\n%d-%b'))
    ax1.xaxis.set_major_locator(mdates.HourLocator(interval=2))
    plt.xticks(rotation=0, ha='center')
    ax1.axvline(timestamp_anchor, color='k', linestyle=':', linewidth=1, alpha=0.7, label='Forecast Anchor')

    lines, labels = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax2.legend(lines + lines2, labels + labels2, loc='upper center', bbox_to_anchor=(0.5, -0.15), ncol=3, frameon=False)

    plt.tight_layout(rect=[0, 0.05, 1, 0.95])
    
    plot_filename = PLOTS_OUTPUT_DIR / f"forecast_indiv_{timestamp_anchor.strftime('%Y%m%d_%H%M')}{plot_idx}.png"
    plt.savefig(plot_filename)
    print(f"Saved plot: {plot_filename}")
    plt.close(fig)

# --- Main Script ---
if __name__ == "__main__":
    # --- File Checks ---
    if not MODELS_DIR_BASE.exists():
        print(f"Error: Base directory for individual models not found at {MODELS_DIR_BASE}"); exit()
    if not TEST_DATA_FILE.exists():
        print(f"Error: Test data file not found at {TEST_DATA_FILE}"); exit()
    if not YSSY_OBS_FILE.exists():
        print(f"Error: YSSY observation file not found at {YSSY_OBS_FILE}"); exit()

    # --- Load Individual Models ---
    print(f"Loading individual models from {MODELS_DIR_BASE}...")
    loaded_models, model_feature_names = load_individual_models(MODELS_DIR_BASE)
    if not loaded_models:
        print("No models loaded. Exiting."); exit()
    
    # --- Load Test Data (for model input features and anchor times) ---
    print(f"Loading test data (for model inputs) from {TEST_DATA_FILE}...")
    test_df_features = pd.read_csv(TEST_DATA_FILE)
    test_df_features[TIMESTAMP_COL] = pd.to_datetime(test_df_features[TIMESTAMP_COL])
    print(f"Test data for features loaded. Shape: {test_df_features.shape}")

    # --- Load YSSY Full Observations Data ---
    print(f"Loading YSSY observation data from {YSSY_OBS_FILE}...")
    yssy_full_obs_df = pd.read_csv(YSSY_OBS_FILE)
    yssy_full_obs_df[YSSY_TIMESTAMP_COL] = pd.to_datetime(yssy_full_obs_df[YSSY_TIMESTAMP_COL])
    yssy_full_obs_df.set_index(YSSY_TIMESTAMP_COL, inplace=True, drop=False) # Keep original ts col
    yssy_full_obs_df.sort_index(inplace=True)
    print(f"YSSY observation data loaded. Shape: {yssy_full_obs_df.shape}")

    # --- Determine Feature Columns for Model Input ---
    # If we got feature names from a loaded model, use those.
    # Otherwise, assume all columns in test_df_features except TIMESTAMP_COL are features.
    if model_feature_names:
        X_COLUMN_ORDER = model_feature_names
        print(f"Using feature names from loaded model: {len(X_COLUMN_ORDER)} features.")
        # Sanity check if these features exist in test_df_features
        missing_model_features = [f for f in X_COLUMN_ORDER if f not in test_df_features.columns]
        if missing_model_features:
            print(f"CRITICAL ERROR: The following features expected by the model are MISSING from test_df_features: {missing_model_features}")
            exit()
    else:
        print("Warning: Could not get feature names from models. Inferring from test_data_file.")
        X_COLUMN_ORDER = [col for col in test_df_features.columns if col != TIMESTAMP_COL]
        print(f"Inferred feature order (all non-timestamp columns): {len(X_COLUMN_ORDER)} features.")


    # --- Plot for Random Samples ---
    num_random_samples = 1 # Reduced for quicker testing
    if len(test_df_features) == 0:
        print("Test data (for features) is empty. Cannot generate plots."); exit()
    
    if len(test_df_features) < num_random_samples:
        num_random_samples = len(test_df_features)
        print(f"Warning: Requested {num_random_samples} samples, but test set only has {len(test_df_features)}. Plotting all.")

    random_indices = random.sample(range(len(test_df_features)), num_random_samples)

    print(f"\nGenerating {num_random_samples} random sample plots...")
    for i, idx in enumerate(random_indices):
        model_input_row = test_df_features.iloc[idx]
        anchor_ts = model_input_row[TIMESTAMP_COL]
        
        print(f"\nPlotting for sample {i+1}/{num_random_samples}, anchor time: {anchor_ts}")
        plot_forecast_vs_actual(anchor_ts, loaded_models, model_input_row,
                                yssy_full_obs_df, X_COLUMN_ORDER, plot_idx=f"_rand{i+1}")
    
    # --- Plot for a Specific Time ---
    # Find a row in test_df_features that corresponds to this specific time, or close to it.
    # For this example, let's try to find the first available timestamp in test_df_features
    # or allow manual specification.
    
    # Example: Use the timestamp from the first random sample for the "manual" plot for simplicity
    # Or, you can hardcode a specific timestamp string here.
    if random_indices:
        # --- Configuration for the loop ---
        start_datetime_str = '2024-01-01 00:00:00'
        end_datetime_str = '2024-01-31 23:00:00' # The loop will include this time if it's on a 30-min interval

        # Ensure your TIMESTAMP_COL in test_df_features is already in datetime format
        # If not, convert it:
        # test_df_features[TIMESTAMP_COL] = pd.to_datetime(test_df_features[TIMESTAMP_COL])

        # --- Generate the time range ---
        try:
            start_dt = pd.to_datetime(start_datetime_str)
            end_dt = pd.to_datetime(end_datetime_str)
        except ValueError as e:
            print(f"Error parsing date strings: {e}")
            # Handle error appropriately, e.g., exit or raise
            raise

        # Generate timestamps at 30-minute intervals
        # 'T' or 'min' for minute frequency. '30T' or '30min' for 30 minutes.
        time_range = pd.date_range(start=start_dt, end=end_dt, freq='30T')

        if time_range.empty:
            print(f"Warning: The generated time range from {start_dt} to {end_dt} with 30-min frequency is empty.")
            print("Check if start_datetime_str is before or equal to end_datetime_str.")
        else:
            print(f"Generating plots for {len(time_range)} timestamps from {time_range[0]} to {time_range[-1]}")

            # --- Loop through the generated timestamps ---
            for current_anchor_ts in time_range:
                print(f"\nProcessing anchor timestamp: {current_anchor_ts}")

                # Find the target row in your features DataFrame
                # Ensure TIMESTAMP_COL in test_df_features is of datetime type for direct comparison
                target_row_df = test_df_features[test_df_features[TIMESTAMP_COL] == current_anchor_ts]

                if not target_row_df.empty:
                    # Get the first matching row (assuming timestamps are unique or you want the first)
                    specific_model_input_row = target_row_df.iloc[0]

                    # Create a unique plot_idx for each plot, e.g., by including the timestamp
                    plot_idx_suffix = current_anchor_ts.strftime('%Y%m%d_%H%M')
                    current_plot_idx = f"_auto_spec_{plot_idx_suffix}"

                    #print(f"  Found data. Calling plot_forecast_vs_actual with plot_idx: {current_plot_idx}")
                    plot_forecast_vs_actual(
                        current_anchor_ts,
                        loaded_models,
                        specific_model_input_row,
                        yssy_full_obs_df, # Renamed from yssy_full_obs_df for clarity in function call
                        X_COLUMN_ORDER, # Renamed from X_COLUMN_ORDER
                        current_plot_idx
                    )
                else:
                    print(f"  No data found in test_df_features for anchor timestamp: {current_anchor_ts}")

        print("\nFinished processing all timestamps in the range.")
        
    else:
        print("No random samples generated, cannot pick a specific time for manual plot based on them. Skipping.")
                                
    print(f"\nAll plots saved to: {PLOTS_OUTPUT_DIR.resolve()}")