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

The fluxes above are collected from catalogs such as HSC, PS1, GAIA.

---

## pfsArm

`pfsArm` contains the **wavelength-calibrated, sky-subtracted**, but **not flux-calibrated** extracted spectra
for all fibers in a single spectrograph arm from a single exposure.
Each active arm (`b`=Blue, `r`=Red, `n`=IR, `m`=Medium-resolution red) and each spectrograph module (1–4)
produces a separate file. The wavelength grid is not required to be uniform — a wavelength array is stored per pixel.

Files are named following the Gen3 butler datastore convention, e.g.:

```
pfsArm_PFS_{visit}_{arm}{spectrograph}_PFS_science_{proposal}_{collection}_{group}_{timestamp}.fits
```

Example from a real reduction (visit 121998, proposal S25A, blue and red arms across 4 spectrographs):
```
pfsArm_PFS_121998_b1_PFS_science_S25A_reduceExposure_20260206_brm_group1_20260210T014710Z.fits
pfsArm_PFS_121998_b2_PFS_science_S25A_reduceExposure_20260206_brm_group1_20260210T014710Z.fits
pfsArm_PFS_121998_b3_PFS_science_S25A_reduceExposure_20260206_brm_group1_20260210T014710Z.fits
pfsArm_PFS_121998_b4_PFS_science_S25A_reduceExposure_20260206_brm_group1_20260210T014710Z.fits
pfsArm_PFS_121998_r1_PFS_science_S25A_reduceExposure_20260206_brm_group1_20260210T014710Z.fits
...
```

Here `brm` in the collection name indicates the blue, red and medium-resolution arms were processed;
`reduceExposure.20260206` is the processing collection using calibrations from 2026-02-06.

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

Files follow the Gen3 naming convention, e.g.:

```
pfsMerged_PFS_{visit}_PFS_science_{proposal}_{collection}_{merge_group}_{timestamp}.fits
```

Example from a real reduction (visit 121998, proposal S25A):
```
pfsMerged_PFS_121998_PFS_science_S25A_reduceExposure_20260206_merge_group1_20260211T071650Z.fits
```

---

## pfsCalibrated

`pfsCalibrated` is a collection of wavelength-calibrated, sky-subtracted,
flux-calibrated, arm-merged spectra from a single visit, stored as a single
FITS file. It following is the general naming convention, e.g.:

```
pfsCalibrated_PFS_{visit}_PFS_science_{proposal}_{collection}_{group}_{timestamp}.fits
```

Example from a real reduction - visit 121998 from S25A semester:
```
pfsCalibrated_PFS_121998_PFS_science_S25A_calibrated_20260206_group1_20260212T054929Z.fits
```

The individual spectrum of a single object (i.e. one row/entry inside `pfsCalibrated`) within this file is referred to as a **`pfsSingle`** spectrum.

---

## pfsCoadd

`pfsCoadd` is a collection of wavelength-calibrated, sky-subtracted,
flux-calibrated, coadded spectra for a group of objects within a single catalog (`catId`),
co-adding spectra across multiple visits. Due to limitations on file size, `pfsCoadd` files are split by `catId` and `objGroup`, so there
can be multiple `pfsCoadd` files per `catId`. 

The individual coadded spectrum of a single object (i.e. one row/entry inside `pfsCoadd`) within this file is referred to as a **`pfsObject`** spectrum.

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
