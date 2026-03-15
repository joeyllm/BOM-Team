# 📂 Data Environment & Rules

Welcome to the **BOM Nowcasting** data environment. This directory contains the documentation for accessing and working with our shared project datasets. 

Because we are dealing with massive amounts of data—specifically a 60 TB corpus—it is critical that you understand how our storage architecture works to avoid crashing the system or breaking your personal workspace.

## 💾 Storage Limits & Quotas

Each student is allocated a strict **50 GB personal storage quota** for their notebook environment. This space is intended solely for your code, small test files, environment configurations, and limited output data.

**🛑 Rule #1: Never copy shared datasets to your personal directory.**

Attempting to copy even a small fraction of our main datasets (like a handful of 2 GB Parquet files) will instantly exhaust your 50 GB quota, freeze your notebook, and break your environment. Always read the data directly from the shared, read-only folders into memory.

---

## ⚠️ CRITICAL WARNING: Data Persistence & GitHub

While you can process data and save the outputs to your 50 GB personal allocation, **there is no guarantee that your saved data will be there from week to week.** This is a dynamic, evolving environment. Storage may be wiped, instances may be reset, or your quota may need to be cleared to fix an issue. 

**You must commit your code to the GitHub repository regularly.** In data engineering, your cleaned data is completely disposable, but the *code* that cleans it is your most valuable asset. If your processed data is wiped, you can simply run your pipeline again. If you lose your pipeline code, you lose weeks of work. **Commit your pipelines to GitHub!**

---

## 📚 Documentation Index

Please read through the following documents to understand how to interact with the data safely and efficiently:

| File | Description |
| :--- | :--- |
| `Fineweb.md` | Details on the 60 TB Fineweb corpus, the read-only mount, and the Parquet file structure. |
| `LoadingData.md` | Code examples for loading data efficiently on CPU (Pandas/PyArrow) vs. GPU (cuDF). |
| `L4Gpu.md` | Crucial VRAM management rules and OOM (Out of Memory) prevention for the L4 GPUs. |
| `BestPractices.md` | The "Subset First" rule, memory management, and how to transition code into background jobs. |
| `Publishing.md` | Hugging Face, Kaggle & Data Cards |
