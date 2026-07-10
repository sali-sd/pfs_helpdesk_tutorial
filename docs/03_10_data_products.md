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

`pfsArm` contains the **wavelength-calibrated, sky-subtracted**, but **not flux-calibrated** extracted spectra
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
It is **wavelength-calibrated and sky-subtracted**, but **not flux-calibrated**.
The format is identical to `pfsArm`, with two differences:

- Flux units are **electrons per nm** (rather than electrons)
- The `WAVELENGTH` array may be a single shared array applied to all fibers
  (rather than one per fiber), if all fibers share the same wavelength sampling

---

## pfsCalibrated

`pfsCalibrated` is a collection of wavelength-calibrated, sky-subtracted,
flux-calibrated, arm-merged spectra from a single visit, stored as a single
FITS file. It is produced by the Gen3 butler pipeline and named following the Gen3 datastore convention, e.g.:

```
pfsCalibrated_PFS_{visit}_PFS_science_{proposal}_{collection}_{group}_{timestamp}.fits
```

Example from a real reduction (visit 121998 from S25A semester:
```
pfsCalibrated_PFS_121998_PFS_science_S25A_calibrated_20260206_group1_20260212T054929Z.fits
```

The individual spectrum of a single object (i.e. one row/entry inside `pfsCalibrated`) within this file is referred to as a **`pfsSingle`** spectrum.

---

## pfsCoadd

`pfsCoadd` is the **actual file on disk** containing wavelength-calibrated, sky-subtracted,
flux-calibrated, coadded spectra for a group of objects within a single catalog (`catId`),
combining data across multiple visits. Files are split by `catId` and `objGroup`, so there
are multiple `pfsCoadd` files per catalog — one per object group. The individual coadded
spectrum of a single object within this file is referred to as a **`pfsObject`** spectrum.
`pfsObject` is not a standalone file — it is a logical unit (one row/entry) inside `pfsCoadd`.

Files are named following the Gen3 butler datastore convention, e.g.:

```
pfsCoadd_PFS_selected_{proposal}_{catId}_{objGroup}_{instrument}_{type}_{proposal}_{collection}_{group}_{timestamp}.fits
```

Example from a real reduction (catId 10091, proposal S25A, 70 object groups):
```
pfsCoadd_PFS_selected_S25A_10091_1_PFS_science_S25A_coadd_20260206_group1_20260213T045043Z.fits
pfsCoadd_PFS_selected_S25A_10091_2_PFS_science_S25A_coadd_20260206_group1_20260213T045043Z.fits
...
pfsCoadd_PFS_selected_S25A_10091_70_PFS_science_S25A_coadd_20260206_group1_20260213T045043Z.fits
```

Here the incrementing number (1–70) is the `objGroup` index, and `coadd.20260206` is the
processing collection using calibrations from 2026-02-06.

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
