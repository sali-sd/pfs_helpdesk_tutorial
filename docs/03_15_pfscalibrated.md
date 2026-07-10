# pfsCalibrated

`pfsCalibrated` is the **actual file on disk** containing wavelength-calibrated, sky-subtracted,
flux-calibrated, arm-merged spectra for all science objects in a single visit.
The individual spectrum of a single object (i.e. one row/entry inside `pfsCalibrated`) is referred to as a **`pfsSingle`** spectrum.

Filename format: `pfsCalibrated_PFS_{visit}_{collection}.fits`

Example (PFS Filler Program, visit 122041):
```
/shared/pfs/programs/S25A-000QF/2d/S25A_April2026/pfsCalibrated/20250323/122041/
    pfsCalibrated_PFS_122041_S25A_April2026.fits
```
