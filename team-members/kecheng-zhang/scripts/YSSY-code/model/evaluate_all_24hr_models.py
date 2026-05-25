import pandas as pd
import numpy as np
import joblib
from pathlib import Path
from sklearn.metrics import mean_squared_error, mean_absolute_error
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

# --- Configuration ---
MODELS_DIR_BASE = Path("output_final_models") # Base directory where u_models and v_models are
TEST_DATA_FILE = Path("data24") / "test_dataset.txt"
EVALUATION_OUTPUT_DIR = Path("output_model_evaluation_full1.0_MSE_OCTOBER")
EVALUATION_OUTPUT_DIR.mkdir(exist_ok=True, parents=True)

TIMESTAMP_COL = "timestamp_t"
TARGET_STATION_PREFIX = "YSSY"
NUM_FORECAST_STEPS = 48 # t+1 to t+48

# --- Helper Functions ---
def load_individual_models_and_features(models_base_dir):
    """Loads all .joblib models and attempts to get feature names."""
    loaded_models = {}
    feature_names_from_model = None
    models_found_count = 0
    
    for component in ['u', 'v']:
        component_dir = models_base_dir / f"{component}_models"
        if not component_dir.exists():
            print(f"Info: Directory not found, skipping: {component_dir}")
            continue
            
        model_files = sorted(list(component_dir.glob("*.joblib"))) # Sort for consistent order if needed
        
        for model_file in model_files:
            target_name = model_file.stem
            try:
                model_obj = joblib.load(model_file)
                loaded_models[target_name] = model_obj
                models_found_count += 1
                # print(f"  Loaded: {target_name}") # Can be verbose

                if feature_names_from_model is None:
                    if hasattr(model_obj, 'feature_name_'):
                        feature_names_from_model = model_obj.feature_name_
                    elif hasattr(model_obj, 'booster_') and hasattr(model_obj.booster_, 'feature_name'):
                         feature_names_from_model = model_obj.booster_.feature_name()
            except Exception as e:
                print(f"Error loading model {model_file}: {e}")
    
    print(f"Total models loaded: {models_found_count}")
    if feature_names_from_model is None and loaded_models:
        print("Warning: Could not extract feature names from any loaded model.")
        
    return loaded_models, feature_names_from_model

def make_predictions_with_all_models(loaded_models_dict, X_test_df, num_fcst_steps, station_prefix):
    """
    Generates predictions for all 96 targets using individual models.
    Returns a DataFrame of predictions.
    """
    all_predictions = {}
    num_samples = len(X_test_df)

    for step in range(1, num_fcst_steps + 1):
        for component_letter in ['u', 'v']:
            target_name = f"{station_prefix}_{component_letter}_forecast_t_plus_{step}"
            
            if target_name in loaded_models_dict:
                model = loaded_models_dict[target_name]
                # Predict for all samples in X_test_df at once
                all_predictions[target_name] = model.predict(X_test_df)
            else:
                # Fill with NaNs if model is missing
                all_predictions[target_name] = np.full(num_samples, np.nan)
                print(f"Warning: Model for {target_name} not found. Predictions will be NaN.")
                
    return pd.DataFrame(all_predictions)

