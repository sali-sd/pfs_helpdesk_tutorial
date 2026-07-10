# PFS Data Products

This page describes the main PFS spectroscopic data products produced by the 2D DRP pipeline.
They are all FITS files and follow a strict naming convention based on observation identifiers.

---

## pfsConfig

**Filename:** `pfsConfig-0x{pfsDesignId:016x}-{visit:06d}.fits`

`pfsConfig` records the *realised* fiber configuration for a specific exposure.
It is the as-observed counterpart to `pfsDesign`, capturing where each fiber
actually ended up on the focal plane (as opposed to where it was intended to be).

**FITS structure:**

| HDU | Name | Type | Description |
|-----|------|------|-------------|
| #0 | PDU | Header | Actual telescope boresight RA/Dec (degrees) |
| #1 | CONFIG | Binary table | Per-fiber target and position data |
| #2 | PHOTOMETRY | Binary table | Per-fiber flux measurements in multiple filters |

**CONFIG table columns (key fields):**

| Column | Type | Description |
|--------|------|-------------|
| `fiberId` | 32-bit int | Fiber identifier (starts at 1) |
| `catId` | 32-bit int | Source catalog identifier |
| `objId` | 64-bit int | Unique object identifier |
| `ra`, `dec` | 64-bit float | Target position (degrees) |
| `targetType` | 32-bit int | Target class (SCIENCE=1, SKY=2, FLUXSTD=3, UNASSIGNED=4, ...) |
| `fiberStatus` | 32-bit int | Fiber health (GOOD=1, BROKENFIBER=2, BLOCKED=3, BLACKSPOT=4, ...) |
| `pfiNominal` | 2×32-bit float | Intended fiber position on the focal plane (mm) |
| `pfiCenter` | 2×32-bit float | Actual measured fiber position on the focal plane (mm) |
| `proposalId` | string | Subaru proposal ID (e.g. `S24B-001QN`) |
| `obCode` | string | Observing Block code within a proposal |

**PHOTOMETRY table columns (key fields):**

| Column | Units | Description |
|--------|-------|-------------|
| `fiberFlux` | nJy | Flux within ~1 arcsec fiber aperture (seeing-corrected) |
| `psfFlux` | nJy | Flux from PSF fitting to infinite radius |
| `totalFlux` | nJy | Total flux (PSF for point sources; extended model for galaxies) |
| `filterName` | — | Filter name specifying the transmission curve |

---

## pfsArm

**Filename:** `pfsArm-{visit:06d}-{arm}{spectrograph}.fits`

`pfsArm` contains the wavelength-calibrated, **not flux-calibrated** extracted spectra
for all fibers in a single spectrograph arm from a single exposure.
Each arm (`b`=Blue, `r`=Red, `n`=IR, `m`=Medium-resolution red) produces a separate file.
The wavelength grid is not required to be uniform — a wavelength array is stored per pixel.

**FITS structure:**

| HDU | Name | Type | Units | Dimensions |
|-----|------|------|-------|------------|
| #0 | PDU | Header | — | — |
| #1 | FIBERID | Image | — | NFIBER |
| #2 | WAVELENGTH | Image | nm (vacuum) | NROW × NFIBER |
| #3 | FLUX | Image | electrons | NROW × NFIBER |
| #4 | MASK | Image | bitmask | NROW × NFIBER |
| #5 | SKY | Image | electrons | NROW × NFIBER |
| #6 | NORM | Image | electrons | NROW × NFIBER |
| #7 | COVAR | Image | — | NROW × 3 × NFIBER |
| #8 | CONFIG | Binary table | — | 1 row (pfsDesignId, visit) |
| #9 | NOTES | Binary table | — | NFIBER rows |

The `COVAR` HDU stores the near-diagonal part of the flux covariance matrix:
diagonal (`±0`), first off-diagonal (`±1`), and second off-diagonal (`±2`) terms.

---

## pfsMerged

**Filename:** `pfsMerged-{visit:06d}.fits`

`pfsMerged` combines the spectra from all arms for a single visit into one file.
It is wavelength-calibrated but **not flux-calibrated**.
The format is identical to `pfsArm`, with two differences:

- Flux units are **electrons per nm** (rather than electrons)
- The `WAVELENGTH` array may be a single shared array applied to all fibers
  (rather than one per fiber), if all fibers share the same wavelength sampling

---

## pfsCalibrated

`pfsCalibrated` is a **visit-level bundle** of flux-calibrated, arm-merged spectra for
all science objects in a single visit, stored in a single file. The individual spectrum
for each object within this file is called **`pfsSingle`**.

### pfsSingle (individual spectrum)

**Filename:** `pfsSingle-{catId:05d}-{tract:05d}-{patch}-{objId:016x}-{visit:06d}.fits`

