# Notebooks 📓

## Week02

---

## Environment Setup

- **Tool:** PyEarthTools (cloned from team repo)
- **Python version:** 3.13.9 (Global)
- **OS:** Windows 11
- **IDE:** VS Code

### Installation Notes
- PyEarthTools requires **Python 3.11 or higher**
- Installed dependencies via `pip install -r requirements.txt` inside the cloned repo
- Some packages (`healpy`, `hydra`) do not build on Windows natively, workaround needed for advanced notebooks
- ERA5 data access requires a **CDS (Climate Data Store) account** from Copernicus

---

## ERA5 Data Download

To run most pyearthtools notebooks, ERA5 reanalysis data is required.

### Steps :
1. Registered at [cds.climate.copernicus.eu](https://cds.climate.copernicus.eu)
2. Accepted the ERA5 dataset licence
3. Set up CDS API credentials in `~/.cdsapirc`
4. Downloaded a small test file (1 day of wind data) using the request:

## Week03

Ran RadarVisualization notebook on googlecolab, crash while loading all 1 day data, adjust a little to only load 10 