# --- Main Script ---
if __name__ == "__main__":
    # --- File Checks ---
    if not MODELS_DIR_BASE.exists():
        print(f"Error: Base directory for individual models not found: {MODELS_DIR_BASE}"); exit()
    if not TEST_DATA_FILE.exists():
        print(f"Error: Test data file not found: {TEST_DATA_FILE}"); exit()

    # --- 1. Load Individual Models ---
    print(f"Loading individual models from {MODELS_DIR_BASE}...")
    loaded_models, model_feature_names = load_individual_models_and_features(MODELS_DIR_BASE)
    if not loaded_models:
        print("No models loaded. Exiting."); exit()

    # --- 2. Load Test Data ---
    print(f"Loading test data from {TEST_DATA_FILE}...")
    test_df_full = pd.read_csv(TEST_DATA_FILE)
    # test_df_full[TIMESTAMP_COL] = pd.to_datetime(test_df_full[TIMESTAMP_COL]) # Timestamps not strictly needed for X,y
    print(f"Test data loaded. Shape: {test_df_full.shape}")

    # --- 3. Prepare X_test and y_test ---
    # Determine feature columns (X)
    if model_feature_names:
        X_test = test_df_full[model_feature_names]
        print(f"Using feature names from loaded model for X_test: {len(model_feature_names)} features.")
        missing_features = [f for f in model_feature_names if f not in test_df_full.columns]
        if missing_features:
            print(f"CRITICAL ERROR: Model features missing from test data: {missing_features}"); exit()
    else:
        # Infer feature columns: all columns NOT starting with TARGET_STATION_PREFIX and NOT TIMESTAMP_COL
        print("Warning: Inferring feature names for X_test (all non-target, non-timestamp columns).")
        potential_target_cols = [col for col in test_df_full.columns if col.startswith(TARGET_STATION_PREFIX)]
        feature_cols_inferred = [
            col for col in test_df_full.columns if col != TIMESTAMP_COL and col not in potential_target_cols
        ]
        X_test = test_df_full[feature_cols_inferred]
        print(f"Inferred X_test feature count: {len(feature_cols_inferred)}.")

    # Determine target columns (y)
    y_test_cols = []
    for step in range(1, NUM_FORECAST_STEPS + 1):
        y_test_cols.append(f"{TARGET_STATION_PREFIX}_u_forecast_t_plus_{step}")
        y_test_cols.append(f"{TARGET_STATION_PREFIX}_v_forecast_t_plus_{step}")
    
    # Check if all expected target columns exist in test_df_full
    missing_y_cols = [col for col in y_test_cols if col not in test_df_full.columns]
    if missing_y_cols:
        print(f"CRITICAL ERROR: Expected target columns missing from test data: {missing_y_cols}")
        print("Ensure your test_dataset.txt contains all 96 target forecast columns.")
        exit()
    y_test = test_df_full[y_test_cols]
    
    print(f"X_test shape: {X_test.shape}, y_test shape: {y_test.shape}")

    # --- 4. Make Predictions ---
    print("\nMaking predictions with loaded models...")
    predictions_df = make_predictions_with_all_models(
        loaded_models, X_test, NUM_FORECAST_STEPS, TARGET_STATION_PREFIX
    )
    # Ensure predictions_df columns are in the same order as y_test for direct comparison
    predictions_df = predictions_df[y_test.columns] 
    print(f"Predictions generated. Shape: {predictions_df.shape}")

    # --- 5. Calculate Metrics ---
    metrics_data = []
    overall_mae_sum = 0
    overall_mse_sum = 0
    num_valid_targets_for_overall = 0 # Count targets for which we have predictions

    for step in range(1, NUM_FORECAST_STEPS + 1):
        target_u = f"{TARGET_STATION_PREFIX}_u_forecast_t_plus_{step}"
        target_v = f"{TARGET_STATION_PREFIX}_v_forecast_t_plus_{step}"

        actual_u = y_test[target_u]
        pred_u = predictions_df[target_u]
        actual_v = y_test[target_v]
        pred_v = predictions_df[target_v]

        # Check if predictions are all NaN (model was missing)
        has_pred_u = not pred_u.isnull().all()
        has_pred_v = not pred_v.isnull().all()

        mae_u, mse_u, mae_v, mse_v = np.nan, np.nan, np.nan, np.nan
        
        if has_pred_u:
            mae_u = mean_absolute_error(actual_u, pred_u)
            mse_u = mean_squared_error(actual_u, pred_u)
            overall_mae_sum += mae_u
            overall_mse_sum += mse_u
            num_valid_targets_for_overall +=1
        
        if has_pred_v:
            mae_v = mean_absolute_error(actual_v, pred_v)
            mse_v = mean_squared_error(actual_v, pred_v)
            overall_mae_sum += mae_v
            overall_mse_sum += mse_v
            num_valid_targets_for_overall +=1

        avg_mae_step = np.nanmean([mae_u, mae_v]) if (has_pred_u or has_pred_v) else np.nan
        avg_mse_step = np.nanmean([mse_u, mse_v]) if (has_pred_u or has_pred_v) else np.nan
        
        metrics_data.append({
            "Lead Time (t+)": step,
            "MAE_u": mae_u, "MSE_u": mse_u,
            "MAE_v": mae_v, "MSE_v": mse_v,
            "Avg_MAE_step": avg_mae_step,
            "Avg_MSE_step": avg_mse_step
        })

    metrics_df = pd.DataFrame(metrics_data)
    
    # --- 6. Display and Save Metrics Table ---
    print("\n--- Per-Step Model Evaluation Metrics ---")
    # Format for display
    metrics_display_df = metrics_df.copy()
    for col in metrics_display_df.columns:
        if col != "Lead Time (t+)":
            metrics_display_df[col] = metrics_display_df[col].map(lambda x: f"{x:.4f}" if pd.notnull(x) else "N/A")
    
    print(metrics_display_df.to_string(index=False))
    
    metrics_table_file = EVALUATION_OUTPUT_DIR / "per_step_evaluation_metrics.txt"
    with open(metrics_table_file, "w") as f:
        f.write("Per-Step Model Evaluation Metrics:\n")
        f.write(metrics_display_df.to_string(index=False))
        f.write("\n\n")

        if num_valid_targets_for_overall > 0:
            final_overall_mae = overall_mae_sum / num_valid_targets_for_overall
            final_overall_mse = overall_mse_sum / num_valid_targets_for_overall
            print(f"\n--- Overall Average Metrics (across {num_valid_targets_for_overall} available targets) ---")
            print(f"Overall Average MAE: {final_overall_mae:.4f}")
            print(f"Overall Average MSE: {final_overall_mse:.4f}")
            f.write(f"Overall Average MAE (across {num_valid_targets_for_overall} available targets): {final_overall_mae:.4f}\n")
            f.write(f"Overall Average MSE (across {num_valid_targets_for_overall} available targets): {final_overall_mse:.4f}\n")
        else:
            print("\nNo valid targets with predictions found to calculate overall average metrics.")
            f.write("No valid targets with predictions found to calculate overall average metrics.\n")

    print(f"\nMetrics table saved to: {metrics_table_file}")

    # --- 7. Generate Plot ---
    if not metrics_df.empty:
        # Create two subplots, side by side
        fig, (ax_mae, ax_mse) = plt.subplots(1, 2, figsize=(22, 8)) # Increased figure size
        
        lead_time_steps_hours = metrics_df["Lead Time (t+)"] * 0.5 # Convert steps to hours

        # --- MAE Subplot (Left) ---
        ax_mae.set_xlabel('Forecast Lead Time (hours)')
        ax_mae.set_ylabel('Mean Absolute Error (MAE)')
        
        # U-component MAE (Red, Dashed)
        ax_mae.plot(lead_time_steps_hours, metrics_df["MAE_u"], color='red', linestyle='--', marker='o', markersize=4, label='MAE U-Component')
        # V-component MAE (Blue, Dashed)
        ax_mae.plot(lead_time_steps_hours, metrics_df["MAE_v"], color='blue', linestyle='--', marker='s', markersize=4, label='MAE V-Component')
        # Average MAE (Black, Solid, Thicker)
        ax_mae.plot(lead_time_steps_hours, metrics_df["Avg_MAE_step"], color='black', linestyle='-', marker='x', markersize=5, linewidth=2.5, label='Avg MAE (U & V)')
        
        ax_mae.grid(True, linestyle=':', alpha=0.7)
        ax_mae.tick_params(axis='y')
        ax_mae.set_xticks(np.arange(0, NUM_FORECAST_STEPS * 0.5 + 0.5, 2)) # Ticks every 2 hours
        ax_mae.set_title('MAE vs. Forecast Lead Time', fontsize=14)
        # Optional: Set y-limits for MAE if needed, e.g., 
        ax_mae.set_ylim(bottom=0)

        # --- MSE Subplot (Right) ---
        ax_mse.set_xlabel('Forecast Lead Time (hours)')
        ax_mse.set_ylabel('Mean Squared Error (MSE)')

        # U-component MSE (Red, Dashed)
        ax_mse.plot(lead_time_steps_hours, metrics_df["MSE_u"], color='red', linestyle='--', marker='o', markersize=4, label='MSE U-Component')
        # V-component MSE (Blue, Dashed)
        ax_mse.plot(lead_time_steps_hours, metrics_df["MSE_v"], color='blue', linestyle='--', marker='s', markersize=4, label='MSE V-Component')
        # Average MSE (Black, Solid, Thicker)
        ax_mse.plot(lead_time_steps_hours, metrics_df["Avg_MSE_step"], color='black', linestyle='-', marker='x', markersize=5, linewidth=2.5, label='Avg MSE (U & V)')

        ax_mse.grid(True, linestyle=':', alpha=0.7)
        ax_mse.tick_params(axis='y')
        ax_mse.set_xticks(np.arange(0, NUM_FORECAST_STEPS * 0.5 + 0.5, 2)) # Ticks every 2 hours
        ax_mse.set_title('MSE vs. Forecast Lead Time', fontsize=14)
        # Optional: Set y-limits for MSE if needed, e.g., 
        ax_mse.set_ylim(bottom=0)

        # --- Overall Figure Settings ---
        fig.suptitle('Model Performance vs. Forecast Lead Time', fontsize=18, y=0.98) # y to adjust title position
        
        # Create a single legend for the entire figure
        # Get handles and labels from one of the axes (they should be the same for both if plotting all lines)
        handles, labels = [], []
        for ax in [ax_mae, ax_mse]: # Collect unique legend items
            for h, l in zip(*ax.get_legend_handles_labels()):
                if l not in labels:
                    labels.append(l)
                    handles.append(h)
        
        # Sort legend items to group U, V, Avg if desired, or keep as collected
        # Example: Custom sort order
        desired_order = ['MAE U-Component', 'MSE U-Component', 
                         'MAE V-Component', 'MSE V-Component',
                         'Avg MAE (U & V)', 'Avg MSE (U & V)']
        # Filter and reorder handles and labels based on what's actually plotted
        # This is a bit more robust if not all lines are always present
        ordered_handles = []
        ordered_labels = []
        
        # Get all unique labels plotted
        all_plotted_labels = []
        temp_handles, temp_labels = ax_mae.get_legend_handles_labels()
        all_plotted_labels.extend(temp_labels)
        temp_handles_mse, temp_labels_mse = ax_mse.get_legend_handles_labels()
        all_plotted_labels.extend(temp_labels_mse)
        unique_plotted_labels = sorted(list(set(all_plotted_labels)))


        # Create a dictionary for easy lookup
        handle_label_map = {}
        for h, l in zip(*ax_mae.get_legend_handles_labels()): handle_label_map[l] = h
        for h, l in zip(*ax_mse.get_legend_handles_labels()): handle_label_map[l] = h # Overwrite if same label, should be fine

        # Build legend items in a specific order if desired, or just use unique_plotted_labels
        # For simplicity, let's just use the unique plotted labels as collected
        final_legend_handles = [handle_label_map[l] for l in unique_plotted_labels if l in handle_label_map]
        final_legend_labels = [l for l in unique_plotted_labels if l in handle_label_map]


        fig.legend(final_legend_handles, final_legend_labels, loc='upper center', bbox_to_anchor=(0.5, 0.03), ncol=3, frameon=False) # Adjusted y for legend
        
        plt.tight_layout(rect=[0, 0.06, 1, 0.94]) # Adjust layout: left, bottom, right, top
        
        plot_file = EVALUATION_OUTPUT_DIR / "performance_vs_lead_time_subplots.png"
        plt.savefig(plot_file)
        print(f"Performance plot saved to: {plot_file}")
        plt.show() # Display the plot
    else:
        print("Metrics DataFrame is empty, skipping plot generation.")

    print(f"\nEvaluation complete. Outputs are in: {EVALUATION_OUTPUT_DIR.resolve()}")