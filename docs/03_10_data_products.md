# PFS Data Products

## Overview of PFS Data Products

This page describes the main PFS spectroscopic data products produced by the 2D DRP pipeline.
They are all FITS files and follow a strict naming convention based on observation identifiers.

---

## Accessing PFS Data Products

All PFS data products are stored in **collections** within a Gen3 butler repository.
A collection is a named, logical grouping of datasets — typically tied to a specific
processing run or observing programme — that allows the butler to locate the correct
version of the data when multiple reductions exist in the same repository.

Data is accessed using the [LSST Gen3 Butler](https://pipelines.lsst.io/modules/lsst.daf.butler/index.html),
which provides a uniform interface for reading and writing pipeline products without
needing to know the exact file paths on disk.

**Setting up the butler:**

```python
from lsst.daf.butler import Butler

repo        = "/shared/pfs/programs/S25A-000QF/2d/"  # path to the datastore (PFS Filler Program)
collections = "S25A_April2026"                        # named processing collection

butler = Butler(repo, collections=collections)
```

**Querying available visits:**

```python
all_visits = sorted({ref.dataId['visit'] for ref in butler.registry.queryDatasets('pfsMerged')})
print(f"Total visits in collection: {len(all_visits)}")
```

**Loading a data product:**

```python
pfsConfig = butler.get('pfsConfig', dict(visit=122041))
pfsMerged = butler.get('pfsMerged', dict(visit=122041))
```

The string passed to `butler.get()` (e.g. `'pfsConfig'`, `'pfsMerged'`) is the
**dataset type name** — it corresponds directly to the product names described in
the sections below.

---

## pfsConfig

Filename format: `pfsConfig_PFS_{visit}_{collection}.fits`

Example (PFS Filler Program, visit 122041):
```
/shared/pfs/programs/S25A-000QF/2d/S25A_April2026/pfsConfig/20250323/122041/
    pfsConfig_PFS_122041_S25A_April2026.fits
```

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

The fluxes above are collected from catalogs such as HSC, PS1, GAIA.

---

## pfsArm

`pfsArm` contains the **wavelength-calibrated, sky-subtracted**, but **not flux-calibrated** extracted spectra
for all fibers in a single spectrograph arm from a single exposure.
Each active arm (`b`=Blue, `r`=Red, `n`=IR, `m`=Medium-resolution red) and each spectrograph module (1–4)
produces a separate file. The wavelength grid is not required to be uniform — a wavelength array is stored per pixel.

Filename format: `pfsArm_PFS_{visit}_{arm}{spectrograph}_{collection}.fits`

One file is produced per arm and spectrograph module. Example (PFS Filler Program, visit 122041, blue `b`, medium `m`, and IR `n` arms across 4 spectrograph modules):
```
/shared/pfs/programs/S25A-000QF/2d/S25A_April2026/pfsArm/20250323/122041/
    pfsArm_PFS_122041_b1_S25A_April2026.fits
    pfsArm_PFS_122041_b2_S25A_April2026.fits
    pfsArm_PFS_122041_b3_S25A_April2026.fits
    pfsArm_PFS_122041_b4_S25A_April2026.fits
    pfsArm_PFS_122041_m1_S25A_April2026.fits
    ...
    pfsArm_PFS_122041_n4_S25A_April2026.fits
```

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

---

## pfsMerged

`pfsMerged` combines the spectra from all arms for a single visit into one file.
It is **wavelength-calibrated and sky-subtracted**, but **not flux-calibrated**.
The format is identical to `pfsArm`, with two differences:

- Flux units are **electrons per nm** (rather than electrons)
- The `WAVELENGTH` array may be a single shared array applied to all fibers
  (rather than one per fiber), if all fibers share the same wavelength sampling

Filename format: `pfsMerged_PFS_{visit}_{collection}.fits`

Example (PFS Filler Program, visit 122041):
```
/shared/pfs/programs/S25A-000QF/2d/S25A_April2026/pfsMerged/20250323/122041/
    pfsMerged_PFS_122041_S25A_April2026.fits
```

---

## pfsCalibrated

`pfsCalibrated` is the **actual file on disk** containing wavelength-calibrated, sky-subtracted,
flux-calibrated, arm-merged spectra for all science objects in a single visit.
The individual spectrum of a single object (i.e. one row/entry inside `pfsCalibrated`) is referred to as a **`pfsSingle`** spectrum.

Filename format: `pfsCalibrated_PFS_{visit}_{collection}.fits`

Example (PFS Filler Program, visit 122041):
```
/shared/pfs/programs/S25A-000QF/2d/S25A_April2026/pfsCalibrated/20250323/122041/
    pfsCalibrated_PFS_122041_S25A_April2026.fits
```

---

## pfsCoadd

`pfsCoadd` is the **actual file on disk** containing wavelength-calibrated, sky-subtracted,
flux-calibrated, coadded spectra combining data across multiple visits.
Files are split by `catId` and `objGroup`, so there are multiple `pfsCoadd` files per catalog.
The individual coadded spectrum of a single object (i.e. one row/entry inside `pfsCoadd`) is referred to as a **`pfsObject`** spectrum.

Filename format: `pfsCoadd_PFS_selected_{proposal}_{catId}_{objGroup}_{collection}.fits`

Example (PFS Filler Program, catId 10094, 32 object groups):
```
/shared/pfs/programs/S25A-000QF/2d/S25A_April2026/pfsCoadd/10094/
    pfsCoadd_PFS_selected_S25A_10094_1_S25A_April2026.fits
    pfsCoadd_PFS_selected_S25A_10094_2_S25A_April2026.fits
    ...
    pfsCoadd_PFS_selected_S25A_10094_32_S25A_April2026.fits
```
