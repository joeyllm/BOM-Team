# YSSY Wind Forecast Pipeline — Notes

**Project:** YSSY 24-Hour Wind Forecast
**Notebook:** `weather_pipeline.ipynb`
**Date:** 2026-05-25

---

## What This Notebook Does

Takes 25 years (2000–2024) of raw weather station data from 10 stations around NSW and
trains a machine learning model to forecast wind at Sydney Airport (YSSY) 24 hours ahead,
in 30-minute steps.

**One-line summary of the workflow:**
```
FinalData/*.txt  →  Parquet  →  XGBoost  →  Forecast plots
```

---

## How to Use It

### Setup
1. Place the notebook at `/home/jovyan/Techlauncher/weather_pipeline.ipynb`
2. Update the paths in the config cell (Section 0):
```python
DATA_FOLDER  = Path('/home/jovyan/data/weather/YSSY-Winds/Techlauncher/FinalData')
PARQUET_FILE = Path('/home/jovyan/Techlauncher/weather_data.parquet')
MODELS_DIR   = Path('/home/jovyan/Techlauncher/models')
PLOTS_DIR    = Path('/home/jovyan/Techlauncher/forecast_plots')
```
3. Install dependencies:
```bash
/opt/venv/bin/pip install xgboost pandas numpy matplotlib scikit-learn joblib pyarrow
```

### Running the notebook
- Run all cells top to bottom: **Run → Run All Cells**
- Or run one cell at a time with **Shift+Enter**
- Section 1 (data prep) is skipped automatically if the Parquet file already exists
- Section 4 (training) skips any model already saved to disk — safe to re-run

### First run vs subsequent runs
| Run | Section 1 | Section 4 |
|---|---|---|
| First time | Loads all .txt files, saves Parquet (~2 min) | Trains all 96 models (~20–30 min on GPU) |
| After that | Skipped — Parquet already exists | Skipped — models already saved |

### To force a full reprocess
```bash
rm /home/jovyan/Techlauncher/weather_data.parquet
rm -r /home/jovyan/Techlauncher/models/
```

### Quick test run
Set `QUICK_RUN = True` in the config cell to train on 10% of data — useful for checking
the pipeline works end to end before committing to a full training run.

---

## Input Data

**Location:** `FinalData/` folder
**Format:** CSV files saved as `.txt`, one file per station

**File format:**
```
timestamp,air_temp,dew_point,msl_pressure,u_component,v_component
2000-01-01 00:00:00,12.2,6.3,,-3.86,-4.6
```

**Columns:**
| Column | Unit | Notes |
|---|---|---|
| timestamp | — | 30-min intervals, 2000–2024 |
| air_temp | °C | |
| dew_point | °C | |
| msl_pressure | hPa | Empty for BELL and MTB (no sensor) |
| u_component | kt | East-west wind. Positive = eastward |
| v_component | kt | North-south wind. Positive = northward |

Wind was pre-converted to U/V components in an earlier preprocessing step —
the raw `wind_speed` and `wind_dir` columns are not in these files.

**Stations:**
| ID | Location | Has Pressure |
|---|---|---|
| YSSY | Sydney Airport (target) | ✓ |
| YSCN | Canberra | ✓ |
| YSNW | Nowra | ✓ |
| YBTH | Bathurst | ✓ |
| YCNK | Cessnock | ✓ |
| YSBK | Bankstown | ✓ |
| YSRI | Richmond | ✓ |
| YSWG | Wagga Wagga | ✓ |
| BELL | Bellambi | ✗ |
| MTB | Mount Boyce | ✗ |

---

## Outputs

### 1. Parquet file
**Path:** `weather_data.parquet`
All 10 stations merged into one wide table, aligned to a clean 30-min grid.
Used as the input for all subsequent steps — the raw `.txt` files are never touched again.

### 2. Trained models
**Path:** `models/u_models/` and `models/v_models/`
96 `.joblib` files — one per forecast target:
```
models/
├── u_models/
│   ├── YSSY_u_forecast_t_plus_1.joblib
│   ├── YSSY_u_forecast_t_plus_2.joblib
│   └── ... (48 files)
└── v_models/
    ├── YSSY_v_forecast_t_plus_1.joblib
    └── ... (48 files)
```

### 3. Performance plot
**Path:** `forecast_plots/performance_vs_lead_time.png`
Two side-by-side charts showing MAE and MSE for U and V components at every
forecast step from 30 min to 24 hr. Error should increase with lead time —
if it stays flat something is wrong.

### 4. Forecast sample plots
**Path:** `forecast_plots/forecast_YYYYMMDD_HHMM.png`
One plot per random test sample showing:
- Red line — observed temperature
- Blue line — observed dewpoint
- Grey line — observed wind speed
- **Thick black line** — model's 24-hr wind speed forecast
- Grey circles — observed wind direction (right axis)
- Black crosses — forecast wind direction (right axis)
- Dotted vertical line — the forecast anchor time

---

## How the Model Works

### Why XGBoost
XGBoost is a **gradient boosted decision tree** model. It builds hundreds of decision trees
in sequence, where each new tree corrects the errors of all the trees before it.
LightGBM was the original choice (it was used in earlier scripts) but could not be installed
on this VM due to a missing `libgomp.so.1` system library. XGBoost produces equivalent
results and was already available.

### Why 96 individual models
The forecast covers 48 steps × 2 wind components (U and V) = 96 targets.
One model is trained per target rather than one model predicting all 96 outputs at once.

