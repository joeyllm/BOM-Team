# Nowcasting Research Project: Core Features

### 1. The "Algorithm Sandbox" (Standardized API Wrappers)
* **Description:** A standardized input/output wrapper for all predictive models.
* **Research Value:** This allows the team to drop in a completely new algorithm (e.g., a Random Forest or a different neural network) halfway through the project without having to rewrite the data ingestion or UI visualization layers. If an experimental algorithm fails entirely, it fails in isolation without bringing down the pipeline.

### 2. Historical Replay Engine (The "Time Machine")
* **Description:** A pipeline execution mode that allows historical, timestamped radar and sensor data to be fed into the models as if it were streaming in real-time.
* **Research Value:** This enables reliable backtesting of algorithms against specific historical weather events (like sudden storms or sensor outages). It allows for direct comparison of a model's 10-to-15-minute prediction against the actual ground-truth data that occurred 15 minutes later.

### 3. Granular Telemetry & Performance Logging
* **Description:** An automated logging system that records not just the final prediction, but the execution metadata: computing time, memory usage, algorithm latency, and error metrics (e.g., Mean Absolute Error) for every single run.
* **Research Value:** If a complex model is slightly more accurate but takes 12 minutes to generate a 10-minute forecast, it is operationally useless. This feature provides the quantitative data required to write robust research conclusions regarding the trade-offs between computational speed and predictive accuracy.

### 4. Dynamic "Side-by-Side" Evaluation Dashboard
* **Description:** A UI dashboard that visualizes the outputs of multiple algorithms (e.g., Baseline Persistence vs. Optical Flow vs. ConvLSTM) layered over or placed next to the actual ground-truth data.
* **Research Value:** Visualizing the data makes it instantly apparent if an algorithm is hallucinating, lagging, or over-predicting intensity. It shifts the research focus from finding a "perfect" model to defining the specific conditions under which each model excels or breaks.

### 5. Automated "Graceful Degradation" (Fallback Logic)
* **Description:** A built-in timeout and fallback mechanism within the pipeline. If a primary experimental algorithm does not return a result within a strict time limit (e.g., 60 seconds), the system automatically defaults to serving the baseline Persistence model output.
* **Research Value:** This demonstrates that the system architecture is robust enough for real-world operational use. It ensures the pipeline survives and continues providing data even if a newly deployed research algorithm hangs or fails catastrophically.

### 6. The "Frankenstein" Ensemble Builder
* **Description:** A customizable module that ingests the outputs of all active algorithms and applies adjustable weights to create a single, unified forecast.
* **Research Value:** This allows the team to experiment with combining the spatial tracking of Optical Flow with the stability of the Persistence model. It provides a testing ground to see if dynamically weighting models based on their performance over the previous hour yields a better 15-minute forecast than any single algorithm running in isolation.
