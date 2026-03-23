# PyEarthTool Data Notebooks

## Notebooks

- **Basic_Indexing.ipynb**  
  Introduces basic data indexing. Shows how to initialize a DataIndex object (using ERA5 as an example), search for file paths with the search method, and load data for a specific time by calling the DataIndex directly. Focuses on the unified interface and basic retrieval techniques.

- **Catalog.ipynb**  
  Explains data catalogs for managing and reusing DataIndex configurations. Demonstrates creating reusable entries (CatalogEntry), adding them to catalogs for sharing, and using the default catalog (Default_Catalog). Shows how catalog entries can be called like regular DataIndex objects.

- **CustomDataIndex.ipynb**  
  Guides on implementing custom data indexers. Explains inheriting from DataIndex or OperatorIndex to extend the library for custom data sources, especially standard NetCDF files. Provides examples of setting variables, transforms, and resolution.

- **GettingComplexSeries.ipynb**  
  Covers complex time series retrieval. Demonstrates the .series method for loading data over time ranges at specified intervals, including applying transforms. Introduces the custom datetime object (pyearthtoolsDatetime) and its behavior with resolutions and tolerances.

- **PatternIndexing.ipynb**  
  Introduces pattern-based indexing. Uses the pyearthtools.data.pattern module to index custom data sources following specific naming patterns (e.g., ExpandedDate, DirectDate). Shows implementing custom pattern indexers with filesystem search and catalog integration.

- **RegionCutting.ipynb**  
  Explains region cutting. Uses pyearthtools.data.transform.region to crop global datasets to regions of interest (e.g., bounding boxes, reference datasets, Shapefiles). Emphasizes applying transforms early in retrieval for performance.

- **SingleIndexing.ipynb**  
  Details single data indexing. Shows retrieving individual time steps, aggregating data (e.g., daily averages), and handling partially defined times (e.g., just a date). Includes examples from different sources like Himawari satellite data.

- **Transforms.ipynb**  
  Introduces dataset transforms. Demonstrates applying built-in transforms (e.g., region cutting, masking, interpolation) and defining custom ones. Explains transform collections and how to apply functions during DataIndex initialization or retrieval.

- **UsingTheInBuiltOperations.ipynb**  
  Covers built-in operations. Shows operations on DataIndex like range (for time range retrieval) and aggregation (e.g., mean, min). Includes advanced features like percentile calculations with visualization examples.

## Relationships Between Scripts

- **Foundation**: Basic_Indexing.ipynb and SingleIndexing.ipynb provide core indexing and retrieval, serving as the base for others.
- **Extension**: Catalog.ipynb and CustomDataIndex.ipynb enable configuration management and data source expansion for reusability.
- **Time Series**: GettingComplexSeries.ipynb adds time-range and interval handling on top of basic indexing.
- **Pattern and Transform**: PatternIndexing.ipynb handles custom data patterns, while Transforms.ipynb and RegionCutting.ipynb offer preprocessing tools (e.g., cropping, transforms).
- **Operations**: UsingTheInBuiltOperations.ipynb integrates everything for advanced aggregation and analysis.

## Data Formats

### Currently Supported Formats

- **NetCDF**: Core format for multidimensional scientific data (e.g., meteorological variables). Built-in indexers (ERA5, Himawari, etc.) primarily handle this; extensible via custom indexers.
- **Extension Mechanism**: Inherit from DataIndex or OperatorIndex classes to support other formats (e.g., pattern-matching custom files). Uses xarray underneath, compatible with NetCDF/Zarr, etc.
- **Other**: Shapefile used for region cutting (as transform input, not primary data format).

### Other Formats Possibly Encountered in Meteorological Analysis

- **GRIB**: Meteorological model outputs (e.g., ECMWF, GFS), gridded data. Requires cfgrib/pygrib for parsing.
- **HDF4/HDF5**: Satellite data (e.g., MODIS), supports compression and metadata, suitable for large datasets.
- **GeoTIFF**: Remote sensing raster data with geographic coordinates, suitable for GIS.
- **CSV/ASCII**: Station observation data, easy to parse but lacks spatial dimensions.
- **Shapefile**: Vector geographic features, used for masks/overlays.
- **Zarr**: Cloud-friendly chunked array format, similar to NetCDF, suitable for distributed storage (e.g., CMIP6).
Parquet: Columnar storage for big data analysis (e.g., observation time series).
Other: BUFR (observations), KML (Google Earth), JP2 (satellite), HDF-EOS, etc.

### Potential functions:
- Add built-in GRIB/HDF indexers, or Zarr/Parquet integration tutorials.
- Integrate Dask for parallel processing of large formats.
- Ensure transforms/operations are compatible with xarray loading results.