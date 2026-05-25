# ----------------------------------
# Imports
# ----------------------------------
import pandas as pd
import numpy as np
import lightgbm as lgb
from sklearn.metrics import mean_squared_error # For optional evaluation after training
import joblib
from pathlib import Path
import time
import json
import argparse

# ----------------------------------
# Configuration
# ----------------------------------
# --- Paths ---
DATA_DIR = Path("data24")
TRAIN_FILE = DATA_DIR / "training_dataset.txt"
VAL_FILE = DATA_DIR / "validation_dataset.txt" # Validation set for early stopping
OUTPUT_DIR_BASE = Path("output_final_models") # Base directory for final models

# --- Data Settings ---
TIMESTAMP_COL = "timestamp_t"
TARGET_STATION_PREFIX = "YSSY" # e.g., YSSY_u_forecast_t_plus_1

# --- Model Training Settings ---
# These are the hyperparameters you decided on from your tuning phase.
# PASTE YOUR CHOSEN HYPERPARAMETERS HERE:
# Example:
CHOSEN_HYPERPARAMETERS = {
    "learning_rate": 0.025,
    "num_leaves": 300,
    "max_depth": 40,
    "min_child_samples": 150,
    "subsample": 0.8,
    "colsample_bytree": 0.7,
    "reg_alpha": 0.1,
    "reg_lambda": 0.1,
    # IMPORTANT: n_estimators will be set high, early stopping determines the actual number.
    # The 'best_iteration_' from tuning is a good reference but might change with full data.
    "n_estimators_max": 4000, # Max estimators for final fit, early stopping will choose
    "objective": "regression_l2",
    "metric": "l2",
    "random_state": 42,
    "n_jobs": -1,
    "verbose": -1
}
CHOSEN_HYPERPARAMETERS = {
    "learning_rate": 0.01,
    "num_leaves": 300,
    "max_depth": 40,
    "min_child_samples": 100,
    "subsample": 0.7,
    "colsample_bytree": 0.7,
    "reg_alpha": 0.5,
    "reg_lambda": 0.1,
    # IMPORTANT: n_estimators will be set high, early stopping determines the actual number.
    # The 'best_iteration_' from tuning is a good reference but might change with full data.
    "n_estimators_max": 4000, # Max estimators for final fit, early stopping will choose
    "objective": "regression_l2",
    "metric": "l2",
    "random_state": 42,
    "n_jobs": -1,
    "verbose": -1
}
# CHOSEN_HYPERPARAMETERS = {
#     "learning_rate": 0.018,
#     "num_leaves": 300,
#     "max_depth": 40,
#     "min_child_samples": 120,
#     "subsample": 0.75,
#     "colsample_bytree": 0.7,
#     "reg_alpha": 0.2,
#     "reg_lambda": 0.1,
#     # IMPORTANT: n_estimators will be set high, early stopping determines the actual number.
#     # The 'best_iteration_' from tuning is a good reference but might change with full data.
#     "n_estimators_max": 4000, # Max estimators for final fit, early stopping will choose
#     "objective": "regression_l2",
#     "metric": "l2",
#     "random_state": 42,
#     "n_jobs": -1,
#     "verbose": -1
# }

EARLY_STOPPING_ROUNDS_FINAL_FIT = 50
LGBM_FIT_VERBOSE_PERIOD_FINAL = 250  # Print evaluation metric every N boosting rounds

# ----------------------------------
# Utility Functions
# ----------------------------------
def save_model_artifact(model_obj, path):
    """Saves a model object to a file using joblib."""
    path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model_obj, path)
    print(f"Model saved to {path}")

def load_json_artifact(path):
    """Loads a dictionary from a JSON file."""
    with open(path, 'r') as f:
        data_dict = json.load(f)
    print(f"Loaded JSON from {path}")
    return data_dict

# ----------------------------------
# Data Handling Function
# ----------------------------------
def load_data_for_single_target_final(
    train_file_path, val_file_path, target_col_name, ts_col
):
    """
    Loads FULL train and validation data, extracts the specified single target column,
    and prepares X, y_single for training and validation.
    Identifies feature columns based on all columns minus timestamp and all potential targets.
    """
    print(f"\n--- Loading Full Data for Target: {target_col_name} ---")
    
    # Determine all possible target column names to identify feature columns
    # This is a bit more robust if we don't hardcode prefixes everywhere
    temp_df_cols = pd.read_csv(train_file_path, nrows=0).columns
    all_possible_target_cols = sorted(
        [col for col in temp_df_cols if col.startswith(f"{TARGET_STATION_PREFIX}_u_forecast_t_plus_") or \
                                        col.startswith(f"{TARGET_STATION_PREFIX}_v_forecast_t_plus_")],
        key=lambda x: (int(x.split('_t_plus_')[-1]), x.split('_')[1])
    )
    
    feature_cols = [col for col in temp_df_cols if col != ts_col and col not in all_possible_target_cols]

    # Load Training Data (Full)
    print(f"Loading training data from: {train_file_path}")
    df_train = pd.read_csv(train_file_path)
    if target_col_name not in df_train.columns:
        raise ValueError(f"Target column '{target_col_name}' not found in training data columns.")
    
    X_train = df_train[feature_cols]
    y_train_single = df_train[target_col_name]
    print(f"  Train X shape: {X_train.shape}, y_single shape: {y_train_single.shape}")

    # Load Validation Data (Full)
    print(f"Loading validation data from: {val_file_path}")
    df_val = pd.read_csv(val_file_path)
    if target_col_name not in df_val.columns:
        raise ValueError(f"Target column '{target_col_name}' not found in validation data columns.")
    
    X_val = df_val[feature_cols] # Assuming val features match train features
    y_val_single = df_val[target_col_name]
    print(f"  Validation X shape: {X_val.shape}, y_single shape: {y_val_single.shape}")
    
    return X_train, y_train_single, X_val, y_val_single

