# Week 13 Report 🗂️

**Week:** Week 13  
**Date:** 2026-08-17  
**Attendees:** Matt, Kecheng, Junling, Olivia, Adam, Dylan

---

## Agenda

1. Confirm the Week 13 sprint goal and priorities.
2. Review the updated CRAFT paper and NVIDIA ATLAS.
3. Confirm the scope and time sequence of the initial ACCESS-SY dataset.
4. Discuss how the CRAFT architecture maps into a basic PyTorch model.

## Discussion

> The project has been renamed from SWIFT to CRAFT: Compressed Representation for Atmospheric Forecasting through Time.
>
> The team will finish reviewing the updated CRAFT paper and study NVIDIA ATLAS as a related latent-space weather forecasting model. The main focus is to understand the similarities and differences between the two approaches, particularly their spatial compression, latent representations, temporal forecasting, and decoding strategies.
>
> The initial ACCESS-SY test dataset will cover approximately 24 hours. The full hourly source data must be retained, while the first small Parquet dataset will contain five snapshots: T+0, T+6, T+12, T+18, and T+24. For this first test, the dataset will focus on the wind-related variables and channels. The hourly states will be used later when the finer 10-minute sequence is introduced.
>
> The 5th sprint goal is to prepare a basic working model of the CRAFT structure: ACCESS-SY data → Encoder → Latent State → Temporal Transformer → Decoder.

### Email clarification on the ACCESS-SY sequence

The team asked for clarification about how the hourly source data should be used for the initial 24-hour dataset:

![Email asking for clarification about the initial ACCESS-SY sequence](/Users/apple/.codex/.chatgpt-projects/g-p-69c9c06a59148191ae10dd9d564c4113/assets/week13-meeting/access-sy-clarification-question.png)

Matt confirmed that the complete hourly data should be retained, while the initial Parquet dataset should contain only the five six-hourly snapshots and focus on wind-related channels:

![Matt's response confirming the five ACCESS-SY snapshots](/Users/apple/.codex/.chatgpt-projects/g-p-69c9c06a59148191ae10dd9d564c4113/assets/week13-meeting/access-sy-clarification-response.png)

## Decisions

- Keep the complete hourly ACCESS-SY data without deleting intermediate hourly states.
- Use T+0, T+6, T+12, T+18, and T+24 for the initial Parquet test dataset.
- Limit the initial dataset to wind-related channels; additional variables can be added after the first pipeline is working.
- Complete the CRAFT and NVIDIA ATLAS paper review and document the main architectural differences.
- Start with a basic PyTorch model skeleton before moving to full training.
- Use JupyterHub directly without WireGuard for model development.

## Action Items

| Action | Owner | Due |
|--------|-------|-----|
| Prepare and verify the five-snapshot ACCESS-SY Parquet dataset | Dylan | End of Week 13 |
| Finish reviewing the updated CRAFT paper | Dylan, Junling, Kecheng, Adam, Olivia | End of Week 13 |
| Nvidia Atlas model structure understanding | Dylan, Junling Kecheng, Adam, Olivia| Week 14 |
| Basic implementation of CRAFT | Junling, Kecheng, Olivia | Week 15 |
| Data processing pipeline implementation | Kecheng | End of Week 13 |
| Git Issues and Management | Adam, Dylan | End of Week 13 |


## Progress Summary

> The team has moved from data-access and paper-update tasks toward the first implementation stage. The immediate priorities are a clean five-snapshot ACCESS-SY dataset, a shared understanding of CRAFT and ATLAS, and a basic model structure that can accept the initial data.

## Completed This Week

- Confirmed that JupyterHub is publicly accessible without WireGuard.
- Confirmed GitHub repository write access for the BOM team.
- Reviewed the updated project direction and the change from SWIFT to CRAFT.
- Clarified the initial ACCESS-SY temporal sequence with Matt.
- Confirmed that the first Parquet dataset should use five snapshots while preserving the full hourly source data.
- Confirmed that the first dataset should focus on wind-related channels.

## In Progress

- Preparing and validating the initial ACCESS-SY Parquet dataset.
- Completing the updated CRAFT paper review.
- Reviewing NVIDIA ATLAS and comparing its latent-space design with CRAFT.
- Defining the input, latent, temporal, and output tensor shapes.
- Translating the CRAFT architecture into a basic PyTorch model structure.

## Blockers

> No active blockers. The dataset timing question has been resolved. Model dimensions and detailed training settings will be refined during implementation.

## Plan for Next Week

- Pass the 24-hour five-snapshot dataset through the first CRAFT model skeleton.
- Check the tensor shapes and interfaces between the Encoder, Temporal Transformer, and Decoder.
- Run an initial forward pass and identify data-loading or architecture issues.
- Prepare for the first training and reconstruction tests.

## Next Meeting

**Date:** 2026-08-17  
🙂
