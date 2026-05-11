
## 1. Where the archive is hosted
### The archive is hosted on JAXA's P-Tree FTP site. Must request a free account via a registration form at https://www.eorc.jaxa.jp/ptree/registration_top.html. Once registered, can access it with an FTP client (FileZilla, WinSCP, etc.) major web browsers cannot connect to FTP directly.

*** Long-term Archive ***
Himawari Standard Data (HSD) older than 30 days is deleted from P-Tree.
For HSD going back to 2015, JAXA explicitly points users to two alternatives:
1. NICT World Science Data Bank
https://sc-web.nict.go.jp/himawari/
Run by Japan's National Institute of Information and Communications Technology. Full HSD archive.
2. DIAS — Data Integration and Analysis System (University of Tokyo)
https://auth.diasjp.net/
Academic archive, requires registration, holds full HSD back to 2015.
3. NOAA/AWS S3 (what we already discussed)
s3://noaa-himawari8 and s3://noaa-himawari9
Archive back to July 2015, publicly accessible with no account needed. This is genuinely the **easiest** long-term access path for researchers.

## 2. File formats and access methods
LayerFormatAccessHimawari Standard Data (HSD) Proprietary binary (closest to raw sensor)FTP → /jma/hsd/L1 Gridded (preferred for analysis)NetCDF, EQR projectionFTPGeophysical products (SST, aerosol, cloud, etc.)NetCDF (SST follows GHRSST GDS2.0)FTPWildfireCSVFTP

**NOAA AWS**
Bucket Folder Structure

AHI-L1b-FLDK/        ← raw imagery, full disk
AHI-L1b-Japan/       ← raw imagery, Japan rapid scan (2.5 min)
AHI-L1b-Target/      ← raw imagery, target area rapid scan
AHI-L2-FLDK-Clouds/       ← cloud mask, phase, height
AHI-L2-FLDK-ISatSS/       ← cloud moisture imagery tiles
AHI-L2-FLDK-RainfallRate/ ← rainfall rate
AHI-L2-FLDK-SST/          ← sea surface temperature
AHI-L2-FLDK-Winds/        ← derived motion winds  (most relevant) 

**Tier 1 : L1b Raw Imagery (HSD binary + bz2)**
The raw satellite data. The format is not NetCDF, it's a proprietary binary format.
L1b data is calibrated, navigated radiances in Himawari Standard Format (HSF), a unique binary data format : need to write reader, or use the sample C code provided by JMA. The ISatSS directory contains tiled NetCDF files specifically designed for use by the NOAA National Weather Service AWIPS software

**Tier 2 : L2 Derived Products (NetCDF)**
Already processed, standard NetCDF files. Much easier to work with directly in Python with xarray. All L2 products refresh every 10 minutes (except SST which is hourly), and include cloud moisture imagery, SST, cloud mask/phase/height, derived motion winds, and rainfall rate.
The Derived Motion Winds product is the most directly useful.

**Access** : AWS CLI
**Access via Python** : via boto3 / s3fs + xarray / satpy  

**Resolution Differences between L1 & L2**
L1b : Dense Continuous Raster Image
Every pixel in the image has a value. It's a regular grid covering the full disk:

## L1b — Dense Continuous Raster Image

| Band | Wavelength | Native Resolution | Full Disk Pixel Count |
|---|---|---|---|
| B03 | 0.64 µm VIS | **0.5 km** | ~22,000 × 22,000 |
| B01, B02, B04 | VIS/NIR | **1 km** | ~11,000 × 11,000 |
| B05–B16 | SWIR/IR/TIR | **2 km** | ~5,500 × 5,500 |


**L2 Derived Motion Winds : Sparse Irregular Point Cloud**
AMV data is not a grid at all. Wind estimates from the Derived Motion Winds algorithm are sparse and do not come with uncertainty measures.
Each "observation" is a single point with:
latitude, longitude, pressure_level, u_wind, v_wind, quality_flag

