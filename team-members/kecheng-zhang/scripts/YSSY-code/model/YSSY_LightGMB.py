# ----------------------------------
# Imports
# ----------------------------------
import pandas as pd
import numpy as np
import lightgbm as lgb
from sklearn.multioutput import MultiOutputRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error
import optuna
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import joblib
import json
from datetime import timedelta
from pathlib import Path
import random




# ----------------------------------
# Configuration
# ----------------------------------
TIMESTAMP_COL = "timestamp_t"
DATA_DIR = Path("data24x0.1")
TRAIN_FILE = DATA_DIR / "training_dataset.txt"
VAL_FILE = DATA_DIR / "validation_dataset.txt"
TEST_FILE = DATA_DIR / "test_dataset.txt"
YSSY_RAW_FILE = DATA_DIR / "YSSY.txt" # Not used in this version, as lagged features are in main files


PARAMS_FILE_PATH = Path("output") / "best_params_final_31May.json" # Or "best_params_initial.json"


OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(exist_ok=True) # Create output directory if it doesn't exist
BEST_PARAMS_INITIAL_FILE = OUTPUT_DIR / "best_params_initial.json"
BEST_PARAMS_FINAL_FILE = OUTPUT_DIR / "best_params_final.json"
FINAL_MODEL_FILE = OUTPUT_DIR / "final_yssy_wind_model.joblib"
PLOTS_DIR = OUTPUT_DIR / "plots"
PLOTS_DIR.mkdir(exist_ok=True)








# ----------------------------------
# Data Handling Functions
# ----------------------------------
def get_column_names(df_columns):
    """Identifies target, drop, and YSSY lagged wind columns."""
    target_cols = [col for col in df_columns if col.startswith("YSSY_u_forecast_t+") or col.startswith("YSSY_v_forecast_t+")]
    target_cols = sorted(target_cols, key=lambda x: (int(x.split('+')[-1]), x.split('_')[1]))

    cols_to_drop_explicit = [
        "BELL_mslp_deriv_t_vs_t3", "BELL_mslp_deriv_t3_vs_t6", "BELL_mslp_deriv_t_vs_t6",
        "MTB_mslp_deriv_t_vs_t3", "MTB_mslp_deriv_t3_vs_t6", "MTB_mslp_deriv_t_vs_t6"
    ]
    cols_to_drop_from_x = [col for col in cols_to_drop_explicit if col in df_columns]

    yssy_u_lag_cols = sorted([c for c in df_columns if c.startswith("YSSY_u_component_lag")], key=lambda x: int(x.split('lag')[-1]))
    yssy_v_lag_cols = sorted([c for c in df_columns if c.startswith("YSSY_v_component_lag")], key=lambda x: int(x.split('lag')[-1]))

    return target_cols, cols_to_drop_from_x, yssy_u_lag_cols, yssy_v_lag_cols

def load_and_prepare_data(file_path, target_cols, cols_to_drop_from_x, ts_col=TIMESTAMP_COL):
    """Loads data, separates features/targets, drops specified columns."""
    print(f"Loading data from: {file_path}")
    df = pd.read_csv(file_path)
    df[ts_col] = pd.to_datetime(df[ts_col])

    y = df[target_cols].copy()
    timestamps = df[ts_col].copy()

    cols_to_remove_for_x = target_cols + [ts_col] + cols_to_drop_from_x
    X = df.drop(columns=[col for col in cols_to_remove_for_x if col in df.columns])
    
    print(f"Loaded {file_path}: X shape {X.shape}, y shape {y.shape}")
    return df, X, y, timestamps

def load_hyperparameters(file_path):
    """Loads hyperparameters from a JSON file."""
    if not file_path.exists():
        print(f"Error: Hyperparameter file not found at {file_path}")
        return None
    try:
        with open(file_path, 'r') as f:
            params = json.load(f)
        print(f"Successfully loaded hyperparameters from {file_path}")
        return params
    except Exception as e:
        print(f"Error loading hyperparameters from {file_path}: {e}")
        return None
    


