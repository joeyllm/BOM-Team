# Weather Station Data Pipeline — Documentation

## Overview

This pipeline transforms raw weather station `.txt` files into a machine-learning-ready dataset. Data flows through 9 scripts in the order below. Each script reads from one folder and writes to another.

```
Raw station files
      │
      ▼
[merge_stations.py]       — Merge old/new versions of the same station
      │
      ▼
[interpolateData0_5.py]   — Fill single 30-min gaps (linear)
      │
      ▼
[outage_lengths.py]       — (Diagnostic) Plot outage distributions per station
[find_missing_timestamp.py] — (Diagnostic) Find missing timestamps for a station pair
      │
      ▼
[drop_columns.py]         — Remove unwanted columns (e.g. max_gust_speed, aws_flag)
      │
      ▼
[crop_to_years.py]        — Filter data to a specific year range
      │
      ▼
[convertWindComponents.py] — Convert wind speed/dir → U/V components
      │
      ▼
[interpolate.py]          — Spline-interpolate gaps up to 5 steps (2.5 hrs)
      │
      ▼
[preprocess_data.py]      — Feature engineering + train/val/test dataset export
```

---

## Folder Names (Data Flow)

The folder names used across scripts are not defined in one place. This table maps where each folder is read from and written to:

| Folder | Produced by | Consumed by |
|---|---|---|
| `ProcessedData Manual/` | Manual / external | `merge_stations.py` |
| `ProcessedData/` | (external or merged output) | `interpolateData0_5.py`, `outage_lengths.py` |
| `InterpolatedData0.5/` | `interpolateData0_5.py` | `outage_lengths.py`, `convertWindComponents.py` |
| `UVComponentData/` | `convertWindComponents.py` | `interpolate.py` |
| `SplineInterpolatedData/` | `interpolate.py` | `drop_columns.py` (first config block) |
| `FinalData/` | `drop_columns.py` | `crop_to_years.py`, `preprocess_data.py`, `find_missing_timestamp.py` |
| `FinalData2000/` | `crop_to_years.py` | (end of file pipeline) |
| `OutageDistributionPlots_Grouped/` | `outage_lengths.py` | (visual output only) |
| `SplineInterpolationSamplePlots/` | `interpolate.py` | (visual output only) |

> **⚠️ Warning:** These folder names are hardcoded inside each script individually. There is no shared config file. If a folder name changes, every affected script must be updated manually.

---

## Script-by-Script Notes

---

### 1. `merge_stations.py`

**Purpose:** Merges two `.txt` files representing the same station at different time periods (e.g. a relocated instrument). Data from `file2` (the newer station) takes priority; gaps are filled from `file1`.

**Logic:** Uses `pd.merge(..., how='outer')` on timestamp, then `combine_first()` per weather parameter to prefer file2 values.

**Issues:**
- **Single-pair only.** Hardcoded to merge exactly two specific files (`YSRI.txt` and `YSRI Old.txt`). To merge a different pair, the filenames must be manually edited each time.
- **`data_completeness` includes `aws_flag`.** The completeness recalculation checks all of `WEATHER_PARAMS`, which includes `aws_flag`. This is likely unintentional — a flag field is not a measurement and shouldn't gate completeness.

---

### 2. `interpolateData0_5.py`

**Purpose:** Fills isolated single-timestep (30-minute) NaN gaps in weather data using linear interpolation (simple average of the two neighbours).

**Logic:** Iterates through each series value-by-value. If `value[i-1]` is valid, `value[i]` is NaN, and `value[i+1]` is valid, it fills `value[i]` with their average.

**Issues:**
- **Inconsistent with later spline step.** This script fills only single gaps; `interpolate.py` later fills gaps up to 5 steps using a spline. The relationship between these two passes is not documented — it is unclear whether running both is intentional or whether one is a draft of the other.
- **`data_completeness` recalculated here** using `ELEMENTS_TO_INTERPOLATE` — but `aws_flag` is not in that list, so the definition of completeness differs subtly from `merge_stations.py` and `interpolate.py`. See the cross-script inconsistency note below.
- **Float format `%.1f`** — data is saved with 1 decimal place here, which may reduce precision for some variables (e.g. pressure).

---

### 3. `outage_lengths.py` *(Diagnostic)*

**Purpose:** Produces grouped bar charts showing the distribution of outage lengths for each weather element at each station. Also prints uptime percentages. Output is PNG files only — it does not modify data.

**Issues:**
- `plt.cm.get_cmap()` is deprecated in recent Matplotlib versions. Should be replaced with `matplotlib.colormaps['viridis']` or `plt.get_cmap()`.
- The "30 min" bin (single-step gaps) will always dwarf other bins. The script handles this by clipping the y-axis and annotating clipped bars with a red label, but this means the "30 min" bars are always visually misleading.

