# ----------------------------------
# Imports
# ----------------------------------
import pandas as pd
import numpy as np
import lightgbm as lgb
from sklearn.metrics import mean_squared_error
import optuna
import joblib
from pathlib import Path
import time
import json
import argparse # For command-line arguments

# ----------------------------------
# Configuration (Defaults - can be overridden by CLI args)
# ----------------------------------
# --- Paths ---
DATA_DIR = Path("data24")
TRAIN_FILE = DATA_DIR / "training_dataset.txt"
VAL_FILE = DATA_DIR / "validation_dataset.txt"
OUTPUT_DIR = Path("output_tuned_hps") # Directory to save tuned HPs

# --- Data Settings ---
TIMESTAMP_COL = "timestamp_t"
TARGET_PREFIXES = ("YSSY_u_forecast_t_plus_", "YSSY_v_forecast_t_plus_")

# --- Optuna/LGBM Settings ---
DEFAULT_TRAIN_SUBSAMPLE_FRACTION = 0.1 # Default if not provided by CLI
DEFAULT_OPTUNA_N_TRIALS = 10          # Default if not provided by CLI
EARLY_STOPPING_ROUNDS = 50            # For LightGBM early stopping
LGBM_FIT_VERBOSE_PERIOD = 50         # Print evaluation metric every N boosting rounds during fit

