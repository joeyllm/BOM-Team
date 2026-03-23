# Session Notes: PyEarthTools Environment & Pipeline Setup
**Date:** 2026-03-23
**Focus:** Data Ingestion, Pipeline Architecture, and Environment Debugging

## 🏆 What We Achieved

* **Architecture Breakdown:** Analyzed the core `pyearthtools` tutorial notebook and conceptually split it into two distinct, modular scripts:
    1.  **Data Ingestion (`ingest_era5.py`):** Fetching raw ERA5 NetCDF data from Google Cloud.
    2.  **Data Pipeline (`build_pipeline.py`):** Standardizing, normalizing, and reshaping data into Numpy arrays.
* **Data Verification:** Successfully downloaded the 2.8GB ERA5 test dataset to `/tmp/outputs` and verified its integrity (contains valid time steps from 1959 to 2021).

## 🛑 The Technical Roadblocks
* **Environment Clashes:** We discovered that the default `pip install` command was struggling to link the library's sub-modules (like `tutorial` and `pipeline`) to our specific virtual environment (`/opt/venv/`).
* **The `pyearthtools` Cache Bug:** The library uses highly aggressive, hidden internal caching (stored in `~/.pyearthtools`). Because the pipeline script initially ran before the data was fully downloaded, it permanently cached a "data not found" state and refused to look at the fresh data.

## 🧹 The Environment Reset
* Successfully wiped the slate clean to prepare for a fresh installation in the next session.
* Deleted the 2.8GB test file (`/tmp/outputs`), the hidden caches (`~/.pyearthtools` and `~/.cache/pyearthtools`), and uninstalled the broken library components.
* **Note:** The project repository, personas, risk log, and folder structure remain perfectly intact.

---

## 🚀 Game Plan for Next Session

### Step 1: The Local Source Installation
Clone the source code and install it directly into the virtual environment using the explicit path. This ensures all sub-modules link correctly without global environment clashes.

```bash
git clone [https://github.com/ACCESS-Community-Hub/PyEarthTools.git](https://github.com/ACCESS-Community-Hub/PyEarthTools.git)
cd PyEarthTools
/opt/venv/bin/python3 -m pip install -r requirements.txt
/opt/venv/bin/python3 -m pip install -e packages/tutorial
/opt/venv/bin/python3 -m pip install -e packages/pipeline
/opt/venv/bin/python3 -m pip install -e packages/data

Gemini said
Here is the raw Markdown code block. You can copy this directly and save it as a new file (something like pyearthtools_debugging_log.md) right into your repository's notes folder.

Markdown
# Session Notes: PyEarthTools Environment & Pipeline Setup
**Date:** 2026-03-23
**Focus:** Data Ingestion, Pipeline Architecture, and Environment Debugging

## 🏆 What We Achieved
* **Agile & Admin:** Finalized the two project personas (Operational Forecaster & Infrastructure Builder) and generated the Week 2 report.
* **Git Troubleshooting:** Resolved a Visual Studio file-locking issue by adding the `.vs/` directory to `.gitignore` and clearing the Git cache.
* **Architecture Breakdown:** Analyzed the core `pyearthtools` tutorial notebook and conceptually split it into two distinct, modular scripts:
    1.  **Data Ingestion (`ingest_era5.py`):** Fetching raw ERA5 NetCDF data from Google Cloud.
    2.  **Data Pipeline (`build_pipeline.py`):** Standardizing, normalizing, and reshaping data into Numpy arrays.
* **Data Verification:** Successfully downloaded the 2.8GB ERA5 test dataset to `/tmp/outputs` and verified its integrity (contains valid time steps from 1959 to 2021).

## 🛑 The Technical Roadblocks
* **Environment Clashes:** We discovered that the default `pip install` command was struggling to link the library's sub-modules (like `tutorial` and `pipeline`) to our specific virtual environment (`/opt/venv/`).
* **The `pyearthtools` Cache Bug:** The library uses highly aggressive, hidden internal caching (stored in `~/.pyearthtools`). Because the pipeline script initially ran before the data was fully downloaded, it permanently cached a "data not found" state and refused to look at the fresh data.

## 🧹 The Environment Reset
* Successfully wiped the slate clean to prepare for a fresh installation in the next session.
* Deleted the 2.8GB test file (`/tmp/outputs`), the hidden caches (`~/.pyearthtools` and `~/.cache/pyearthtools`), and uninstalled the broken library components.
* **Note:** The project repository, personas, risk log, and folder structure remain perfectly intact.

---

## 🚀 Game Plan for Next Session

### Step 1: The Local Source Installation
Clone the source code and install it directly into the virtual environment using the explicit path. This ensures all sub-modules link correctly without global environment clashes.

```bash
git clone [https://github.com/ACCESS-Community-Hub/PyEarthTools.git](https://github.com/ACCESS-Community-Hub/PyEarthTools.git)
cd PyEarthTools
/opt/venv/bin/python3 -m pip install -r requirements.txt
/opt/venv/bin/python3 -m pip install -e packages/tutorial
/opt/venv/bin/python3 -m pip install -e packages/pipeline
/opt/venv/bin/python3 -m pip install -e packages/data

Step 2: Re-Ingest the Data
Re-create the ingest_era5.py script. Download the data to the temporary directory using the strict default filename expected by the library's internal index:

output_dir="/tmp/outputs"

filename="mini.nc"

Step 3: Run the Pipeline Test
Re-create the build_pipeline.py script.

Crucial Fix: Include os.environ['ERA5LOWRESDEMO'] = "/tmp/outputs" at the very top of the script, before any pyearthtools imports, to force the library to bypass its default cache and look in our specific output folder.

Test the pipeline against a known date from the dataset (e.g., 2010-01-01T00).