---

### 4. `find_missing_timestamp.py` *(Diagnostic)*

**Purpose:** Compares one station file against a reference station and against the expected full 30-minute date range (2000–2024) to find missing timestamps.

**Issues:**
- **Fully hardcoded.** Station names (`YSNW`, `YSCN`), data folder, date range, and timestep are all set as module-level constants with no function wrapper or argument parsing. To check a different station, the constants must be edited directly.
- **Not importable.** All logic runs at module level (no `if __name__ == "__main__":` guard), so importing this file in another script would execute it immediately.

---

### 5. `drop_columns.py`

**Purpose:** Drops specified columns from all `.txt` files in a folder (e.g. removing `max_gust_speed`, `aws_flag`, `wind_dir_recalc` after they are no longer needed).

**⚠️ Bug — Duplicate Configuration Block:**
```python
# First assignment (lines ~35–36)
INPUT_SUBFOLDER_NAME = "SplineInterpolatedData"
OUTPUT_SUBFOLDER_NAME = "FinalData"

# Second assignment immediately overrides the first (lines ~38–39)
INPUT_SUBFOLDER_NAME = "FinalData"    # ← shadows the line above
OUTPUT_SUBFOLDER_NAME = "FinalData"
```
The first pair of assignments (`SplineInterpolatedData` → `FinalData`) is completely overridden by the second pair (`FinalData` → `FinalData`). The script currently reads from and writes to the same folder (`FinalData`). This may be intentional for in-place editing, but the leftover first assignment is confusing and should be removed.

---

### 6. `crop_to_years.py`

**Purpose:** Filters all `.txt` files to keep only rows within a specified year range.

**Issues:**
- **Start and end year are both set to 2000** in the `__main__` block:
  ```python
  START_YEAR_CONFIG = 2000
  END_YEAR_CONFIG = 2000
  ```
  This produces a single-year (2000-only) output. If the intention is to filter to a multi-year range, both values must be updated. The variable names suggest a range is expected — this looks like a placeholder that was never updated.
- The function itself is general and reusable; the limitation is entirely in the hardcoded `__main__` configuration.

---

### 7. `convertWindComponents.py`

**Purpose:** Converts `wind_speed` and `wind_dir` (meteorological, degrees from North) into Cartesian U (east–west) and V (north–south) components, then removes the original speed/direction columns.

**Formula used:**
```
U = -speed × sin(dir_rad)
V = +speed × cos(dir_rad)     ← NOTE: positive cos
```

**⚠️ Potential Convention Error:**

The code comment says:
```
# v = -speed * cos(direction_radians)
```
But the actual code is:
```python
df[V_COMPONENT_COL] = df[WIND_SPEED_COL] * np.cos(dir_rad)   # positive
```
Standard meteorological convention (wind *from* a direction) uses **negative cosine** for V. The sign discrepancy between the comment and the implementation needs to be verified — if wrong, all downstream wind direction reconstructions will be mirrored in the north–south axis. The wind direction recalculation in `interpolate.py` (`np.arctan2(-u, -v)`) does use the negated form, so this may be self-consistent within the pipeline, but it should be explicitly confirmed.

---

### 8. `interpolate.py`

**Purpose:** The main interpolation script. Fills NaN gaps of up to `MAX_GAP_STEPS_FOR_SPLINE = 5` timesteps (2.5 hours) using a local cubic spline fitted to the 6 nearest known points on each side of the gap. Also produces sample diagnostic plots of interpolated sections. Wind speed and direction are recalculated from interpolated U/V after each gap is filled.

**Key parameters (all at the top of the file):**
| Parameter | Value | Meaning |
|---|---|---|
| `MAX_GAP_STEPS_FOR_SPLINE` | 5 | Max gap size to attempt filling (2.5 hrs) |
| `SPLINE_CONTEXT_POINTS` | 6 | Known points used on each side for spline fit |
| `SPLINE_ORDER` | 3 | Cubic spline |
| `SPLINE_SMOOTHING_FACTOR` | 1 | `s=1` in `UnivariateSpline`; slight smoothing |
| `NUM_SAMPLE_PLOTS` | 50 | Random interpolation events to plot |

**Issues:**
- **Large amount of commented-out code** in `plot_interpolation_sample_spline_v2()` (lines 295–308). These are previous plotting approaches. They should be removed or moved to a separate archive file.
- **Comment at line 337** reads: *"Make sure to use the corrected versions from above"* — this is a developer note that was never removed and is confusing to anyone reading the file.
- **`SPLINE_SMOOTHING_FACTOR = 1`**: With `s=1`, `UnivariateSpline` does *not* exactly interpolate the known points (it smooths them). This is intentional but undocumented — a comment should explain why smoothing is preferred over exact interpolation (`s=0`) here.
- **`data_completeness` recalculation** (lines 402–408) uses `["air_temp", "dew_point", "msl_pressure", "wind_speed_recalc", "wind_dir_recalc"]` — again a different set from other scripts.