# ----------------------------------
# Main Execution Block
# ----------------------------------
if __name__ == "__main__":
    # parser = argparse.ArgumentParser(description="Train individual LightGBM models for specified wind components.")
    # parser.add_argument("component", type=str, choices=['u', 'v'], help="Wind component to train models for ('u' or 'v').")
    
    # args = parser.parse_args()
    COMPONENT_TO_TRAIN = "u"

    print(f"--- Starting Final Model Training ---")
    print(f"Component to train: {COMPONENT_TO_TRAIN}")
    print(f"Base output directory: {OUTPUT_DIR_BASE.resolve()}")
    print("Using fixed hyperparameters (excluding n_estimators, determined by early stopping):")
    for k, v in CHOSEN_HYPERPARAMETERS.items():
        if k != "n_estimators_max":
            print(f"  {k}: {v}")
    print(f"  Max n_estimators for fit: {CHOSEN_HYPERPARAMETERS['n_estimators_max']}")
    print(f"  Early stopping rounds: {EARLY_STOPPING_ROUNDS_FINAL_FIT}")

    # Create specific output subfolder for the component
    component_output_dir = OUTPUT_DIR_BASE / f"{COMPONENT_TO_TRAIN}_models"
    component_output_dir.mkdir(parents=True, exist_ok=True)
    print(f"Models for '{COMPONENT_TO_TRAIN}' will be saved to: {component_output_dir.resolve()}")

    targets_trained_count = 0
    total_training_time = 0

    for step in range(47, 49):
        target_col_name = f"{TARGET_STATION_PREFIX}_{COMPONENT_TO_TRAIN}_forecast_t_plus_{step}"
        
        print(f"\n======================================================================")
        print(f"Training model for: {target_col_name} (Step {step} for component '{COMPONENT_TO_TRAIN}')")
        print(f"======================================================================")
        
        fit_start_time = time.time()
        # --- 1. Load Data for the current target ---
        try:
            X_train, y_train_single, X_val, y_val_single = load_data_for_single_target_final(
                TRAIN_FILE, VAL_FILE, target_col_name, TIMESTAMP_COL
            )
        except ValueError as e:
            print(f"Error loading data for {target_col_name}: {e}. Skipping this target.")
            continue # Skip to the next target if data loading fails

        # --- 2. Prepare Model Parameters ---
        # Use a copy to avoid modifying the global dict if needed later
        current_model_params = CHOSEN_HYPERPARAMETERS.copy()
        # The 'n_estimators' key for LGBMRegressor is what we set high
        current_model_params['n_estimators'] = current_model_params.pop('n_estimators_max') 

        # --- 3. Train Model ---
        model = lgb.LGBMRegressor(**current_model_params)
        
        print(f"Fitting model for {target_col_name}...")
        
        callbacks_final_fit = [
            lgb.early_stopping(stopping_rounds=EARLY_STOPPING_ROUNDS_FINAL_FIT, verbose=False),
            lgb.log_evaluation(period=LGBM_FIT_VERBOSE_PERIOD_FINAL)
        ]

        model.fit(
            X_train, y_train_single,
            eval_set=[(X_val, y_val_single)],
            eval_metric=CHOSEN_HYPERPARAMETERS.get('metric', 'l2'), # Use metric from HPs
            callbacks=callbacks_final_fit
        )
        fit_duration = time.time() - fit_start_time
        total_training_time += fit_duration
        
        print(f"Training for {target_col_name} complete in {fit_duration:.2f}s. Best iteration: {model.best_iteration_}")

        # --- 4. Save Trained Model ---
        model_output_file = component_output_dir / f"{target_col_name}.joblib"
        save_model_artifact(model, model_output_file)
        
        # Optional: Store best_iteration_ if you want to log it
        # For example, in a summary JSON file later
        
        targets_trained_count += 1

    print(f"\n--- All Specified Model Training Complete for Component '{COMPONENT_TO_TRAIN}' ---")
    print(f"Successfully trained and saved {targets_trained_count} models.")
    print(f"Total training time for this run: {total_training_time:.2f} seconds ({total_training_time/60:.2f} minutes).")
    print(f"Models are saved in: {component_output_dir.resolve()}")