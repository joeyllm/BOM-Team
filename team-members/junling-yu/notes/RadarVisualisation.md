https://github.com/ACCESS-Community-Hub/PyEarthTools/blob/develop/docs/notebooks/RadarVisualisation.ipynb

The time-series of corrected_reflectivity is computed by averaging over all x, y, z. This shows overall precipitation intensity changes, and low reflectivity values tend to produce cleaner, less noisy plots.

For visualization:

Pick the most active moment (2024-04-02T05:00 nearest time with max radar echo).
Plot the 2D map by averaging in height (z), so you see horizontal rain pattern in x-y plane — where the precipitation is and how intense.

For 3D:

Use the same time and take vertical slices (z = 500..6000 m), convert to voxel values.
Build a 3D volume rendering so you can inspect the vertical structure of the storm: where strong echoes are in altitude, cloud shape, and core structure using semi-transparent isosurfaces.