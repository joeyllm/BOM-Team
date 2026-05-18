## Steps:
1. process_data.py : 
    1. reading raw BOM fixed-width weather files
    2. cleaning and saving per-station data
    
    Processes a single raw weather data file one by one.
    Read the fixed-width file, initially as strings.
    # --- Data Cleaning and Transformation ---
        1. Extract Station ID (and strip any whitespace) (Assuming station ID is consistent throughout the file)
        2. Create 'timestamp' column
        Ensure date/time parts are strings for concatenation then conversion
        3. Convert relevant columns to numeric, coercing errors to NaN
        4. Create 'data_completeness' column (contain the actual measurement)
        5. Select and reorder final columns
        6. save the processed data to FinalData folder
        
2. convertWindComponents.py : converting wind speed/direction into u_component and v_component 
    Reads data files, converts wind speed/direction to U/V components, and saves new files without original wind speed/direction.
    Calculate U and V components
         U component: positive for wind from the West (eastward wind)
         V component: positive for wind from the South (northward wind)
         Meteorological convention (wind FROM):
             u = -speed * sin(direction_radians)
             v = -speed * cos(direction_radians)
    u and v component are added as the last columns.
    save dataframe with u/v components/

3. filling gaps and merging station data
    find_missing_timestamp.py : 
    - load file with potential missing rows and the reference file
    - Find timestamps in expected_range but NOT in df1
    interpolate.py :
     Interpolates a specific NaN gap in a series using a cubic spline, fitted to a limited number of context points before and after the gap.
     Uses integer locations (iloc) for indexing.
     v2 function: Plots a sample of spline interpolated data with context, updated y-axis handling and connected thick lines. Derive wind speed/direction if U/V were interpolated, or use existing.

    interpolateData0.5.py :
     Linearly interpolates single-timestep NaN gaps in a pandas Series.
     Reads processed data files, interpolates single-step gaps, and saves them.

    merge_stations.py :
     Reads a processed weather data file into a pandas DataFrame
     Merges two processed weather data files based on specified rules : 
        Perform an outer merge on the timestamp to keep all records from both files
        Suffixes are added to distinguish columns from df1 and df2
        Create the final merged column for the parameter : 
            Rule: If file2 has data, use it. Else if file1 has data, use it. Else NaN.
        Sort by timestamp adn save the merged data 

4. creating ML samples from the previous 24 hours of station weather 
    preprocess_data.py : 
    data configuration, data splitting configuration, and save splitting dataset.

5. predicting the next 24 hours of YSSY wind at 30-minute intervals
    LightGBM/evaluate_all_24hr_models.py :
    make predictions with all models (u_models and v_models are from model dir folder)
     models are in .joblib format : its a Python serialization format, saves a Python object (like a trained ML model) to disk so you can reload it later without retraining. generally saves model parameters, learned coefficients to run inferences.
     prediction : one per model, each producing a column of predictions.
     t_plus in models name :    t_plus_1   = 30 minutes ahead
                                t_plus_2   = 60 minutes ahead (1 hour)
                                t_plus_3   = 90 minutes ahead
                                ...
                                t_plus_48  = 1440 minutes ahead (24 hours)
    so will added 96 new columns represent the model's forecast of u and v wind at YSSY for every 30-minute interval over the next 24 hours.

6. training and evaluating LightGBM models 📊