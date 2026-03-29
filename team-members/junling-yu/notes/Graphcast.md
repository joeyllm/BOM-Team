# 📘 GraphCast  
*(Deterministic Weather Forecasting Model)*

## 1. Problem  
GraphCast aims to predict the future state of the atmosphere using historical weather data.  
The task is **medium-range forecasting**, typically from a few hours up to several days.

Formally:
- Learn a mapping from current state to future state  
- `X_t → X_{t+Δt}`

It focuses on:
- Wind (u, v components)  
- Temperature  
- Pressure  

This is a **deterministic forecasting problem**, meaning the model outputs a single best estimate.

---

## 2. Data Representation  

GraphCast represents the Earth’s atmosphere as a **graph instead of a grid**.

- Each **node** = one grid cell (latitude–longitude point)  
- Each **edge** = spatial relationship between neighbouring cells  
- Each **feature** = meteorological variables (e.g. wind, pressure)

This allows the model to:
- Capture spatial interactions directly  
- Model how weather moves across regions  

---

## 3. Model Architecture  

The model follows an **encoder–processor–decoder structure**:

### Encoder  
- Converts raw weather variables into latent node features  

### Processor (Core component)  
- Multiple layers of **graph message passing**  
- Each node updates its state using neighbouring nodes  

**Key idea:**  
> Weather evolves through interactions between nearby regions  

This is similar to attention, but constrained by graph structure.

### Decoder  
- Converts updated node features into predicted weather variables  

---

## 4. Temporal Modelling  

GraphCast uses **single-step prediction + autoregressive rollout**:

- Predict:
  - `t → t+6h`
- Then reuse output:
  - `t+6h → t+12h`, etc.

This enables multi-step forecasting without training separate models.

---

## 5. Training  

- Supervised learning  
- Input: current weather state  
- Target: next timestep (e.g. +6h)

**Loss:**
- Mean Squared Error (MSE) across variables  

Training is typically:
- Single-step prediction  
- No explicit modelling of uncertainty  

---

## 6. Inference  

- Start from initial condition  
- Repeatedly apply the model (rollout)

**Key issue:**
- Error accumulation over long horizons  

---

## 7. Strengths & Limitations  

### Strengths  
- Strong spatial modelling (captures wind propagation)  
- Fast inference (much faster than NWP)  
- Works well for large-scale atmospheric dynamics  

### Limitations  
- Deterministic → no uncertainty estimation  
- Errors compound during rollout  
- Cannot represent multiple possible futures  

---

## 8. Key Insight  

> GraphCast learns the dynamics of the atmosphere as a spatial system using graph-based message passing.

---