# ----------------------------------
# Optuna Objective Function
# ----------------------------------
def optuna_objective(trial, X_train, y_train, X_val, y_val):
    """Optuna objective function for hyperparameter tuning."""
    objective_type = trial.suggest_categorical('objective', ['regression_l1', 'regression_l2'])
    metric_type = 'l1' if objective_type == 'regression_l1' else 'l2'

    params = {
        'objective': objective_type,
        'metric': metric_type,
        'n_estimators': trial.suggest_int('n_estimators', 500, 1500, step=50),
        'learning_rate': trial.suggest_float('learning_rate', 0.01, 0.05, log=True),
        'num_leaves': trial.suggest_int('num_leaves', 50, 1000, step=50),
        'max_depth': trial.suggest_int('max_depth', 5, 30), # Allow -1 if num_leaves is well-tuned, but fixed range for now
        'min_child_samples': trial.suggest_int('min_child_samples', 10, 500),
        'subsample': trial.suggest_float('subsample', 0.6, 1.0), # bagging_fraction
        'colsample_bytree': trial.suggest_float('colsample_bytree', 0.5, 1.0), # feature_fraction
        'reg_alpha': trial.suggest_float('reg_alpha', 1e-3, 10.0, log=True), # L1
        'reg_lambda': trial.suggest_float('reg_lambda', 1e-3, 10.0, log=True), # L2
        'random_state': 42,
        'n_jobs': -1,
        'verbose': -1,
    }

    params = {
        'objective': 'regression_l2',
        'metric': 'l2',
        'n_estimators': 800,
        'learning_rate': 0.02130325383067257,
        'num_leaves': 200,
        'max_depth': 17, # Allow -1 if num_leaves is well-tuned, but fixed range for now
        'min_child_samples': 45,
        'subsample': 0.8767980400385894, # bagging_fraction
        'colsample_bytree': 0.6947769061520032, # feature_fraction
        'reg_alpha': 1.959826832632918, # L1
        'reg_lambda': 0.12507898430314643, # L2
        'random_state': 42,
        'n_jobs': -1,
        'verbose': -1,
    }

    print(f"Trial {trial.number} Parameters: {params}") # New: Print chosen parameters

    base_lgbm = lgb.LGBMRegressor(**params)
    multi_output_model = MultiOutputRegressor(base_lgbm)

    multi_output_model.fit(X_train, y_train)
    preds = multi_output_model.predict(X_val)

    if objective_type == 'regression_l1':
        score = mean_squared_error(y_val, preds)
    else: # regression_l2
        score = mean_squared_error(y_val, preds)
    
    return score



# ----------------------------------
# Model Training Function
# ----------------------------------
def train_final_lgbm_model(X_train, y_train, params):
    """Trains a MultiOutputRegressor with LGBM using given parameters."""
    lgbm_params = params.copy()
    if 'metric' not in lgb.LGBMRegressor().get_params().keys(): # pragma: no cover
        lgbm_params.pop('metric', None) # metric is for fit, not constructor for some versions if not using callbacks

    base_lgbm = lgb.LGBMRegressor(**lgbm_params, random_state=42, n_jobs=-1)
    model = MultiOutputRegressor(base_lgbm)
    model.fit(X_train, y_train)
    return model



# ----------------------------------
# Evaluation Function
# ----------------------------------
def evaluate_model_performance(model, X_test, y_test, target_names):
    """Evaluates the model and prints metrics."""
    print("\nEvaluating model performance...")
    preds = model.predict(X_test)

    overall_mae = mean_absolute_error(y_test, preds)
    overall_mse = mean_squared_error(y_test, preds)
    print(f"Overall MAE: {overall_mae:.4f}")
    print(f"Overall MSE: {overall_mse:.4f}")

    print("\nPer-target metrics:")
    for i, target_name in enumerate(target_names):
        mae = mean_absolute_error(y_test.iloc[:, i], preds[:, i])
        mse = mean_squared_error(y_test.iloc[:, i], preds[:, i])
        print(f"  {target_name}: MAE={mae:.4f}, MSE={mse:.4f}")
    
    return overall_mae, overall_mse



