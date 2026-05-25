import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.interpolate import UnivariateSpline




# --- 1. Generate Synthetic Time Series Data ---
np.random.seed(42)
n_points = 48
time = np.arange(n_points)
trend = np.sin(time / ((n_points-1)/(2*np.pi))) + time / 20
noise = np.random.normal(0, 0.3, n_points)
data_original = trend + noise

# --- 2. Introduce a Single Gap of 10 Missing Steps ---
data_with_missing = data_original.copy()
gap_start_index = 20
n_missing = 10
gap_end_index = gap_start_index + n_missing -1
data_with_missing[gap_start_index : gap_start_index + n_missing] = np.nan

series_with_missing = pd.Series(data_with_missing, index=time)
series_original = pd.Series(data_original, index=time)

# --- 3. Local Smoothed Spline Interpolation ---

# Parameters for local interpolation
n_local_points = 5  # Number of points on EACH side of the gap to use
smoothing_factor_local = 0.4 # Smoothing factor for the local spline (adjust as needed)
spline_degree_local = 3    # Degree of the spline (e.g., 3 for cubic)

# Create a copy to fill
series_interpolated_local = series_with_missing.copy()

# Identify the actual numeric indices of the gap in the pandas series
# This is a bit more robust if your index isn't a simple arange(n_points)
# For this example, direct iloc slicing is also fine.
missing_mask = series_interpolated_local.isna()
if not missing_mask.any():
    print("No missing data to interpolate.")
else:
    # Find the first and last NaN index (assuming one contiguous block for simplicity here)
    # For multiple gaps, you'd need to iterate through them.
    # This example focuses on the single specified 10-step gap.

    # Indices of the data points TO BE interpolated (the gap itself)
    gap_indices_to_fill = series_interpolated_local.index[gap_start_index : gap_start_index + n_missing]

    # Select data points around the gap
    # Points BEFORE the gap
    points_before_gap = series_with_missing.iloc[:gap_start_index].dropna().tail(n_local_points)

    # Points AFTER the gap
    points_after_gap = series_with_missing.iloc[gap_start_index + n_missing:].dropna().head(n_local_points)

    # Combine local data for fitting the spline
    local_data_for_spline = pd.concat([points_before_gap, points_after_gap])

    if len(local_data_for_spline) < spline_degree_local + 1:
        print(f"Not enough local data points ({len(local_data_for_spline)}) to fit a spline of degree {spline_degree_local}.")
        print("Consider reducing n_local_points or spline_degree_local, or using a simpler interpolation.")
        # Fallback or error handling
        # For this example, let's try linear if spline fails due to insufficient points
        if len(local_data_for_spline) >= 2: # Need at least 2 points for linear
             print("Falling back to local linear interpolation for the gap.")
             # Create a temporary series with only the gap and its local context
             temp_series_for_linear = pd.concat([points_before_gap,
                                                 pd.Series(index=gap_indices_to_fill, dtype=float), # The NaNs
                                                 points_after_gap])
             filled_gap_values = temp_series_for_linear.interpolate(method='linear').loc[gap_indices_to_fill]
             series_interpolated_local.loc[gap_indices_to_fill] = filled_gap_values
        else:
            print("Not enough points even for linear interpolation. Gap remains.")

    else:
        local_x = local_data_for_spline.index.values
        local_y = local_data_for_spline.values

        # Fit the local spline
        local_spline = UnivariateSpline(local_x, local_y, s=smoothing_factor_local, k=spline_degree_local)

        # Interpolate the values for the missing steps
        interpolated_values_for_gap = local_spline(gap_indices_to_fill.values)

        # Fill the gap in our copied series
        series_interpolated_local.loc[gap_indices_to_fill] = interpolated_values_for_gap

# --- For Comparison: Global Scipy UnivariateSpline (from previous example) ---
known_indices_global = series_with_missing.dropna().index.values
known_values_global = series_with_missing.dropna().values
smoothing_factor_global = 5 # Same as before
spline_global = UnivariateSpline(known_indices_global, known_values_global, s=smoothing_factor_global, k=3)
interpolated_global_scipy = spline_global(time)


