# 🚀 NVIDIA L4 GPU: Capabilities & Usage 🖥️

This document outlines the role of the **NVIDIA L4 GPUs** within our compute infrastructure. Because we have a limited number of these GPUs 🛑, it is important to understand their specific purpose for the different phases of our project.

## ⚙️ Hardware Overview 🛠️

Each L4 GPU is equipped with **24 GB of VRAM**. They are highly efficient cards optimized heavily for **inference**, AI video, and data processing ⚡, making them perfectly suited for our pipeline preparation.

---

## 📅 Term 1 Focus: Data Preparation & Inference 🧹

During the first term, the GPUs will act as the engine for our data pipeline 🚂. Instead of running large training jobs from scratch, you will use the L4s for accelerated preprocessing, inference, and validation workflows.

**Key tasks for Term 1:**
* 🧽 **Dataset Cleaning:** Running preprocessing jobs to filter, sort, and format raw inputs.
* 🏎️ **Accelerated Processing with cuDF:** For robust data cleaning, we highly recommend using the **`cudf`** library. It provides a familiar pandas-like API but runs completely on the GPU. It works exceptionally well and fully utilizes the L4's architecture to crunch through massive datasets in a fraction of the time.

* 🕵️ **Quality Checks:** Using smaller models or rules-based checks to evaluate and score data quality.
* 🧬 **Feature Generation:** Producing derived features or intermediate products to support downstream modelling.

---

## 🌍 Term 2 Focus: Scaling & Multi-GPU Testing 📈

In the second term, our focus will shift toward larger-scale model training 🧠. The L4s will transition into a **testing and staging ground** 🚧 before we move workloads to a much larger supercomputer cluster equipped with several NVIDIA A100s.

You will use the L4 environment to:
* 🗺️ Map out the exact steps and scripts required for large-scale training jobs.
* 🐛 Test and debug multi-GPU communication and memory allocation.
* ✅ Validate **Distributed Data Parallel (DDP)** or **Fully Sharded Data Parallel (FSDP)** configurations.



Testing distributed strategies on the L4s is critical 🎯. By ensuring that DDP and FSDP are running perfectly here first, we can confidently pipe the jobs off to the larger A100 supercomputer without wasting expensive, high-tier compute time on configuration errors 💸.

---

## ⚠️ Usage Reminder 🚦

Because these are stepping stones for larger jobs and vital for data cleaning, please ensure you:
* 🟢 **Only request a GPU when actively running a workload.**
* 🔴 **Release the GPU immediately after your job finishes.** * 💻 **Do your standard code writing and EDA on the CPU profiles.**