# ----------------------------------
# Plotting Functions
# ----------------------------------
def plot_single_forecast(timestamp_anchor, model, full_df_row, target_names,
                         yssy_u_lag_cols, yssy_v_lag_cols, x_cols_for_model, plot_idx=""):
    """Plots past, actual future, and forecasted future winds for a sample."""
    
    # Extract past YSSY winds (lag11 (oldest) to lag0 (newest))
    past_u_winds = full_df_row[yssy_u_lag_cols].values[::-1] 
    past_v_winds = full_df_row[yssy_v_lag_cols].values[::-1]

    # Time axes
    past_times = [timestamp_anchor - timedelta(minutes=30 * i) for i in range(11, -1, -1)]
    future_times = [timestamp_anchor + timedelta(minutes=30 * i) for i in range(1, 13)]

    # Extract actual future winds
    actual_future_winds_flat = full_df_row[target_names].values
    actual_future_u = actual_future_winds_flat[0::2] # u_t+1, u_t+2, ...
    actual_future_v = actual_future_winds_flat[1::2] # v_t+1, v_t+2, ...

    # Make model prediction
    X_sample = pd.DataFrame([full_df_row[x_cols_for_model]], columns=x_cols_for_model)
    pred_future_winds_flat = model.predict(X_sample)[0]
    pred_future_u = pred_future_winds_flat[0::2]
    pred_future_v = pred_future_winds_flat[1::2]

    fig, axs = plt.subplots(2, 1, figsize=(15, 10), sharex=True)
    fig.suptitle(f"YSSY Wind Forecast anchored at {timestamp_anchor.strftime('%Y-%m-%d %H:%M')}", fontsize=16)

    # U-component
    axs[0].plot(past_times, past_u_winds, 'o-', color='gray', label='Past U (Input)')
    axs[0].plot(future_times, actual_future_u, 's-', color='blue', label='Actual Future U')
    axs[0].plot(future_times, pred_future_u, 'x--', color='red', label='Forecasted U')
    axs[0].set_ylabel('U-component (knots)')
    axs[0].legend()
    axs[0].grid(True)

    # V-component
    axs[1].plot(past_times, past_v_winds, 'o-', color='gray', label='Past V (Input)')
    axs[1].plot(future_times, actual_future_v, 's-', color='green', label='Actual Future V')
    axs[1].plot(future_times, pred_future_v, 'x--', color='orange', label='Forecasted V')
    axs[1].set_ylabel('V-component (knots)')
    axs[1].legend()
    axs[1].grid(True)

    axs[1].set_xlabel('Time')
    axs[1].xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))
    plt.xticks(rotation=45)
    plt.tight_layout(rect=[0, 0, 1, 0.96]) # Adjust layout to make space for suptitle
    
    plot_filename = PLOTS_DIR / f"forecast_plot_{timestamp_anchor.strftime('%Y%m%d_%H%M')}{plot_idx}.png"
    plt.savefig(plot_filename)
    print(f"Saved plot: {plot_filename}")
    plt.close(fig)


def plot_random_samples(model, test_df_full, target_names, yssy_u_lag_cols, yssy_v_lag_cols,
                        x_cols_for_model, num_samples=5):
    """Generates plots for a number of random samples from the test set."""
    print(f"\nGenerating {num_samples} random sample plots...")
    if len(test_df_full) < num_samples:
        print(f"Warning: Requested {num_samples} samples, but test set only has {len(test_df_full)}.")
        num_samples = len(test_df_full)
    
    random_indices = random.sample(range(len(test_df_full)), num_samples)
    
    for i, idx in enumerate(random_indices):
        sample_row = test_df_full.iloc[idx]
        anchor_ts = sample_row[TIMESTAMP_COL]
        plot_single_forecast(anchor_ts, model, sample_row, target_names,
                             yssy_u_lag_cols, yssy_v_lag_cols, x_cols_for_model, plot_idx=f"_rand{i+1}")




# ----------------------------------
# Utility Functions
# ----------------------------------
def save_model_artifact(model_obj, path):
    joblib.dump(model_obj, path)
    print(f"Model saved to {path}")

def load_model_artifact(path):
    model_obj = joblib.load(path)
    print(f"Model loaded from {path}")
    return model_obj

def save_json(data_dict, path):
    with open(path, 'w') as f:
        json.dump(data_dict, f, indent=4)
    print(f"Parameters saved to {path}")

def load_json(path):
    with open(path, 'r') as f:
        data_dict = json.load(f)
    print(f"Parameters loaded from {path}")
    return data_dict




