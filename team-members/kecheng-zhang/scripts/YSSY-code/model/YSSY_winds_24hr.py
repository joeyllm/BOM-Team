# ----------------------------------
# Imports
# ----------------------------------
import pandas as pd
import numpy as np
import lightgbm as lgb
from sklearn.multioutput import MultiOutputRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error
import joblib
from pathlib import Path
import time # To measure training time

# ----------------------------------
# Configuration
# ----------------------------------
# --- Paths ---
DATA_DIR = Path("data24x0.1") # Assuming your data is in a subdir named 'data24x0.1'
TRAIN_FILE = DATA_DIR / "training_dataset.txt"
VAL_FILE = DATA_DIR / "validation_dataset.txt" # Validation set can be used for fit params if needed, or just for info
TEST_FILE = DATA_DIR / "test_dataset.txt"
OUTPUT_DIR = Path("output_quick_model")
MODEL_OUTPUT_FILE = OUTPUT_DIR / "yssy_multi_output_model_24hr_quick.joblib"

# --- Data Settings ---
TIMESTAMP_COL = "timestamp_t"
TARGET_PREFIXES = ("YSSY_u_forecast_t_plus_", "YSSY_v_forecast_t_plus_")
# For the 24hr forecast, targets will be t_plus_1 to t_plus_48
# YSSY_u_forecast_t_plus_1, YSSY_v_forecast_t_plus_1, ..., YSSY_u_forecast_t_plus_48, YSSY_v_forecast_t_plus_48

# --- Model Training Settings ---
TRAIN_DATA_SUBSAMPLE_FRACTION = 0.1 # Use 10% of training data for a quick run. Set to 1.0 for full.
# Consider starting with a smaller fraction (e.g., 0.01 or 0.05) if 10% is still too slow for the very first test.

# Fixed LightGBM Hyperparameters (Example - these may need tuning for optimal performance)
# These are just illustrative. You'll likely want to adjust based on previous experience or a quick HP search.
FIXED_LGBM_PARAMS = {
    'objective': 'regression_l2', # MSE
    'metric': 'l2',               # MSE
    'n_estimators': 10,          # Number of boosting rounds
    'learning_rate': 0.05,
    'num_leaves': 10,             # Max number of leaves in one tree
    'max_depth': 10,              # Max tree depth
    'min_child_samples': 10,      # Min number of data in one leaf
    'subsample': 0.8,             # Fraction of samples for training each tree
    'colsample_bytree': 0.7,      # Fraction of features for training each tree
    'reg_alpha': 0.5,             # L1 regularization
    'reg_lambda': 0.1,            # L2 regularization
    'random_state': 42,
    'n_jobs': -1,                 # Use all available cores
    'verbose': 10                 # Suppress LightGBM's own verbose output
}

# ----------------------------------
# Utility Functions
# ----------------------------------
def save_artifact(obj, path):
    """Saves an object (model, dict, etc.) to a file using joblib."""
    path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(obj, path)
    print(f"Artifact saved to {path}")

# ----------------------------------
# Data Handling Function
# ----------------------------------
def load_and_split_data(file_path, ts_col, target_prefixes, subsample_frac=1.0):
    """
    Loads data, identifies features (X) and targets (Y) based on column names.
    The timestamp column is also identified. Any columns not timestamp or target are features.
    """
    print(f"Loading data from: {file_path} (subsample: {subsample_frac*100:.1f}%)")
    start_time = time.time()
    df = pd.read_csv(file_path)
    load_time = time.time() - start_time
    print(f"  Loaded {len(df)} rows in {load_time:.2f} seconds.")

    # Identify target columns
    target_cols = [col for col in df.columns if col.startswith(target_prefixes)]
    # Ensure correct sorting: u_t+1, v_t+1, u_t+2, v_t+2, ...
    target_cols = sorted(target_cols, key=lambda x: (int(x.split('_t_plus_')[-1]), x.split('_')[1]))
    
    print(f"  Identified {len(target_cols)} target columns (e.g., {target_cols[:4]}...).")

    # Identify feature columns (anything not a target or the timestamp column)
    potential_feature_cols = [col for col in df.columns if col != ts_col and col not in target_cols]
    print(f"  Identified {len(potential_feature_cols)} potential input feature columns.")
    
    y = df[target_cols].copy()
    X = df[potential_feature_cols].copy()
    timestamps = pd.to_datetime(df[ts_col]) if ts_col in df.columns else None

    if subsample_frac < 1.0 and subsample_frac > 0:
        print(f"  Subsampling data to {subsample_frac*100:.1f}%.")
        X = X.sample(frac=subsample_frac, random_state=42)
        y = y.loc[X.index]
        if timestamps is not None:
            timestamps = timestamps.loc[X.index]
        print(f"  Subsampled X shape: {X.shape}, y shape: {y.shape}")
    
    print(f"  Final X shape: {X.shape}, y shape: {y.shape}")
    if timestamps is not None:
        print(f"  Timestamps shape: {timestamps.shape}")
    return X, y, timestamps, target_cols # Return target_cols for evaluation reference

