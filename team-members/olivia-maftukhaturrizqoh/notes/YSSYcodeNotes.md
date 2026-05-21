## Steps:
### Step 1 `process_data.py` : Raw Data Ingestion & Cleaning

Processes raw BOM fixed-width weather files, one station file at a time, and saves cleaned per-station data.

**Process:**
1. Read the fixed-width file, initially parsed as strings
2. Extract Station ID (strip any whitespace); station ID is assumed consistent throughout the file
3. Create a `timestamp` column by combining date and time string parts before conversion
4. Convert relevant columns to numeric, coercing errors to `NaN`
5. Create a `data_completeness` flag column (contains the actual measurements)
6. Select and reorder final columns
7. Save the processed data to the `FinalData/` folder

---

### Step 2 `convertWindComponents.py` : Wind Direction → U/V Components

Reads data files and converts raw wind speed and direction into meteorological U and V wind components, then saves the updated files without the original wind speed/direction columns.

**Conversion formulas (meteorological convention — wind FROM direction):**

```
u = -speed × sin(direction_radians)    # positive = eastward (wind from West)
v = -speed × cos(direction_radians)    # positive = northward (wind from South)
```

save dataframe with The `u_component` and `v_component` columns are appended as the last columns of each file.

---

### Step 3 : Gap Filling & Station Merging

A collection of scripts that handle missing timestamps and data gaps, then merge station files.

#### `find_missing_timestamps.py`
- Loads file with potential missing rows and the reference file
- Identifies timestamps present in the expected date range but missing from the station data 

#### `interpolate.py`
- Fills specific NaN gaps using **cubic spline interpolation**, fitted to a limited number of context points surrounding the gap
- Uses integer-based `iloc` indexing for precision
- Includes a plotting function (`v2`) to visualise spline-interpolated samples with context, connected thick lines, and updated y-axis handling
- If U/V components were interpolated, derives the corresponding wind speed and direction; otherwise uses existing values

#### `interpolateData0.5.py`
- Fills **single-timestep NaN gaps only** using **linear interpolation** (average of the two neighbouring values)
- Gaps of 2 or more consecutive NaN steps are left unchanged
- Reads all processed station files, applies interpolation per element, and saves results

#### `merge_stations.py`
- Reads Reads a processed weather data file into a pandas DataFrame : read two processed station files and merges them based on defined priority rules
- Performs an **outer merge** on timestamp to retain all records from both files
- Column suffixes are added to distinguish source files during merging
- **Merge rule per parameter:** use File 2 value if available; otherwise use File 1 value; otherwise `NaN`
- Sorts by timestamp and saves the merged output

---
### Step 4 `preprocess_data.py` : ML Sample Construction

creating ML samples from the previous 24 hours of station weather. Transforms the cleaned and merged station data into structured machine learning samples. Each sample represents 24 hours of historical weather observations used to predict the next 24 hours of wind at YSSY.

**Key configuration:**
- Data configuration (stations, features, file paths)
- Dataset splitting configuration (train / validation / test proportions and date boundaries) :  0.8, 0.1, 0.1
- Feature engineering across all stations (lagged values, pressure gradients, time derivatives, cyclical encodings)
- Saves the three split datasets as flat CSV-format `.txt` files

---

### Step 5 `LightGBM/evaluate_all_24hr_models.py` : Generating Predictions

Loads all trained models and generates wind forecasts for the next 24 hours at YSSY at 30-minute intervals.

**Models format are `.joblib`:**
- A Python serialization format (via the `joblib` library)
- Saves a trained model object to disk (similar in concept to a `.ckpt` file in deep learning)
- Stores learned model parameters and coefficients, enabling inference without retraining
- Loaded the models for prediction

**Model naming convention:**

| Model name suffix | Forecast horizon |
|---|---|
| `_u_forecast_t_plus_1` | U component, 30 min ahead |
| `_v_forecast_t_plus_1` | V component, 30 min ahead |
| `_u_forecast_t_plus_2` | U component, 60 min ahead |
| `...` | `...` |
| `_u_forecast_t_plus_48` | U component, 24 hours ahead |
| `_v_forecast_t_plus_48` | V component, 24 hours ahead |

**Output:**
One prediction call per model produces one column of predictions. The final output DataFrame added **96 columns** representing U and V wind forecasts at YSSY for every 30-minute interval over the next 24 hours:

```
48 forecast steps × 2 components (u, v) = 96 columns
```

---

### 6. training and evaluating LightGBM models