But those points are only generated where the algorithm found a trackable feature, a cloud edge, a water vapour swirl, etc. Where the sky is clear or featureless, there are simply no wind observations at all.
Typical density in practice is roughly one AMV vector every 50–100 km, and the distribution is highly irregular, dense over cloud systems, zero over clear ocean.

## L1b vs L2 — Key Properties

| Property | L1b Image | L2 AMV Winds |
|---|---|---|
| **Data structure** | Dense regular grid | Sparse irregular points |
| **Spatial coverage** | Complete (every pixel) | Only where clouds/WV features exist |
| **Resolution** | 0.5–2 km pixel size | ~50–100 km between points |
| **Vertical info** | None (2D image) | Each point has pressure level (3D) |
| **Format** | Binary HSD, needs satpy | NetCDF, opens with xarray directly |
| **What you get** | Raw radiance/brightness temp | u, v wind components + height |

## Wind Nowcasting — Which to Use

| Approach | Data | Pros | Cons |
|---|---|---|---|
| **L2 AMVs directly** | L2 NetCDF winds | Ready-to-use u/v/height, no computation | Sparse gaps over clear regions |
| **L1b + optical flow** | L1b HSD imagery | Complete spatial coverage | Must derive winds yourself |
| **L1b + deep learning** | L1b HSD imagery | Dense wind field output, learns from data | Needs training labels |
| **Combined (recommended)** | L1b input + L2 labels | Best of both — full coverage + height info | More complex pipeline |


## 3. Naming structure and metadata


## L1b File Naming Convention

### Path Pattern
AHI-L1b-FLDK / YYYY / MM / DD / HHmm / HS_aaa_YYYYMMDD_HHmm_Bbb_FLDK_Rjj_Skkll.DAT.bz2

### Real Example
AHI-L1b-FLDK/2024/01/15/0030/HS_H09_20240115_0030_B08_FLDK_R20_S0110.DAT.bz2

### Field Decoder

| Field | Position | Meaning | Possible Values |
|---|---|---|---|
| `HS` | Prefix | Himawari Standard Data | Always `HS` |
| `aaa` | Satellite | Satellite identifier | `H08` = Himawari-8, `H09` = Himawari-9 |
| `YYYYMMDD` | Date | Observation date UTC | e.g. `20240115` |
| `HHmm` | Time | Observation time UTC | `0000`–`2350` (every 10 min) |
| `Bbb` | Band | Band number | `B01`–`B16` |
| `FLDK` | Region | Coverage area | `FLDK` = full disk |
| `Rjj` | Resolution | Spatial resolution code | `R05`=0.5 km, `R10`=1 km, `R20`=2 km |
| `Skk` | Segment | Segment number (N→S) | `S01`–`S10` |
| `ll` | Total segs | Total segment count | `10` (always 10 for full disk) |

### Band × Resolution Reference

| Band | Wavelength | Type | Resolution Code | Resolution |
|---|---|---|---|---|
| B01 | 0.47 µm | VIS blue | R10 | 1 km |
| B02 | 0.51 µm | VIS green | R10 | 1 km |
| **B03** | **0.64 µm** | **VIS red** | **R05** | **0.5 km** |
| B04 | 0.86 µm | NIR | R10 | 1 km |
| B05 | 1.6 µm | SWIR | R20 | 2 km |
| B06 | 2.3 µm | SWIR | R20 | 2 km |
| B07 | 3.9 µm | SWIR/MWIR | R20 | 2 km |
| **B08** | **6.2 µm** | **WV upper** | **R20** | **2 km** |
| B09 | 6.9 µm | WV mid-upper | R20 | 2 km |
| **B10** | **7.3 µm** | **WV mid-lower** | **R20** | **2 km** |
| B11 | 8.6 µm | TIR | R20 | 2 km |
| B12 | 9.6 µm | Ozone | R20 | 2 km |
| **B13** | **10.4 µm** | **TIR window** | **R20** | **2 km** |
| B14 | 11.2 µm | TIR window | R20 | 2 km |
| B15 | 12.4 µm | TIR window | R20 | 2 km |
| B16 | 13.3 µm | CO₂ | R20 | 2 km |