# ----------------------------------
# Main Execution Block
# ----------------------------------
if __name__ == "__main__":
    # --- 0. Setup ---
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Output will be saved to: {OUTPUT_DIR.resolve()}")

    # --- 1. Load Data ---
    # We only need headers from one file to get column structure consistently
    # For this simplified version, load_and_split_data will handle it per file.
    
    print("\n--- Loading Training Data ---")
    X_train, y_train, _, train_target_names = load_and_split_data(
        TRAIN_FILE,
        ts_col=TIMESTAMP_COL,
        target_prefixes=TARGET_PREFIXES,
        subsample_frac=TRAIN_DATA_SUBSAMPLE_FRACTION
    )

    # Validation data can be used if you want to monitor performance during training with LightGBM's fit params
    # For a MultiOutputRegressor, this is a bit more complex to set up for each estimator.
    # For this quick script, we'll skip using validation set during fit, but load it for info.
    print("\n--- Loading Validation Data ---")
    X_val, y_val, _, _ = load_and_split_data(
        VAL_FILE,
        ts_col=TIMESTAMP_COL,
        target_prefixes=TARGET_PREFIXES,
        subsample_frac=1.0 # Usually no subsampling for validation/test
    )

    print("\n--- Loading Test Data ---")
    X_test, y_test, ts_test, test_target_names = load_and_split_data(
        TEST_FILE,
        ts_col=TIMESTAMP_COL,
        target_prefixes=TARGET_PREFIXES,
        subsample_frac=1.0 # No subsampling for test
    )
    
    # Ensure consistent feature columns between train and test (if subsetting or different files might cause issues)
    # This is a basic check; more robust handling might be needed if columns truly differ.
    if not X_train.columns.equals(X_test.columns):
        print("Warning: Training and Test set feature columns do not match. This could be an issue.")
        # For simplicity, we'll assume they are consistent due to your data prep.
        # A more robust solution would involve aligning columns.
        
    # --- 2. Define Model & Train ---
    print("\n--- Model Training ---")
    base_lgbm = lgb.LGBMRegressor(**FIXED_LGBM_PARAMS)
    model = MultiOutputRegressor(base_lgbm, n_jobs=-1) # n_jobs here for MultiOutputRegressor if estimators are parallelizable

    print(f"Training MultiOutputRegressor with LightGBM using fixed parameters:")
    for k, v in FIXED_LGBM_PARAMS.items():
        print(f"  {k}: {v}")
    print(f"Training on {X_train.shape[0]} samples and {X_train.shape[1]} features for {y_train.shape[1]} targets.")

    training_start_time = time.time()
    model.fit(X_train, y_train) # For MultiOutputRegressor, early stopping per estimator is not straightforward
    training_time = time.time() - training_start_time
    print(f"Training complete. Time taken: {training_time:.2f} seconds ({training_time/60:.2f} minutes).")

    # --- 3. Save Model ---
    print("\n--- Saving Model ---")
    save_artifact(model, MODEL_OUTPUT_FILE)

    # --- 4. Evaluate Model ---
    if not X_test.empty:
        print("\n--- Model Evaluation on Test Set ---")
        preds_test = model.predict(X_test)

        overall_mse_test = mean_squared_error(y_test, preds_test)
        overall_mae_test = mean_absolute_error(y_test, preds_test)
        print(f"Overall Test MSE: {overall_mse_test:.4f}")
        print(f"Overall Test MAE: {overall_mae_test:.4f}")

        # Optional: Per-target metrics for a few targets
        print("\nPer-target metrics for a few example targets (first 4 and last 4):")
        targets_to_show = test_target_names[:4] + test_target_names[-4:]
        for i, target_name in enumerate(test_target_names):
            if target_name in targets_to_show :
                col_idx = y_test.columns.get_loc(target_name)
                mae = mean_absolute_error(y_test.iloc[:, col_idx], preds_test[:, col_idx])
                mse = mean_squared_error(y_test.iloc[:, col_idx], preds_test[:, col_idx])
                print(f"  {target_name}: MAE={mae:.4f}, MSE={mse:.4f}")
    else:
        print("\nTest set is empty. Skipping evaluation.")

    print("\n--- Workflow Complete ---")
    print(f"Trained model saved to: {MODEL_OUTPUT_FILE}")
    print(f"Consider using this model with your separate visualization program.")