---

### 9. `preprocess_data.py`

**Purpose:** The final ML preparation script. Loads all station files, aligns them to a common timestamp index, engineers features (lagged values, time derivatives, pressure gradients, cyclical time features), and exports train/validation/test CSVs.

**⚠️ Syntax Error — Script Will Not Run:**

Line 21–23 contains a broken variable assignment:
```python
TIMESTEP_MIN          # ← incomplete line
UTES = 30             # ← this is a new variable 'UTES', not 'TIMESTEP_MINUTES'
```
This should be:
```python
TIMESTEP_MINUTES = 30
```
`TIMESTEP_MINUTES` is used extensively throughout the script (lines 25, 26, 44, etc.) and will cause a `NameError` immediately on execution. `UTES` is never used elsewhere.

**⚠️ Very Small Train/Val/Test Proportions:**
```python
TRAIN_SIZE_PROPORTION      = 0.08   # 8%  of 25 years ≈ 2 years
VALIDATION_SIZE_PROPORTION = 0.01   # 1%  of 25 years ≈ 3 months
TEST_SIZE_PROPORTION       = 0.01   # 1%  of 25 years ≈ 3 months
```
Only 10% of the total 25-year dataset (2000–2024) is used. The remaining 90% is loaded into memory but discarded. This is almost certainly a placeholder used for fast iteration during development — the proportions should be updated for a real training run.

**Other notes:**
- Feature engineering is complex and well-structured: it includes raw lags (full resolution for the target station YSSY, every-other-step for others), pressure gradients between station pairs, 3-hourly temperature/pressure derivatives, and special short-lag V-component derivatives for station BELL.
- The `get_val()` helper (defined inside the loop at line 328) raises `IndexError` on out-of-bounds access rather than returning NaN silently. This is intentional and good — it surfaces index calculation bugs loudly.
- `FEATURE_ORDER_X` is set on the first valid sample and then reused for all subsequent samples. If the first sample happens to be missing a feature that later samples would have, the feature order will be wrong. This is a low-risk issue in practice but worth noting.

---

## Cross-Script Issues

### `data_completeness` is recalculated with different column sets in every script

| Script | Columns used for completeness check |
|---|---|
| `merge_stations.py` | All of `WEATHER_PARAMS` (includes `aws_flag`) |
| `interpolateData0_5.py` | `ELEMENTS_TO_INTERPOLATE` (excludes `aws_flag`) |
| `interpolate.py` | `air_temp, dew_point, msl_pressure, wind_speed_recalc, wind_dir_recalc` |
| `preprocess_data.py` | Not recalculated; uses the value from the file |

The flag means something different at each stage. Any downstream script that uses `data_completeness` directly should be aware that its meaning depends on which script last touched the file.

### Float precision changes across the pipeline

| Script | `float_format` |
|---|---|
| `interpolateData0_5.py` | `%.1f` (1 decimal place) |
| `convertWindComponents.py` | `%.2f` |
| `interpolate.py` | `%.3f` |
| `preprocess_data.py` | `%.5f` |

Saving with 1 decimal place in step 2 permanently truncates precision that cannot be recovered in later steps.

### No master script or pipeline runner

There is no `run_pipeline.py`, `Makefile`, or README that documents the correct execution order or the expected folder structure. The order must be inferred from the folder names referenced in each script's configuration block.

---

## Recommended Actions (Priority Order)

1. **Fix the `NameError` in `preprocess_data.py`** — change `TIMESTEP_MIN` / `UTES = 30` to `TIMESTEP_MINUTES = 30`.
2. **Verify the V-component sign** in `convertWindComponents.py` — confirm the code (`+cos`) or fix it to match the comment (`-cos`).
3. **Remove the duplicate config block** in `drop_columns.py` — keep only the intended input/output folders.
4. **Update `crop_to_years.py`** — set `END_YEAR_CONFIG` to the intended final year (e.g. 2024).
5. **Standardise `data_completeness`** — pick one column set and use it consistently, or rename the column at each stage to reflect what it actually measures.
6. **Update train/val/test proportions** in `preprocess_data.py` before any real training run.
7. **Add a `main()` guard** to `find_missing_timestamp.py` so it can be imported safely.
8. **Write a `run_pipeline.py`** or at minimum a README listing the scripts in order with the folder names expected at each step.
9. **Clean up commented-out code** in `interpolate.py` (lines 295–308 and the stray developer comment at line 337).