> **Bold** = recommended 4 channels for wind nowcasting

---

## L2 Derived Motion Winds — File Naming

### Path Pattern
AHI-L2-FLDK-Winds / YYYY / JJJ / HH / NDMW-AHI-Cxx{CT|CS}_v1r0_h08_s{start}_e{end}_c{created}.nc
> Note: L2 paths use **day-of-year (JJJ)** not MM/DD

### Real Example
AHI-L2-FLDK-Winds/2024/015/00/NDMW-AHI-C08CT_v1r0_h08_s20240115000000000_e20240115001000000_c20240115001500000.nc

### Field Decoder

| Field | Meaning | Possible Values |
|---|---|---|
| `NDMW` | Product type — Derived Motion Winds | Always `NDMW` |
| `AHI` | Instrument | Always `AHI` |
| `Cxx` | Channel tracked | `C03`, `C07`, `C08`, `C09`, `C10`, `C14` |
| `CT` or `CS` | Tracking method | `CT` = cloud top, `CS` = cloud side |
| `v1r0` | Version | Algorithm version |
| `h08` | Satellite | `h08` = Himawari-8, `h09` = Himawari-9 |
| `s...` | Scan start | `YYYYMMDDhhmmsss` (UTC) |
| `e...` | Scan end | `YYYYMMDDhhmmsss` (UTC) |
| `c...` | File created | `YYYYMMDDhhmmsss` (UTC) |

### Wind Files Available Per Timestep

| Filename Pattern | Channel | Altitude Layer | Tracking Method |
|---|---|---|---|
| `NDMW-AHI-C03CT_...nc` | B03 — 0.64 µm VIS | Boundary layer | Cloud top |
| `NDMW-AHI-C07CT_...nc` | B07 — 3.9 µm SWIR | Low–mid level | Cloud top |
| `NDMW-AHI-C08CT_...nc` | B08 — 6.2 µm WV | Upper (~300–400 hPa) | Cloud top |
| `NDMW-AHI-C08CS_...nc` | B08 — 6.2 µm WV | Upper (~300–400 hPa) | Cloud side |
| `NDMW-AHI-C09CS_...nc` | B09 — 6.9 µm WV | Mid-upper (~450–550 hPa) | Cloud side |
| `NDMW-AHI-C10CS_...nc` | B10 — 7.3 µm WV | Mid-lower (~600–700 hPa) | Cloud side |
| `NDMW-AHI-C14CT_...nc` | B14 — 11.2 µm TIR | All cloud levels | Cloud top |

---

## L2 Refresh Rates

| Product | Refresh Rate | Format |
|---|---|---|
| Cloud Moisture Imagery (ISatSS) full disk | 10 minutes | NetCDF |
| Cloud Moisture Imagery R3 Tiles (rapid scan) | 2.5 minutes | NetCDF |
| Cloud Mask / Phase / Height | 10 minutes | NetCDF |
| Derived Motion Winds | 10 minutes | NetCDF |
| Rainfall Rate | 10 minutes | NetCDF |
| Sea Surface Temperature | 60 minutes | NetCDF |

---

## ISatSS (Cloud Moisture Imagery) Tile Naming
OR_HFD-rrr-Bxx-M1Cyy-Tzzz_GH8_sYEARJJJHHMMSS0_cYEARJJJHHMMSS0.nc

| Field | Meaning |
|---|---|
| `OR_HFD` | Full disk cloud moisture imagery |
| `rrr` | Resolution — `020`=2 km, `010`=1 km, `005`=0.5 km |
| `Bxx` | Bits per pixel |
| `Cyy` | Channel number |
| `Tzzz` | Tile number |
| `GH8` | Himawari-8 |
| `s...` | Scan start time |
| `c...` | File creation time |

---
