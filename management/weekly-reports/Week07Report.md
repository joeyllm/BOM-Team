# Week 7 Report 🗂️

**Week:** Week 7
**Date:** 2026-05-11
**Facilitator:** Adam
**Prepared by:** Adam

---

## Agenda

1. Sprint 3 Kickoff & Planning (Goals, Poker Planning, Standups)
2. Client Check-in & Alignment
3. Weather Data Pipeline (Collection, Cleaning, and Storage)
4. Satellite Data Research (Himawari 8/9 Feasibility & Alternatives)

## Discussion

> * **Sprint 3 Setup:** Held our initial standup, discussed the overarching sprint goals, and completed poker planning to estimate upcoming tasks. Also held the first client meeting for the sprint to ensure alignment.
> * **Weather & Wind Data:** Discussed the automated collection of daily weather observations from BOM and finding online wind data. Addressed the need to clean the data, drop empty columns, fix encoding issues (like the °C symbol), and merge everything into a single master dataset.
> * **File Formats:** Discussed the advantages of using Parquet over CSV for the master dataset to optimize for size, native datetime handling, and faster read speeds.
> * **Himawari 8/9 Research (Raw Data):** Evaluated the massive scale of the Himawari 8/9 public archive (~1 PB). Discussed strategies to reduce a subset to a manageable size (~20 TB) by cropping to the Australia/Oceania region, filtering to 4 key bands, and using 30-minute intervals. 
> * **Alternative Wind Dataset (NDMW):** Explored the **NOAA Derived Motion Winds (NDMW)** dataset as a highly processed alternative. Since these are Level-2 products (calculating wind speed, direction, and altitude directly from cloud/vapor tracking), they offer massive size reductions. They are also stored in standard `.nc` (NetCDF4) format, bypassing the need for complex `.DAT` block decoding or `.bz2` decompression.

## Decisions

- Use **Parquet** as the final storage format for the consolidated weather data to maintain native datetime objects (Unix Epoch Timestamps) and optimize performance.
- Use Python with `gcsfs`, `bz2`, and `satpy` for future Himawari `.DAT` file extraction instead of standard NetCDF readers, due to the specific 12-block Himawari Standard Format.
- **Evaluate the NOAA NDMW dataset** alongside the raw imagery to determine if using pre-calculated wind vectors will save computational resources and storage space for our upcoming experiments.

## Action Items

| Action | Owner | Due |
|--------|-------|-----|
| Execute the Himawari 8/9 data extraction script for the Australia subset | adambashbash | _[Date]_ |
| Review the combined Parquet weather dataset for quality assurance | _[Name]_ | _[Date]_ |
| Download a sample of NDMW `.nc` files and load them into a notebook | adambashbash | _[Date]_ |

## Progress Summary

> We successfully kicked off Sprint 3 with all planning ceremonies and client meetings completed. On the technical side, we made excellent progress on our data pipeline. We successfully established a method to scrape, clean, and merge BOM weather data into a single optimized Parquet file. Furthermore, we completed a deep-dive investigation into the Himawari 8/9 dataset, establishing a clear, actionable plan to extract a manageable subset for our region. Crucially, we also identified a Level-2 alternative (NOAA Derived Motion Winds) that could drastically reduce our processing overhead if wind tracking becomes our primary objective.

## Completed This Week

- ✅ Research Himawari 8,9 and its usefulness (Task #42)
- ✅ Sprint goal discussion (#41)
- ✅ Sprint 3 standup 1 (#40)
- ✅ Poker planning Sprint 3 (#39)
- ✅ Combine all data into one file (#38)
- ✅ Transfer from CSV to Parquet files (Task #37)
- ✅ Collect Data on wind from weather station information online (Task #36)
- ✅ Client meeting Sprint 3 1 (#35)

## In Progress

- _[List any tasks currently underway in Sprint 3]_

## Blockers

> None currently. We successfully navigated the technical hurdles regarding Himawari file formats (HSF/NetCDF) and compression (`.bz2`), and have viable alternative datasets if storage limits become an issue.

## Plan for Next Week

- Begin downloading and processing the cropped Himawari 8/9 satellite subset.
- Explore the NOAA NDMW `.nc` files to assess their structure and viability for our models.
- Start exploratory data analysis (EDA) on the newly combined Parquet weather and wind datasets.

## Next Meeting

**Date:** 2026-05-18
🙂