# --- Plotting the results ---
plt.figure(figsize=(15, 10))

plt.plot(series_original.index, series_original.values, 'ko-', label='Original Data (no missing)', alpha=0.3, markersize=3)
plt.plot(series_with_missing.index, series_with_missing.values, 'bo', label='Data with Missing Gap', markersize=6)

# Highlight the local points used for the local spline
if len(local_data_for_spline) >= spline_degree_local + 1 : # Only if spline was fit
    plt.plot(local_data_for_spline.index, local_data_for_spline.values, 'ms', markersize=8, markerfacecolor='none', label=f'Local {n_local_points}x2 points for fit')

plt.plot(series_interpolated_local.index, series_interpolated_local.values, 'gD--', label=f'Local Smoothed Spline (s={smoothing_factor_local}, k={spline_degree_local})', linewidth=2, markersize=4)
#plt.plot(time, interpolated_global_scipy, 'r:', label=f'Global UnivariateSpline (s={smoothing_factor_global})', linewidth=2)


# Mark the gap boundaries for clarity
plt.axvline(series_with_missing.index[gap_start_index], color='gray', linestyle='--', alpha=0.7, label='Gap Start/End')
plt.axvline(series_with_missing.index[gap_end_index], color='gray', linestyle='--', alpha=0.7)


plt.title(f'Local ({n_local_points} points each side) vs Global Smoothed Spline Interpolation')
plt.xlabel('Time Step')
plt.ylabel('Value')
plt.legend()
plt.grid(True)
plt.savefig('time_series_local_vs_global_spline_interpolation.png')
# plt.show()

print("Plots saved to 'time_series_local_vs_global_spline_interpolation.png'")

# --- Example with very few local points to test fallback ---
# (Optional: you can uncomment to run this specific test)
print("\n--- Testing with insufficient local points ---")
data_with_missing_edge = data_original.copy()
gap_start_index_edge = 1 # Gap very close to the beginning
data_with_missing_edge[gap_start_index_edge : gap_start_index_edge + n_missing] = np.nan
series_with_missing_edge = pd.Series(data_with_missing_edge, index=time)
series_interpolated_local_edge = series_with_missing_edge.copy()
gap_indices_to_fill_edge = series_interpolated_local_edge.index[gap_start_index_edge : gap_start_index_edge + n_missing]

points_before_gap_edge = series_with_missing_edge.iloc[:gap_start_index_edge].dropna().tail(n_local_points)
points_after_gap_edge = series_with_missing_edge.iloc[gap_start_index_edge + n_missing:].dropna().head(n_local_points)
local_data_for_spline_edge = pd.concat([points_before_gap_edge, points_after_gap_edge])

print(f"Number of local points available for edge case: {len(local_data_for_spline_edge)}")
if len(local_data_for_spline_edge) < spline_degree_local + 1:
    print(f"Not enough local data points ({len(local_data_for_spline_edge)}) to fit a spline of degree {spline_degree_local}.")
    if len(local_data_for_spline_edge) >= 2:
         print("Falling back to local linear interpolation for the edge gap.")
         temp_series_for_linear_edge = pd.concat([points_before_gap_edge,
                                             pd.Series(index=gap_indices_to_fill_edge, dtype=float),
                                             points_after_gap_edge])
         filled_gap_values_edge = temp_series_for_linear_edge.interpolate(method='linear').loc[gap_indices_to_fill_edge]
         series_interpolated_local_edge.loc[gap_indices_to_fill_edge] = filled_gap_values_edge
         plt.figure(figsize=(10,6))
         plt.plot(series_original, label="Original")
         plt.plot(series_with_missing_edge, 'o', label="Missing Edge")
         plt.plot(series_interpolated_local_edge, '--', label="Local Linear Fallback")
         plt.legend()
         plt.title("Edge Case Fallback to Linear")
         plt.savefig("edge_case_interpolation.png")
         print("Plot saved to edge_case_interpolation.png")
    else:
        print("Not enough points even for linear interpolation. Gap remains.")
else:
    print("Sufficient points for spline (this shouldn't happen with gap_start_index_edge=1 and n_local_points=5)")