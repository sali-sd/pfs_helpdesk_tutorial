# pfsCoadd

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
