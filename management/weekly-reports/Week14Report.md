# Week 14 Report 🗂️

**Week:** Week 14  
**Date:** 2026-08-24  
**Attendees:** Matt, Kecheng, Junling, Olivia, Adam, Dylan

---

## Agenda

1. Confirm access to the full ACCESS-SY wind dataset and review its structure.
2. Confirm the privacy and storage requirements for source and derived data.
3. Finish the remaining data-understanding work and prepare small test datasets.
4. Review the decision to use genuine hourly states without temporal interpolation.
5. Start assembling and testing the CRAFT model pipeline.
6. Confirm the initial one-hour prediction step and six-hour forecast horizon.

## Discussion

> The full ACCESS-SY wind dataset is now available in the Jupyter environment at `BOM_Data/access_sy_wind_de_uwnd10m_de_vwnd10m.nc`. It is approximately 139 GB and contains about 26,000 hourly atmospheric states from September 2020 to May 2024. Each state is a 744 × 892 grid with the 10 m U and V wind components, `de_uwnd10m` and `de_vwnd10m`.
>
> The source dataset is read-only. The source data and every derived dataset must remain private to the project and must not be uploaded to public repositories, external storage, or shared outside the team. Temporary outputs and small test datasets can be written to the shared Scratch directory. Scratch is visible to the team but is non-persistent, so it must not be the only location used for important work.
>
> The sample notebook at `BOM_Data/SampleNotebook.ipynb` provides a starting point for loading and inspecting the data. Any remaining work on dimensions, spatial or temporal selections, plotting, and sample creation should use CPUs. GPUs will be reserved for model training after the small-scale pipeline works correctly.
>
> Several methods were tested for interpolating the hourly states into shorter intervals, including linear and cubic interpolation, PCHIP, Farnebäck optical flow, DIS, DeepFlow, RAFT, and RIFE. Farnebäck and RIFE produced the strongest results, but the improvement was not enough to justify synthetic data and extra pipeline complexity. Development will therefore continue with the genuine hourly ACCESS-SY states.
>
> The immediate CRAFT goal is to pass a small dataset through the complete structure: load data → encoder → latent representation → temporal evolution → decoder → output. The first forecast setup will predict one hour at a time over an initial horizon of approximately six hours. This stage checks data flow, tensor interfaces, and model execution rather than forecast quality.

## Decisions

- Use the genuine hourly ACCESS-SY states without interpolation for the current model pipeline.
- Keep the full source dataset read-only and keep all derived datasets private to the project.
- Use the shared Scratch directory only for temporary test datasets, model inputs, outputs, and intermediate files.
- Use CPUs for data inspection, plotting, subsetting, and test-dataset preparation.
- Create several small datasets that are manageable enough for end-to-end development tests.
- Start with one-hour-ahead prediction and an initial forecast horizon of approximately six hours.
- Confirm the full CRAFT data flow at small scale before increasing the training data or GPU resources.

## Action Items

| Action | Owner | Due |
|--------|-------|-----|
| Confirm access to the ACCESS-SY NetCDF dataset and inspect its dimensions, coordinates, variables, and time range | All team members | Start of Week 14 |
| Review `BOM_Data/SampleNotebook.ipynb` | All team members | Start of Week 14 |
| Finish any remaining ACCESS-SY data-understanding work using CPU resources | All team members | End of Week 14 |
| Create a few small hourly U/V wind datasets and store temporary copies in Scratch | Dylan, Kecheng | End of Week 14 |
| Define the input, latent, temporal-evolution, and output tensor interfaces | Junling, Kecheng, Olivia | End of Week 14 |
| Run a small dataset through the encoder, latent representation, temporal evolution, and decoder | Junling, Kecheng, Olivia | End of Week 14 |
| Verify one-hour prediction steps over an initial six-hour horizon | Junling, Kecheng, Olivia | End of Week 14 |
| Review data handling and CRAFT architecture together at the Monday meeting | Matt and project team | 2026-08-24, 10:00 AM |

## Progress Summary

> The project can now move from initial data review into model implementation. The full hourly ACCESS-SY wind dataset is available, the interpolation question has been resolved, and the immediate task is to create small private test datasets and pass them through the complete CRAFT structure. Forecast accuracy and large-scale GPU training are not the focus yet.

## Completed This Week

- Made the full ACCESS-SY wind dataset available in the Jupyter environment.
- Confirmed the dataset size, time coverage, spatial dimensions, and wind variables.
- Provided a sample notebook for reading and inspecting the ACCESS-SY data.
- Confirmed that the main dataset is read-only.
- Confirmed the privacy requirements for both source and derived datasets.
- Made the shared Scratch directory available for temporary project work.
- Reviewed several temporal-interpolation methods and decided not to add synthetic intermediate states at this stage.
- Confirmed that the initial CRAFT setup will work directly with genuine hourly states.

## In Progress

- Finishing the remaining ACCESS-SY data inspection and validation.
- Preparing small hourly U/V wind datasets for development tests.
- Defining the CRAFT encoder, latent representation, temporal-evolution, and decoder interfaces.
- Building a small-scale notebook implementation of the complete model flow.
- Preparing the one-hour-ahead, six-hour-horizon forecast setup.

## Blockers

> No active technical blocker has been identified. Scratch is non-persistent, so important code, configuration, and experiment records need a persistent project copy. The data and derived samples must remain inside the private project environment.

## Plan for Next Week

- Confirm that the small ACCESS-SY datasets pass through the complete CRAFT pipeline without shape or data-loading errors.
- Run the first small-scale training and reconstruction tests.
- Add a chronological validation split and basic forecast checks.
- Record tensor shapes, data normalization choices, and model interfaces.
- Resolve issues found during the first forward and backward passes.
- Begin increasing data volume and GPU use only after the small-scale flow is reliable.

## Next Meeting

**Date:** 2026-08-24  
**Time:** 10:00 AM  
🙂
