# 🏗️ System Overview & Etiquette

This document provides a high-level overview of the compute server's hardware, its intended use, and the etiquette required when sharing this environment.

## ⚙️ Hardware Specifications 🖥️

The BOM Nowcasting compute environment is a robust server equipped with:
* **110 CPU Cores**
* **6x NVIDIA L4 GPUs**
* **500 GB (0.5 TB) RAM**
* **160 TB of Storage**

---

## 🚦 Shared Resource Availability

Please keep in mind that this server is a **shared environment** that handles other background workloads outside of this project. 

Because of this, maximum compute power may not *always* be available. However, when the resources are free, you are heavily encouraged to use them! 

---

## 🧪 Purpose: Testing & Pipeline Building

This system is designed primarily for **testing and building pipelines**, *not* for executing massive, full-scale runs interactively. 

When working with data, you must follow the **Subset First** rule:

1. **Subset Data:** Only load a small subset of the data into your notebook.
2. **Validate:** Test your code, check your I/O (Input/Output) efficiency, and profile your execution speed.
3. **Background Jobs:** If your pipeline runs well on the subset, a dedicated job will be created from your code. This job will be scheduled to run in the background over the full dataset during slow/off-peak times.



> **💡 Why this matters (The 60 TB Example):**
> We are working with massive datasets, including a 60 TB dataset structured in 2GB Parquet files. If your data cleaning code is highly optimized, processing this can take about **1 day**. If the code is unoptimized or poorly written, that exact same job could take **weeks** and bottleneck the entire system. Test small, optimize, then scale!

---

## 🚧 System Evolution & Support

This compute environment is actively evolving alongside the project. Because we are constantly building and tweaking, you may occasionally run into build errors or temporary outages.

If something isn't working as expected, or you think a service is down, please let **Matthew Altenburg** know so it can be investigated and resolved.
