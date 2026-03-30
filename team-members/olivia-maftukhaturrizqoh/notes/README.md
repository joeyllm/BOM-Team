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
- it Uses public WeatherBench 2 ERA5 data (low-res, ~64x32 grid) fetched directly from Google Cloud—no local archives or registration needed.
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
