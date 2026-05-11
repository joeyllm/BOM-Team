import gcsfs
import xarray as xr
import pandas as pd

# 1. Initialize the GCS filesystem (anonymous access for the free public bucket)
fs = gcsfs.GCSFileSystem(token='anon')

# 2. Configuration
date = "2026-05-10" # The single day we want to investigate
band = "B13"        # Band 13 (Clean IR)
bucket = "gcp-public-data-himawari8"

# Generate 30-minute timestamps for the entire day (e.g., 00:00, 00:30, 01:00...)
times = pd.date_range(start=date, end=f"{date} 23:59", freq="30min")

file_paths = []

print("Scanning Google Cloud Storage for matching files...")

for t in times:
    # Format the time variables to match the bucket's folder structure
    year = t.strftime('%Y')
    month = t.strftime('%m')
    day = t.strftime('%d')
    hhmm = t.strftime('%H%M')
    
    # Construct the path pattern to search
    # Note: Structure is generally /{Bucket}/AHI-L1b-FLDK/{YYYY}/{MM}/{DD}/{HHMM}/
    path_pattern = f"{bucket}/AHI-L1b-FLDK/{year}/{month}/{day}/{hhmm}/*{band}*.nc"
    
    # Query the bucket for files matching this pattern
    matched_files = fs.glob(path_pattern)
    
    if matched_files:
        # Prepend 'gs://' so xarray knows it's a Google Storage object
        file_paths.extend(["gs://" + f for f in matched_files])

print(f"Found {len(file_paths)} files for 30-minute intervals.")

# 3. Open the dataset lazily
# engine='h5netcdf' is highly recommended for reading NetCDF4 files over cloud storage
print("Opening dataset lazily (reading metadata only)...")
ds = xr.open_mfdataset(
    file_paths, 
    engine='h5netcdf', 
    combine='nested', 
    concat_dim='time',
    parallel=True # Uses Dask to read metadata from multiple files simultaneously
)

# 4. Define the Australia / Oceania Bounding Box
# Himawari-8 Full Disk covers roughly 60°N to 60°S and 80°E to 160°W
lat_max = -10.0 # Top edge (Northern Australia / PNG)
lat_min = -45.0 # Bottom edge (Tasmania / Southern Ocean)
lon_min = 110.0 # Left edge (West Coast)
lon_max = 155.0 # Right edge (East Coast)

# 5. Apply the Spatial Crop
# Note: Satellite latitude coordinates are usually stored descending (North to South).
# If xarray throws an empty array warning, swap lat_max and lat_min.
aus_subset = ds.sel(
    lat=slice(lat_max, lat_min), 
    lon=slice(lon_min, lon_max)
)

print("\n--- Data Reduction Results ---")
# .nbytes calculates the size of the data in memory
print(f"Original Full Disk Size: {ds.nbytes / (1024**3):.2f} GB")
print(f"Cropped Australia Size:  {aus_subset.nbytes / (1024**3):.2f} GB")

print("\n--- Cropped Dataset Metadata ---")
print(aus_subset)

# Optional: To actually download the cropped data to your local machine:
# print("Downloading cropped subset to local file...")
# aus_subset.to_netcdf("himawari_aus_20260510_B13.nc")