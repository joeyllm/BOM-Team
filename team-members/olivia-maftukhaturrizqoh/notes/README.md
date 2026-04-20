# Notes 📝

## week02

- Installing PyEarthTools on the remote JupyterHub, and tried to access the env from the jupyter notebook to be able to access and import the tools in PyEarthTools
- Read tutorials notebook : 

### 1. `Gallery.ipynb`
Provides an overview of how the tutorial notebooks are organised, as a map of the pyearthtools tutorial ecosystem, outlines:
- **Easiest notebooks to start with** : low hardware requirement, suitable for beginners
- **Working with Station Data** : medium hardware requirement
- **Tutorials on specific modelling** : more advanced use cases
- **Deep dive into other modules** : for users wanting to explore the full tool 

---

### 2. `Project_config.ipynb`
the configuration needed to use pyearthtools effectively:
- **Setting up project paths** : defining `ERA5LOWRES` (path to ERA5 data) and `PROJECT_HOME` (working directory)
- **Path configuration** : how pyearthtools references data locations throughout the tool
- **Accessing data** : how the config connects to downstream notebooks and tools

> **Note:** Running this notebook fully requires ERA5 data to be downloaded first. The `ERA5LOWRES` path must point to a valid local data directory (which is huge data).

---

## Issues Encountered

- `healpy` and `hydra` packages fail to build on Windows : skipped for now
- `no module named pyearthtools` : resolved by ensuring correct Python environment selected in VS Code

## Week03

### 1. Environment Setup & Package Installation
Resolving basic environment issues before getting PyEarthTools fully operational:
- Identified Graphviz requires a system-level binary install, not just pip
- Discovered PyEarthTools is a modular system — each feature is a separate package that must be installed individually
- Manually installed all packages from /PyEarthTools/packages/ especially to be able to import nci_site_archive

### 2. Data Preparation and Pipeline Exploration
Ran and studied the data_pipeline notebook, which covers :
- how to create pipelines for data preprocessing—combining data sources, transformations, and operations into a reusable, visualizable flow.
- it Uses public WeatherBench 2 ERA5 data (low-res, ~64x32 grid) fetched directly from Google Cloud, no local archives or registration needed.
- pipelines can be shared as templates for similar tasks.

### 3. NCI Project Access
- Tried to run several notebooks on tutorial (himawariAllBands, Working_with_Climate_Data, and Catalog), apparently several datasets are gated behind NCI project membership. Encountered access errors and require to join project.

### 4. Data Sources Explored

**Himawari Satellite Imagery**
- Operated by JMA (Japan Meteorological Agency)
- Geostationary satellite providing multi-band imagery over the Asia-Pacific region
- Data includes all bands (visible, infrared, water vapour channels)
- Relatively low spatial resolution compared to other observational sources
- Used as a remote sensing input
- requires NCI project membership to load

**Radar Data**
Explored as a input alongside satellite imagery
Radar Visualisatoin notebook : show radar data visualization in 2D/3D as a self-contained demo, including :
- download and load 1 day data, explore the metadata and visualize data

## Week04

### 1. About ERA5 data 
ERA5 is the fifth generation ECMWF atmospheric reanalysis of the global climate, covering the period from January 1940 to present. It is produced by the Copernicus Climate Change Service (C3S) at ECMWF and provides hourly estimates of a large number of atmospheric, land and oceanic climate variables. The data cover the Earth on a 31km grid and resolve the atmosphere using 137 levels from the surface up to a height of 80km.

**Variables**
ERA5 provides data from the Earth's surface to the top of the atmosphere, for variables such as air temperature, wind, rainfall, sea-surface temperature and ocean wave height. --> so useful for weather forecasting research : it's essentially a complete historical record of the global atmosphere.

**"reanalysis"**
Reanalysis combines model data with observations from across the world into a globally complete and consistent dataset using the laws of physics. Principle : data assimilation, is based on the method used by numerical weather prediction centres, where every so many hours a previous forecast is combined with newly available observations in an optimal way to produce a new best estimate of the state of the atmosphere. (like reconstructing what the weather actually was, everywhere on Earth, using both real observations and physics models to fill in the gaps. )

**so large (270GB)** Because it covers the entire globe, hourly, from 1940 to today, at 31km resolution across 137 atmospheric levels. to try --> may be can only downloaded a tiny 1-day slice of wind data.
ERA5 is essentially the training data, the model learns patterns from decades of historical weather to predict future conditions. Reanalysis is also used to train machine learning models to predict the weather.

**format**
- .nc (NetCDF) : most common, works well with Python
- .grib : another format ECMWF uses, but less common for Python workflows

### Notebook
Tried to retrieve ERA5 data via cdsapi python, 1 hour and 1 month