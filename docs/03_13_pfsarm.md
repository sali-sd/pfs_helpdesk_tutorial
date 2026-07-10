# pfsArm

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
