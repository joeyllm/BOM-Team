# 📘 GenCast  
*(Diffusion-based Probabilistic Forecasting)*

## 1. Problem  

GenCast addresses **probabilistic weather forecasting**.

Instead of predicting a single outcome, it models:

\[
p(X_{t+\Delta t} \mid X_t)
\]

That is:
- A **distribution of possible future states**

This is important for:
- Uncertainty estimation  
- Extreme weather prediction  

---

## 2. Data Representation  

Similar to GraphCast:
- Input: weather fields (grid/tensor form)  
- Variables:
  - wind (u, v)
  - pressure
  - temperature  

Additional concept:
- Noise is added during training (diffusion process)

---

## 3. Core Idea (Diffusion Process)  

Diffusion models work in two stages:

### Forward process  
- Gradually add noise to real data  

### Reverse process  
- Learn to remove noise step by step  

**Goal:**
> Recover realistic weather fields from noise  

---

## 4. Model Architecture  

The model consists of:

### Diffusion process  
- Runs over multiple timesteps (T steps)

### Denoising network  
- Typically Transformer or attention-based network  
- Predicts noise at each step  

### Conditioning  
- The model is conditioned on current weather:

\[
p(x_{future} \mid x_{current})
\]

---

## 5. Training  

- Train model to predict noise added to data  

**Loss:**
- L2 loss between predicted and true noise  

**Input:**
- Noisy weather field  
- Conditioning: current weather  

---

## 6. Inference  

- Start from random noise  
- Iteratively denoise  
- Generate one future sample  

Repeat multiple times:
