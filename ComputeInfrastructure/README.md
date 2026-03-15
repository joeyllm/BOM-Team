# 🖥️ Compute Infrastructure

This repository contains the documentation for the compute infrastructure provided for the BOM Nowcasting project. 

The environment is designed to provide you with real research infrastructure, similar to what is used in industry and research labs. Each student receives their **own isolated notebook environment** running on a shared compute server, which can be used for data exploration, dataset cleaning, and machine learning experiments.

### System Architecture

    Student Laptop
          │
          ▼
    WireGuard VPN
          │
          ▼
    Compute Server
          │
          ├── 🧠 CPU Notebooks (Default)
          └── 🚀 GPU Notebooks (NVIDIA L4)

---

## 🚀 Getting Started

To access your environment, follow these three steps:

**1. Connect to the Network**
The compute infrastructure sits behind a secure internal network. You must first connect using a **WireGuard VPN**. *(See `Wireguard.md` for instructions).*

**2. Verify GitHub Access**
Authentication is handled via GitHub. Before logging in, ensure you have an active GitHub account and have been added to the project's GitHub team.

**3. Launch Your Notebook**
Once connected to the VPN:
* Open your local browser and navigate to the **JupyterHub login page** at `http://10.55.0.245`.
* Sign in using your **GitHub** credentials.
* Choose your compute profile and start your personal notebook environment. *(Note: You can work directly in Jupyter or use VS Code remote development).*

---

## ⚙️ Compute Profiles & Workflow

When starting your notebook, you will be prompted to choose a compute profile. Please use resources responsibly, as GPU access is shared across the team.

| Profile | 🧠 CPU Environment | 🚀 GPU Environment |
| :--- | :--- | :--- |
| **Specs** | Standard compute | NVIDIA L4 GPU (24 GB VRAM)* |
| **Best For** | Data exploration, dataset cleaning, analysis, and standard Python workflows. | Machine learning training, RAPIDS / CUDF workloads, and GPU-accelerated processing. |
| **Availability**| Plentiful | **Limited (6 total GPUs)** |
| **Usage Rule** | **Use this most of the time.** Start all your data prep here. | **Use only when needed.** Move your prepared dataset here for heavy workloads. |

*> Note: The NVIDIA L4 is roughly comparable to (and slightly better than) an NVIDIA A10 commonly used on AWS.*

---

## ⚠️ Best Practices

To keep the infrastructure responsive and fair for the entire team, please adhere to the following:
* **Default to CPU:** Do your exploratory work and code testing on the CPU environment.
* **Free Up Resources:** Always shut down your GPU sessions as soon as your workloads are finished.
* **Save Your Work:** Commit your code to GitHub regularly to prevent data loss.

---

## 📚 Documentation Index

Keep infrastructure notes practical and current. If access steps or machine details change, please update the relevant files below:

| File | Description |
| :--- | :--- |
| `Wireguard.md` | How to install and connect using the WireGuard VPN. |
| `BaseSystem.md` | High-level overview of the system and environment design. |
| `L4Gpu.md` | Details and specific instructions for the NVIDIA L4 GPU environment. |