`pfsSingle` is the **flux-calibrated**, arm-merged spectrum for a single object from a
single visit — one file per science target per visit. It shares the same FITS format
as `pfsObject` (described below). The `pfsCalibrated` file is essentially a bundling
of all `pfsSingle` spectra from a visit into one file, following the same format as `pfsCoadd`.

---

## pfsCoadd

`pfsCoadd` is the **multi-visit coadded** spectral data product, introduced with the
LSST Gen3 middleware in late 2024. It bundles the coadded spectra of **many objects**
(grouped by `catId` and `objGroup`) into a single file, making pipeline I/O far more
efficient than the older per-object approach. The individual coadded spectrum for a
single object within this file is called **`pfsObject`**.

### pfsObject (individual spectrum)

**Filename:** `pfsObject-{catId:05d}-{tract:05d}-{patch}-{objId:016x}-{nVisit%1000:03d}-0x{pfsVisitHash:016x}.fits`

`pfsObject` is the **coadded, flux-calibrated spectrum** for a single object across
multiple visits. The filename encodes the number of visits (`nVisit`, modulo 1000) and
a 63-bit SHA-1 hash of the contributing visits (`pfsVisitHash`) to uniquely identify
the combination. Files are organised on disk as `catId/tract/patch/pfsObject-*.fits`.

**FITS structure:**

| HDU | Name | Type | Units | Dimensions |
|-----|------|------|-------|------------|
| #0 | PDU | Header | — | — |
| #1 | FLUX | Image | nJy | NROW |
| #2 | MASK | Image | bitmask | NROW |
| #3 | TARGET | Binary table | — | NFILTER rows |
| #4 | SKY | Image | nJy | NROW |
| #5 | COVAR | Image | — | NROW × 3 |
| #6 | COVAR2 | Image | — | NCOARSE × NCOARSE |
| #7 | OBSERVATIONS | Binary table | — | NOBS rows |
| #8 | FLUXTABLE | Binary table | nJy, nm | NOBS × NROW rows |
| #9 | NOTES | Binary table | — | — |

The `FLUX`, `MASK`, `SKY`, and `COVAR` HDUs use WCS cards (`CRPIX1`, `CRVAL1`) to
define the wavelength axis, sampled at ~0.8 Å/pixel.
The `FLUXTABLE` HDU stores the un-resampled, per-visit wavelength and intensity arrays
and should be used for highest-precision analysis.

**TARGET HDU keywords (minimum required):**

| Keyword | Type | Description |
|---------|------|-------------|
| `catId` | INT | Catalog identifier |
| `tract` | INT | Sky tract identifier |
| `patch` | STRING | Sky patch identifier |
| `objId` | INT | Object identifier |
| `ra`, `dec` | DOUBLE | Object position (degrees) |
| `targetType` | INT | Target type enum |

### pfsCoadd (bundled file)

**Filename:** `pfsCoadd-{catId:05d}-{objGroup:05d}.fits`

**Filename:** `pfsCoadd-{catId:05d}-{objGroup:05d}.fits`

`pfsCoadd` is the modern replacement for `pfsObject`, introduced with the LSST Gen3
middleware in late 2024. Instead of one file per object, it bundles the coadded spectra
of **many objects** (grouped by `catId` and `objGroup`) into a single file, making
pipeline I/O far more efficient.

**FITS structure:**

| HDU | Name | Type | Units | Description |
|-----|------|------|-------|-------------|
| #0 | PDU | Header | — | — |
| #1 | TARGET | Binary table | — | One row per object (targetId, catId, tract, patch, objId, ra, dec, targetType) |
| #2 | TARGETFLUX | Binary table | nJy | Per-object flux per filter (fiberId, filterName, fiberFlux) |
| #3 | OBSERVATIONS | Binary table | — | Per-visit observation metadata (visit, arm, spectrograph, pfsDesignId, fiberId, pfiNominal, pfiCenter, obsTime, expTime) |
| #4 | WAVELENGTH | Image/table | nm (vacuum) | Wavelength arrays |
| #5 | FLUX | Image/table | nJy | Coadded flux |
| #6 | MASK | Image/table | bitmask | Quality bitmask |
| #7 | SKY | Image/table | nJy | Coadded sky spectra |
| #8 | COVAR | Image/table | — | Near-diagonal covariance (3 arrays per spectrum) |
| #9 | COVAR2 | Image/table | — | Low-resolution non-sparse covariance |
| #10 | METADATA | Binary table | — | Per-object YAML key-value metadata |
| #11 | FLUXTABLE | Binary table | nJy, nm | Un-resampled per-visit wavelength, flux, error, mask arrays |
| #12 | NOTES | Binary table | — | Reduction notes |

When all spectra share the same wavelength sampling (the typical case), the
`WAVELENGTH`, `FLUX`, `MASK`, `SKY`, and `COVAR` HDUs are written as images,
enabling FITS tile compression. Otherwise they are written as binary tables.
