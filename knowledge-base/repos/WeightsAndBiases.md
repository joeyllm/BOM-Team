# 📈 Weights & Biases (W&B)

**Weights & Biases (W&B)** is our central dashboard for tracking machine learning experiments, logging datasets, and monitoring model performance. 

Let's be incredibly clear up front: **Using this tool for our model training and pipeline building is MANDATORY!!!**

---

## 📅 Timeline: Start Learning Now

While we probably won't be using W&B heavily until later in the semester (when we shift focus from data cleaning to actively training models), **you need to get familiar with it right now.**

Do not wait until you are trying to debug a complex distributed training run across multiple GPUs to learn how our logging system works! 

---

## 🔍 Why We Use W&B

When training forecasting models or running large data pipelines, you cannot rely on printing metrics to a Jupyter notebook cell. You need a persistent, visual, and collaborative record of every single experiment.



We use W&B to track:
* **Loss Curves & Accuracy:** Watching the model learn (or fail to learn) in real-time.
* **System Metrics:** Monitoring CPU, RAM, and GPU VRAM usage across our L4s to catch memory leaks or processing bottlenecks.
* **Hyperparameters:** Recording the exact settings (learning rate, batch size, etc.) used for every single run so our results are 100% reproducible.
* **Artifacts:** Versioning our cleaned dataset pipelines and model checkpoints so we never lose our work.

---

## ✅ Your Action Items

Since you need to be comfortable with this by the time we start training, here is your homework for the early part of the semester:

1. **Create an Account:** Head over to [wandb.ai](https://wandb.ai) and set up your account (we recommend signing up with your GitHub).
2. **Read the PyTorch Docs:** Look up how seamlessly the `wandb` library integrates with PyTorch training loops. 
3. **Run a Toy Example:** Write a tiny, basic Python script in your CPU notebook that logs a dummy metric (like a simple math loop) to a W&B project just to see how the connection and the dashboard work.

By the time we hit the heavy model training phase later this year, initializing a W&B run should be second nature!
