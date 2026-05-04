Session Notes: Live API Integration & UNet Performance Evaluation
Date: 2026-05-04
Focus: Live Feed Ingestion, UNet Training Validation, and CSI Metric Analysis

What We Achieved
UNet Baseline Deployment: Successfully trained our first UNet architecture on the temporal chunks of ERA5 data. The model is actively predicting the 4th frame (15-minute intervals) based on the previous 3 hours of historical context.

BoM API Integration: Transitioned from static NetCDF files to testing the live Bureau of Meteorology (BoM) API feeds. Sana finalized his custom data loader, successfully pulling and structuring the live radar data into the required Numpy arrays.

Loss Function Transition: Completely phased out Mean Squared Error (MSE) in favor of the Critical Success Index (CSI). This gives us a much more accurate representation of our model's spatial accuracy for precipitation events.

Metric Validation: Evaluated the UNet against our Persistence Baseline (the assumption that the weather won't change). The UNet demonstrates a clear advantage in retaining predictive skill past the 15-minute mark.

The Technical Roadblocks
API Rate Limiting: We are currently hitting rate limits when polling the live BoM feeds too aggressively. Ryan and Cameron are working on a caching middle-layer to hold the most recent payload so we do not ping the server unnecessarily.

Edge-Case Blurring: The UNet is occasionally producing "blurry" predictions for highly localized, intense convective storms (high CAPE environments). It seems to be smoothing out extreme values to minimize overall error.

Resource Constraints: Training the UNet on the full spatial grid is bottlenecking our GPU resources. Jahin is investigating whether we can use mixed-precision training (FP16) to speed up the batches without losing predictive resolution.

Game Plan for Next Session
Step 1: Hyperparameter Tuning
Adjust the UNet's convolutional layers and introduce Dropout to see if it reduces the smoothing effect on high-intensity storms. We need the model to commit to predicting severe events rather than hedging its bets.

Step 2: API Caching Implementation
Deploy the caching middle-layer script to manage the BoM data flow. We need a stable, uninterrupted feed to run a true "live" test of the 10-15 minute nowcast.

Step 3: Visualization Dashboard
Begin drafting the frontend UI to display the model's predictions side-by-side with the actual observed weather as it happens.

<img width="1024" height="559" alt="image" src="https://github.com/user-attachments/assets/4e09265e-a1b0-4c4d-b5a6-684fdc032d4f" />