This is better because:
- Predicting 30 min ahead is a very different problem to predicting 24 hr ahead
- Short lead times rely heavily on the most recent observations
- Long lead times rely more on pressure patterns and time-of-day cycles
- One shared model would compromise on both

### Features (~1000+ per sample)
| Group | What it captures |
|---|---|
| Lagged YSSY values (48 lags) | Full 24-hr history at the target station |
| Lagged other station values | 6-hr full resolution + every other step to 24 hr |
| Pressure gradients (YBTH−YSSY, etc.) | Synoptic pressure patterns driving wind |
| 3-hr derivatives of temp/pressure | How fast conditions are changing |
| sin/cos time-of-day | Sea breeze cycle |
| sin/cos day-of-year | Seasonal patterns |

Wind direction is stored as U/V rather than degrees because degrees are circular —
359° and 1° are nearly the same wind but numerically far apart. U and V are plain
numbers that regression models handle cleanly. Wind speed and direction are
reconstructed from U/V for plotting only.

### Train / Val / Test split
| Split | Date range | Purpose |
|---|---|---|
| Train | 2000–2018 (76%) | Model learns from this |
| Validation | 2019–2021 (12%) | Early stopping — prevents overfitting |
| Test | 2022–2024 (12%) | Final evaluation — model never sees this during training |

Split is **chronological** — no shuffling. Shuffling would leak future data into
training and produce misleadingly good results.

### Key hyperparameters
| Parameter | Value | Why |
|---|---|---|
| `learning_rate` | 0.05 | Small steps = more trees but less overfitting |
| `max_depth` | 6 | Limits tree complexity, reduces GPU memory usage |
| `n_estimators` | 1000 | Max trees — early stopping cuts this short |
| `early_stopping_rounds` | 50 | Stops if val error doesn't improve for 50 trees |
| `max_bin` | 128 | Halves histogram memory on GPU (default is 256) |
| `colsample_bytree` | 0.5 | Each tree sees 50% of features — reduces overfitting |
| `device` | cuda | Uses the NVIDIA L4 GPU |

---

## Environment

**VM:** JupyterHub — High-performance PyTorch environment
**GPU:** NVIDIA L4 (23 GB VRAM)
**GPU utilisation during training:** ~93%
**GPU memory used:** ~9 GB / 23 GB
**Approximate training time:** 20–30 minutes for all 96 models

Monitor GPU while training:
```bash
watch -n 1 nvidia-smi
```

---

## Issues Encountered & How They Were Fixed

### LightGBM could not be imported
`libgomp.so.1` was missing from the system. The library existed inside the
scikit-learn package (`scikit_learn.libs/libgomp-e985bcbb.so.1.0.0`) but
LightGBM could not find it. Multiple fixes were attempted (symlinks, `LD_PRELOAD`,
reinstall) but the VM environment was too locked down. Switched to XGBoost instead.

### Out of GPU memory during training
XGBoost tried to allocate 16 GB but only 13 GB was free.
Fixed by reducing `max_depth` from 10 → 6 and adding `max_bin: 128`.

### Notebook could not be saved to `data/` folder
The `data/` directory is a read-only mounted volume. Saved the notebook to
`/home/jovyan/Techlauncher/` instead and pointed `DATA_FOLDER` at the read-only path.

---

## What I Learnt

### Data & preprocessing
- Weather data from different stations needs to be aligned to a common timestamp grid
  before it can be used together — stations can have different gaps and start/end dates
- Wind speed and direction should be converted to U/V components before modelling
  because direction is circular (359° ≈ 1°) and breaks regression models
- Parquet is much faster to load than CSV and much smaller on disk — worth saving
  intermediate data as Parquet rather than re-processing every run
- Vectorised pandas operations (`.shift()`, `.where()`) are orders of magnitude faster
  than Python loops for gap filling on large time series

### Modelling
- For multi-step time series forecasting, training one model per forecast step
  outperforms one multi-output model because each lead time has a different error structure
- Early stopping is essential — without it XGBoost will keep adding trees and overfit
- `colsample_bytree` and `max_bin` are the most effective knobs for reducing GPU
  memory usage without significantly hurting accuracy
- GPU training with XGBoost requires `device='cuda'` AND `tree_method='hist'` —
  one without the other falls back to CPU silently

### Infrastructure
- JupyterHub VMs can have read-only mounted data volumes — always check before assuming
  you can write anywhere
- `nvidia-smi` is the quickest way to verify GPU is actually being used
- System libraries like `libgomp` can be missing from containerised environments even
  when the Python package is installed — XGBoost was more reliable than LightGBM here
- Always check `ldd <library.so>` when a shared library fails to load — it shows
  exactly which dependency is missing

### Workflow
- Splitting one large pipeline across many Python scripts makes it very hard to
  understand the full workflow — a single notebook is much clearer for a team
- Skipping expensive steps (data prep, training) when outputs already exist on disk
  makes iterating much faster during development
- `QUICK_RUN = True` with a 10% subsample is a good pattern for smoke-testing a
  pipeline before committing to a full run

---

## Possible Future Improvements

- **Better gap filling** — extend from single-step (30 min) to 5-step (2.5 hr) using
  `pd.Series.interpolate(limit=5)`
- **Outlier clipping** — sensor faults produce physically impossible values that corrupt
  the model; clip to physical limits per variable
- **Data quality report** — print missing data % per station after loading so you know
  which stations are unreliable
- **Walk-forward cross-validation** — more rigorous than a single train/test split for
  reporting results
- **Station selection** — not all 10 stations are equally useful; correlation analysis
  could identify which ones to drop
