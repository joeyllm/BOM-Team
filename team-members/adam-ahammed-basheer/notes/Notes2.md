Session Notes: Short-Range Forecasting & Model Integration
Date: 2026-04-06

Focus: Model Training Setup, Temporal Resolution Scaling, and Pipeline Validation

What We Achieved
Environment Stability: Confirmed that the local source installation of PyEarthTools from the previous session is holding steady. No further sub-module linking errors or cache-miss bugs in /opt/venv/.

Temporal Resampling: Successfully modified build_pipeline.py to handle high-frequency data. While ERA5 is hourly, we implemented a linear interpolation layer to simulate the 10-15 minute intervals required for our nowcasting objective.

Feature Engineering:

Isolated Total Precipitation (tp) and Convective Available Potential Energy (CAPE) as our primary target variables.

Mapped these to a 2D Numpy grid suitable for a Convolutional Neural Network (CNN) architecture.

The Clean Run: Verified that ingest_era5.py and build_pipeline.py can now run end-to-end in under 4 minutes, creating a ready-to-use .npy stack for training.

The Technical Roadblocks
Memory Overflow (OOM): Attempting to load a 15-minute interpolated dataset for a full year crashed the system RAM. The PyEarthTools pipeline isn't natively "lazy-loading" these interpolated frames.

Normalization Drift: Noticed that extreme weather events in the ERA5 set (e.g., 2011 storms) were being clipped by our standard scaler. We need a RobustScaler to handle these outliers without losing the "signal" of high-impact weather.

Latency Issues: The interpolation logic adds a 1.2-second overhead per batch, which might be too slow for a real-time 10-minute prediction window if we scale to larger geographic regions.

Optimization & Refactoring
Chunked Loading: Reconfigured the pipeline to process data in monthly chunks rather than full-year arrays to prevent memory crashes.

Cache Hardening: Added a pre-run script clear_cache.py that automatically targets ~/.pyearthtools if a data integrity check fails, preventing the "permanent error" state encountered in Sprint One.

Game Plan for Next Session
Step 1: Baseline Model Implementation
Draft train_baseline.py. We will start with a Persistence Model (predicting that the next 15 minutes will look exactly like the last 15) to create a benchmark for our ML model to beat.

Step 2: Persistence vs. UNet
Introduce a basic UNet architecture (commonly used in satellite/radar nowcasting).

Input: 3 consecutive hourly frames (interpolated to 15-min intervals).

Output: Prediction of the 4th frame.

Step 3: Real-time API Integration
Research the Bureau of Meteorology (BoM) / Global Forecast System (GFS) real-time API feeds.

The Goal: Transition from training on historical ERA5 data to "warming up" the model with live data feeds to see if the 10-minute prediction holds up in a live environment.

Step 4: Loss Function Refinement
Move from standard Mean Squared Error (MSE) to a Critical Success Index (CSI) or Fractions Skill Score (FSS), which are better at measuring if we actually predicted a storm in the right place, not just the right intensity.