# ----------------------------------
# Main Execution Block
# ----------------------------------
if __name__ == "__main__":
    # --- 1. Load and Prepare Data ---
    # Load a small sample or just headers first to get column names
    print("Identifying column names...")
    sample_df_cols = pd.read_csv(TRAIN_FILE, nrows=0).columns # Read only headers
    TARGET_COL_NAMES, COLS_TO_DROP_FROM_X, YSSY_U_LAG_COLS, YSSY_V_LAG_COLS = get_column_names(sample_df_cols)

    print(f"Target columns ({len(TARGET_COL_NAMES)}): {TARGET_COL_NAMES[:4]}...")
    print(f"Columns to drop from X ({len(COLS_TO_DROP_FROM_X)}): {COLS_TO_DROP_FROM_X}")
    print(f"YSSY U lagged input cols ({len(YSSY_U_LAG_COLS)}): {YSSY_U_LAG_COLS[:4]}...")
    print(f"YSSY V lagged input cols ({len(YSSY_V_LAG_COLS)}): {YSSY_V_LAG_COLS[:4]}...")

    df_train, X_train, y_train, ts_train = load_and_prepare_data(TRAIN_FILE, TARGET_COL_NAMES, COLS_TO_DROP_FROM_X)
    df_val, X_val, y_val, ts_val = load_and_prepare_data(VAL_FILE, TARGET_COL_NAMES, COLS_TO_DROP_FROM_X)
    df_test, X_test, y_test, ts_test = load_and_prepare_data(TEST_FILE, TARGET_COL_NAMES, COLS_TO_DROP_FROM_X)
    
    X_COLUMN_ORDER = X_train.columns # Save for consistent feature order in plotting

    # --- 2. Hyperparameter Tuning (Optuna) ---
    print("\nStarting Optuna initial tuning...")


    # FOR FASTER INITIAL TESTING: Subsample data
    sample_fraction = 0.1 # Use only 1% of data for quick test
    X_train_sampleXS = X_train.sample(frac=sample_fraction, random_state=42)
    y_train_sampleXS = y_train.loc[X_train_sampleXS.index]

    sample_fraction = 0.1 # Use only 1% of data for quick test
    X_train_sample = X_train.sample(frac=sample_fraction, random_state=42)
    y_train_sample = y_train.loc[X_train_sample.index]

    print(f"Using {len(X_train_sampleXS)} samples for initial Optuna tuning.")


    # For quick test, use small n_trials. For real run: 10-20 for initial.
    initial_optuna_trials = 1 # TODO: Increase to 10-20 for a 1-hour run
    study_initial = optuna.create_study(direction="minimize", study_name="yssy_wind_initial_tuning")
    study_initial.optimize(lambda trial: optuna_objective(trial, X_train_sampleXS, y_train_sampleXS, X_val, y_val), 
                           n_trials=initial_optuna_trials)
    
    best_params_initial = study_initial.best_params
    print(f"Best Initial Params (after {initial_optuna_trials} trials): {best_params_initial}")
    print(f"Best Initial Value: {study_initial.best_value}")
    save_json(best_params_initial, BEST_PARAMS_INITIAL_FILE)

    best_hyperparameters = load_hyperparameters(PARAMS_FILE_PATH)


    # --- 3. Intermediate Visualization ---
    print("\nTraining temporary model for initial visualization...")
    temp_model_params = best_params_initial.copy()
    temp_model = train_final_lgbm_model(X_train_sample, y_train_sample, best_hyperparameters)
    
    # Plot for a manually specified timestamp (if it exists in test set)
    if not df_test.empty:
        manual_plot_timestamp_str = df_test[TIMESTAMP_COL].iloc[0].strftime('2023-12-14 05:00')
        
        try:
            manual_ts_to_plot = pd.to_datetime(manual_plot_timestamp_str)
            print(f"\nAttempting to plot specific forecast for timestamp: {manual_ts_to_plot}")
            
            # Find the row in df_test corresponding to this timestamp
            target_row_df = df_test[df_test[TIMESTAMP_COL] == manual_ts_to_plot]
            
            if not target_row_df.empty:
                target_row = target_row_df.iloc[0]
                plot_single_forecast(manual_ts_to_plot, temp_model, target_row, TARGET_COL_NAMES,
                                     YSSY_U_LAG_COLS, YSSY_V_LAG_COLS, X_COLUMN_ORDER, plot_idx="_manual")
            else:
                print(f"Timestamp {manual_ts_to_plot} not found in the test set for manual plotting.")
        except Exception as e:
            print(f"Error during manual plot for {manual_plot_timestamp_str}: {e}")
    else:
        print("Test set is empty, skipping manual plot example.")

    num_plot_samples = 25 # 
    plot_random_samples(temp_model, df_test, TARGET_COL_NAMES, YSSY_U_LAG_COLS, YSSY_V_LAG_COLS,
                        X_COLUMN_ORDER, num_samples=num_plot_samples)


    save_model_artifact(temp_model, FINAL_MODEL_FILE)

    # --- 5. Final Model Evaluation ---
    evaluate_model_performance(temp_model, X_test, y_test, TARGET_COL_NAMES)


    print("\nWorkflow complete.")
    print(f"Outputs (model, params, plots) are in: {OUTPUT_DIR.resolve()}")