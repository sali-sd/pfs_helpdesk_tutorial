# pfsConfig

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
