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
