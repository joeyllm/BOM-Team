# 🛑 Best Practices & Pipeline Testing

Working with a 60 TB dataset requires a different mindset than working with small local files. This document outlines the mandatory workflow for developing and testing your data cleaning pipelines.

---

## 🔬 The Development Workflow: "Look, Pull, Test"

While you can see the entire `fineweb` folder in your root directory, you should think of it as a library to browse, not a workspace to run code against immediately.

### 1. The "Look" Phase (Understanding Structure)
Use the `fineweb` folder to understand the directory hierarchy and the schema of the Parquet files. Peek at the first few rows to see what columns are available and what noise (HTML tags, boilerplate, etc.) needs to be cleaned.

### 2. The "Pull" Phase (Creating a Sandbox)
**Do not run your experimental code against the main 60 TB folder.** Instead, "pull" a tiny subset into your personal directory. We recommend copying exactly **5 Parquet files** into a folder in your own 50 GB workspace.
* This gives you roughly 10 GB of data to work with.
* It is large enough to see if your code handles edge cases.
* It is small enough that if your code crashes or creates an infinite loop, it won't impact the server's NFS performance for everyone else.

```bash
# Example: Creating a local testing directory in your terminal
mkdir ~/my_pipeline_test
cp fineweb/sample_01.parquet ~/my_pipeline_test/
cp fineweb/sample_02.parquet ~/my_pipeline_test/
# ... and so on up to 5 files
```

### 3. The "Test" Phase (Verifying Results)
Run your cleaning script against your local 5-file folder. 
* **Check the output:** Does the cleaned data look exactly how you expected?
* **Check the logs:** Did the script run without memory errors (OOM)?
* **Check the speed:** Based on how long 5 files took, how long will 5,000 files take?

---

## ⚙️ Transitioning to Production

Once your pipeline produces the expected results on your 5-file sandbox, you are ready to scale.

### From Notebook to Script
Jupyter Notebooks are great for exploration, but they are inefficient for massive data runs. Before moving to the full dataset:
1. Export your notebook as a `.py` Python script.
2. Ensure all `del` and `gc.collect()` commands are in place for memory management.
3. Coordinate with Matthew to schedule a background run across the full dataset.

### 🔄 The "Pipeline is the Prize"
Remember the warning in the `README.md`: **Your code is more important than the data.** If your 5-file test run works perfectly, **commit that code to GitHub immediately.** If the server is reset or your local 10 GB test folder is wiped, you haven't lost anything because your "recipe" (the code) is safely backed up.

---

## 📝 Summary Checklist
- [ ] I have looked at the data structure in the `fineweb` folder.
- [ ] I have copied a **maximum of 5 files** to my personal directory for testing.
- [ ] My cleaning code runs on those 5 files without crashing the kernel.
- [ ] I have verified that the output data is correctly cleaned.
- [ ] I have committed my pipeline script to GitHub.
