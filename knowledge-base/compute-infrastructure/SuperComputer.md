# 🌌 Scaling Up: The NCI (Gadi) & University Supercomputers

This document outlines our access to significantly larger compute clusters and the strict prerequisites for using them.

## 🚀 The Next Level of Compute

While our current system (with 110 cores and 6x L4 GPUs) is fantastic for building and testing, we also have access to much more powerful hardware: the **NCI's Gadi supercomputer** and the **University (ANU) HPC systems**. 

These larger systems are equipped with massive arrays of high-end GPUs (like the A100s) and are designed to handle the heavy lifting required for large-scale model training and massive dataset processing.

---

## 🧰 The HPC Software Stack: Slurm, PBS Pro, & Singularity

Unlike our local JupyterHub environment, supercomputers generally do not let you run heavy workloads interactively. You have to package your code and submit it to a queue. 

To use the NCI and ANU systems, you will need to become familiar with their specific software stacks:

* **Slurm & PBS Pro:** These are workload managers (job schedulers). University clusters typically use **Slurm**, while the NCI's Gadi supercomputer uses **PBS Pro**. Instead of clicking "run" in a notebook, you will write bash scripts to request resources (GPUs, RAM, time) and submit your jobs to the cluster's queue.


* **Singularity (Apptainer):** Supercomputers have strict, locked-down environments. You cannot just `pip install` whatever you want onto the host machine. Instead, you will build **Singularity** containers (similar to Docker) on our local system to package your code, libraries, and dependencies, and then execute that container on the supercomputer.

> **💡 Optional Self-Study:** > If you would like to get a head start on your own time, we highly recommend researching **PBS Pro**, **Slurm**, and **Singularity/Apptainer**. Looking into how to write a basic "job run" script or how to build a container will put you in a great position for Term 2.

---

## 📅 Timeline: Term 2 Access

Access to the Gadi and University systems is highly restricted and will **only become available during the second term**. 

More importantly, access is conditional. We will only transition workloads to these larger clusters **if we can demonstrate solid progress and highly optimized pipelines on our current L4 system first.**

---

## ✅ Prerequisites for Scaling

Supercomputer time at the NCI and the University is incredibly valuable, heavily monitored, and shared among many researchers. We cannot waste compute cycles on buggy code, unoptimized I/O, or broken multi-GPU configurations. 

Before any of your workloads are migrated, your code must prove itself on our current environment:

* **Proven Efficiency:** Your data cleaning and preprocessing scripts must be heavily optimized. You should be successfully and quickly processing data subsets on the current system before asking for more power.
* **Validated Pipelines:** Automated jobs must run flawlessly in the background without crashing, leaking memory, or bottlenecking storage.
* **Container & Queue Ready:** You must have your environments successfully containerized using Singularity, and have your multi-GPU configurations (like DDP or FSDP) mapped out and tested on the L4s.

By treating our current system as a rigorous testing ground in Term 1, we will be fully prepared to unleash the massive power of the Gadi and ANU systems in Term 2!
