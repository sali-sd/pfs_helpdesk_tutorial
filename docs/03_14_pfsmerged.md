# pfsMerged

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