# ----------------------------------
# Utility Functions
# ----------------------------------
def save_json_artifact(data_dict, path):
    """Saves a dictionary to a JSON file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w') as f:
        json.dump(data_dict, f, indent=4)
    print(f"JSON artifact saved to {path}")

# ----------------------------------
# Data Handling Function
# ----------------------------------
def load_and_prepare_single_target_data(
    train_file_path, val_file_path, target_col_name, ts_col, target_prefixes,
    train_subsample_frac=1.0
):
    """
    Loads train and validation data, extracts the specified single target column,
    and prepares X, y_single for training and validation.
    """
    print(f"\n--- Loading and Preparing Data for Target: {target_col_name} ---")
    
    # Load Training Data
    print(f"Loading training data from: {train_file_path} (subsample: {train_subsample_frac*100:.1f}%)")
    df_train = pd.read_csv(train_file_path)
    all_target_cols = sorted(
        [col for col in df_train.columns if col.startswith(target_prefixes)],
        key=lambda x: (int(x.split('_t_plus_')[-1]), x.split('_')[1])
    )
    if target_col_name not in df_train.columns:
        raise ValueError(f"Target column '{target_col_name}' not found in training data columns: {df_train.columns.tolist()}")

    feature_cols = [col for col in df_train.columns if col != ts_col and col not in all_target_cols]
    
    X_train_full = df_train[feature_cols]
    y_train_single_full = df_train[target_col_name]

    if 0 < train_subsample_frac < 1.0:
        X_train = X_train_full.sample(frac=train_subsample_frac, random_state=42)
        y_train_single = y_train_single_full.loc[X_train.index]
    else:
        X_train = X_train_full
        y_train_single = y_train_single_full
    print(f"  Train X shape: {X_train.shape}, y_single shape: {y_train_single.shape}")

    # Load Validation Data
    print(f"Loading validation data from: {val_file_path}")
    df_val = pd.read_csv(val_file_path)
    if target_col_name not in df_val.columns:
        raise ValueError(f"Target column '{target_col_name}' not found in validation data columns: {df_val.columns.tolist()}")
    
    X_val = df_val[feature_cols] # Assuming val features match train features
    y_val_single = df_val[target_col_name]
    print(f"  Validation X shape: {X_val.shape}, y_single shape: {y_val_single.shape}")
    
    return X_train, y_train_single, X_val, y_val_single

# ----------------------------------
# Optuna Objective Function
# ----------------------------------
def optuna_objective_single_target(
    trial, X_tr, y_tr_single, X_va, y_va_single, target_name_logging
):
    """Optuna objective function for tuning a single LGBMRegressor."""
    
    # --- Hyperparameter Search Space ---
    # You can customize these ranges as needed
    params = {
        'objective': 'regression_l2', # Or 'regression_l1' (MAE)
        'metric': 'l2',               # Or 'l1'
        'n_estimators': trial.suggest_int('n_estimators', 500, 2000, step=100), # Max estimators, early stopping will choose
        'learning_rate': trial.suggest_float('learning_rate', 0.005, 0.05, log=True),
        'num_leaves': trial.suggest_int('num_leaves', 20, 500),
        'max_depth': trial.suggest_int('max_depth', 5, 30), # -1 for no limit if num_leaves is primary
        'min_child_samples': trial.suggest_int('min_child_samples', 5, 200),
        'subsample': trial.suggest_float('subsample', 0.6, 1.0), # Bagging fraction
        'colsample_bytree': trial.suggest_float('colsample_bytree', 0.4, 1.0), # Feature fraction
        'reg_alpha': trial.suggest_float('reg_alpha', 1e-3, 10.0, log=True), # L1
        'reg_lambda': trial.suggest_float('reg_lambda', 1e-3, 10.0, log=True), # L2
        'random_state': 42,
        'n_jobs': -1,
        # 'verbose': -1, # Suppress LGBM's own verbose, we use callbacks for controlled output
    }

    print(f"\n[Optuna Trial {trial.number} for {target_name_logging}] Training with params:")
    for k, v in params.items():
        print(f"  {k}: {v}")

    model = lgb.LGBMRegressor(**params)

    # Progress monitoring within the fit call
    callbacks = [
        lgb.early_stopping(stopping_rounds=EARLY_STOPPING_ROUNDS, verbose=False),
        lgb.log_evaluation(period=LGBM_FIT_VERBOSE_PERIOD) # Renamed from print_evaluation
    ]

    model.fit(
        X_tr, y_tr_single,
        eval_set=[(X_va, y_va_single)],
        eval_metric='l2', # Ensure this matches the 'metric' in params if it's a list
        callbacks=callbacks
    )

    preds = model.predict(X_va)
    score = mean_squared_error(y_va_single, preds)

    # Store the best iteration (actual number of trees used)
    trial.set_user_attr("best_iteration", model.best_iteration_)
    print(f"[Optuna Trial {trial.number} for {target_name_logging}] Validation MSE: {score:.6f}, Best Iteration: {model.best_iteration_}")
    
    return score

# ----------------------------------
# Main Execution Block
# ----------------------------------
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Hyperparameter tuning for a single target variable using LightGBM and Optuna.")
    parser.add_argument("target_column_name", type=str, help="The exact name of the target column to tune (e.g., 'YSSY_u_forecast_t_plus_1').")
    parser.add_argument("--subsample", type=float, default=DEFAULT_TRAIN_SUBSAMPLE_FRACTION, help=f"Fraction of training data to use (0.0 to 1.0). Default: {DEFAULT_TRAIN_SUBSAMPLE_FRACTION}")
    parser.add_argument("--trials", type=int, default=DEFAULT_OPTUNA_N_TRIALS, help=f"Number of Optuna trials to run. Default: {DEFAULT_OPTUNA_N_TRIALS}")
    
    args = parser.parse_args()

    TARGET_TO_TUNE = args.target_column_name
    TRAIN_SUBSAMPLE_FRACTION = args.subsample
    OPTUNA_N_TRIALS = args.trials

    if not (0 < TRAIN_SUBSAMPLE_FRACTION <= 1.0):
        raise ValueError("Train subsample fraction must be between 0 (exclusive) and 1.0 (inclusive).")

    print(f"--- Starting Hyperparameter Tuning ---")
    print(f"Target Column: {TARGET_TO_TUNE}")
    print(f"Training Data Subsample Fraction: {TRAIN_SUBSAMPLE_FRACTION:.2f}")
    print(f"Number of Optuna Trials: {OPTUNA_N_TRIALS}")
    print(f"Early Stopping Rounds: {EARLY_STOPPING_ROUNDS}")
    print(f"Output directory for HPs: {OUTPUT_DIR.resolve()}")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # --- 1. Load and Prepare Data ---
    X_train, y_train_single, X_val, y_val_single = load_and_prepare_single_target_data(
        TRAIN_FILE, VAL_FILE, TARGET_TO_TUNE,
        TIMESTAMP_COL, TARGET_PREFIXES,
        TRAIN_SUBSAMPLE_FRACTION
    )

    # --- 2. Optuna Study ---
    study_name = f"tune_{TARGET_TO_TUNE.replace('+', 'p').replace('_', '')}" # Optuna-friendly study name
    study = optuna.create_study(direction="minimize", study_name=study_name)
    
    print(f"\n--- Running Optuna Study for {TARGET_TO_TUNE} ({OPTUNA_N_TRIALS} trials) ---")
    start_time_optuna = time.time()
    study.optimize(
        lambda trial: optuna_objective_single_target(trial, X_train, y_train_single, X_val, y_val_single, TARGET_TO_TUNE),
        n_trials=OPTUNA_N_TRIALS
    )


    print(f"\n--- Saving All Trial Data for {TARGET_TO_TUNE} ---")
    # Convert trial data to a pandas DataFrame
    trials_df = study.trials_dataframe()
    
    # The DataFrame includes columns like:
    # 'number', 'value', 'datetime_start', 'datetime_complete', 'duration',
    # 'params_...', 'user_attrs_...', 'state'
    
    # Sort by value (MSE)
    trials_df = trials_df.sort_values(by="value", ascending=True)
    
    # Sanitize filename for CSV
    safe_target_name_csv = TARGET_TO_TUNE.replace("+", "p").replace(":", "").replace("/", "")
    all_trials_output_file = OUTPUT_DIR / f"all_trials_{safe_target_name_csv}.csv"
    
    trials_df.to_csv(all_trials_output_file, index=False)
    print(f"All trial data saved to: {all_trials_output_file}")

    # You can then print the top N from the DataFrame if you still want console output
    print("\nTop 10 trials from DataFrame:")
    print(trials_df[['number', 'value', 'params_n_estimators', 'params_learning_rate', 'params_num_leaves', 'user_attrs_best_iteration']].head(10))

    
    optuna_duration = time.time() - start_time_optuna
    print(f"Optuna study finished in {optuna_duration:.2f} seconds ({optuna_duration/60:.2f} minutes).")

    # --- 3. Save Best Hyperparameters ---
    best_hps = study.best_params
    best_hps["best_iteration_"] = study.best_trial.user_attrs["best_iteration"] # From early stopping
    best_hps["validation_score_mse"] = study.best_value

    # Add some context
    best_hps["_target_column_tuned"] = TARGET_TO_TUNE
    best_hps["_train_subsample_fraction_used"] = TRAIN_SUBSAMPLE_FRACTION
    best_hps["_optuna_n_trials_run"] = OPTUNA_N_TRIALS
    best_hps["_early_stopping_rounds"] = EARLY_STOPPING_ROUNDS
    
    # Sanitize filename
    safe_target_name = TARGET_TO_TUNE.replace("+", "p").replace(":", "").replace("/", "")
    hp_output_file = OUTPUT_DIR / f"best_params_{safe_target_name}.json"
    save_json_artifact(best_hps, hp_output_file)

    print(f"\n--- Tuning Complete for {TARGET_TO_TUNE} ---")
    print(f"Best hyperparameters saved to: {hp_output_file}")
    print("Best Hyperparameters found:")
    for k, v in best_hps.items():
        if not k.startswith("_"): # Don't print context vars
            print(f"  {k}: {v}")