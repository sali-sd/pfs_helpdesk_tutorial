# pfsCoZCandidates

## Overview

`pfsCoZCandidates` is the LAM 1D output file. It bundles redshift candidates, classification results, line measurements, and quality flags for all objects in a single catalog (`catId`) into one file, following the same `pfsCoadd` structure.

The LAM 1D pipeline is run on each `pfsCoadd` basis — one `pfsCoZCandidates` file is produced per `catId`/`objGroup` combination (see the [pfsCoadd](03_16_pfscoadd.md) section). The results are stored in a directory tree where each folder is named `{catId}_{objGroup}`, and the FITS file lives inside a `data/` subdirectory.

Example from proposal `S25A-000QF`, catId 10094 (32 object groups):
```
/shared/pfs/programs/S25A-000QF/lam1d/S25A_April2026/modified/
    10094_1/data/pfsCoZcandidates-10094.fits
    10094_2/data/pfsCoZcandidates-10094.fits
    ...
    10094_32/data/pfsCoZcandidates-10094.fits
```

- Flux units for line measurements are **nJy** (continuum) and **10⁻³⁵ W/m²** (line flux)
- Each object can have multiple redshift candidates ranked by probability (`cRank=0` is the best)

Filename format: `pfsCoZCandidates_PFS_{combination}_{catId}_{collection}.fits`


**FITS structure:**

| HDU | Name | Type | Description |
|-----|------|------|-------------|
| #0 | PDU | Header | Version keywords (D1D_VER, D1DP_VER, etc.) |
| #1 | TARGET | Binary table | Object identifiers (targetId, catId, objId, ra, dec, targetType) |
| #2 | WARNINGS | Binary table | Per-solver warning bitmasks |
| #3 | ERRORS | Binary table | Per-solver error codes and messages |
| #4 | CLASSIFICATION | Binary table | Best classification (GALAXY/QSO/STAR) with probabilities |
| #5 | GALAXY_CANDIDATES | Binary table | Galaxy redshift candidates (ranked) |
| #6 | GALAXY_MODELS | Image/table | Best-fit galaxy model spectra (nJy) |
| #7 | GALAXY_REDSHIFT_GRID | Binary table | Redshift grid used for galaxy PDF |
| #8 | GALAXY_LN_PDF | Image | ln(probability) marginalised over galaxy templates |
| #9 | GALAXY_LINES | Binary table | Galaxy emission/absorption line measurements |
| #10 | QSO_CANDIDATES | Binary table | QSO redshift candidates (ranked) |
| #11 | QSO_MODELS | Image/table | Best-fit QSO model spectra (nJy) |
| #12 | QSO_REDSHIFT_GRID | Binary table | Redshift grid used for QSO PDF |
| #13 | QSO_LN_PDF | Image | ln(probability) marginalised over QSO templates |
| #14 | QSO_LINES | Binary table | QSO emission/absorption line measurements |
| #15 | STAR_CANDIDATES | Binary table | Stellar radial velocity candidates (ranked) |
| #16 | STAR_MODELS | Image/table | Best-fit stellar model spectra (nJy) |
| #17 | STAR_VELOCITY_GRID | Binary table | Velocity grid used for stellar PDF |
| #18 | STAR_LN_PDF | Image | ln(probability) marginalised over stellar templates |
| #19 | QUALITY | Binary table | Quality metrics (OII doublet SNR, valid pixel count, etc.) |

## Key Columns

**CLASSIFICATION (HDU #4):**

| Column | Type | Description |
|--------|------|-------------|
| `targetId` | 16-bit INT | Links to TARGET HDU |
| `class` | STRING | Best classification: `GALAXY`, `QSO`, or `STAR` |
| `probaGalaxy` | FLOAT | Probability of being a galaxy |
| `probaQSO` | FLOAT | Probability of being a QSO |
| `probaStar` | FLOAT | Probability of being a star |

**GALAXY_CANDIDATES (HDU #5) — key columns:**

| Column | Type | Description |
|--------|------|-------------|
| `cRank` | 32-bit INT | Candidate rank; 0 = best |
| `redshift` | 32-bit FLOAT | Best-fit redshift |
| `redshiftError` | 32-bit FLOAT | Redshift uncertainty |
| `redshiftProba` | 32-bit FLOAT | PDF peak area (dz = ±3×10⁻³) |
| `subClass` | STRING | Sub-classification |
| `continuumFile` | STRING | Continuum template used |

The same ranked-candidate structure applies to `QSO_CANDIDATES` (HDU #10) and `STAR_CANDIDATES` (HDU #15), with `velocity` replacing `redshift` for stars.

## Building a LAM 1D Object Table

The following code builds a combined object table across all LAM 1D results in a collection. It works in three steps:

1. **Magnitude lookup** — iterates over all visits in the collection via `pfsMerged`, extracting per-object magnitudes from `pfsConfig` across all available filters
2. **LAM 1D FITS reading** — reads all `pfsCoZCandidates` FITS files from a local LAM 1D output directory, extracting classification, redshift/velocity candidates (best ranked per object), warnings, and errors for each object
3. **Combining and saving** — merges the magnitude lookup with the LAM 1D results into a single CSV file (`{collections}_all_lam1d.csv`), which can be used to browse objects by class, redshift, velocity, or objId

After saving the CSV, the code plots **magnitude vs. redshift** (for GALAXY and QSO) and **magnitude vs. velocity** (for STAR), coloured by `catId`.

```python
import os
import re
import glob
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from astropy.io import fits
from lsst.daf.butler import Butler
from pfs.datamodel import TargetType

# ==== INPUT PARAMETERS ====
repo        = "/shared/pfs/programs/S25A-000QF/2d/"
collections = "S25A_April2026"
lam1d_dir   = "/shared/pfs/programs/S25A-000QF/lam1d/S25A_April2026/modified" # Ensure this directory matches the COLLECTIONS

# ==== HELPER: endian-safe FITS HDU to DataFrame ====
def fits_to_df(hdu_data):
    def fix_endian(arr):
        if arr.dtype.byteorder == '>':
            return arr.byteswap().view(arr.dtype.newbyteorder('<'))
        return arr
    return pd.DataFrame({name: fix_endian(hdu_data[name]) for name in hdu_data.names})

# ==== STEP 1: BUILD MAGNITUDE LOOKUP ====
butler     = Butler(repo, collections=collections)
all_visits = sorted({ref.dataId['visit'] for ref in butler.registry.queryDatasets('pfsMerged')})
print(f"Building magnitude lookup from {len(all_visits)} visits...")

mag_lookup = {}
for i, visit in enumerate(all_visits):
    print(f"  Visit {i+1}/{len(all_visits)}: {visit}  ({len(mag_lookup)} unique objects so far)", end='\r')
    pfsConfig = butler.get('pfsConfig', dict(visit=visit))
    sci       = pfsConfig.select(targetType=TargetType.SCIENCE, fiberStatus=1)
    if len(sci.objId) == 0:
        continue
    total_flux = np.array([list(f) for f in sci.totalFlux], dtype=float)
    psf_flux   = np.array([list(f) for f in sci.psfFlux],   dtype=float)
    flux       = np.where((total_flux > 0) & np.isfinite(total_flux), total_flux, psf_flux)
    with np.errstate(divide='ignore', invalid='ignore'):
        mags = np.where(flux > 0, -2.5 * np.log10(flux) + 31.4, np.nan)
    for j, oid in enumerate(sci.objId):
        oid_int = int(oid)
        if oid_int not in mag_lookup:
            obj_filters = list(sci.filterNames[j])
            seen, obj_cols = {}, []
            for fn in obj_filters:
                count = seen.get(fn, 0)
                obj_cols.append(f'mag_{fn}_{count}' if count > 0 or obj_filters.count(fn) > 1 else f'mag_{fn}')
                seen[fn] = count + 1
            mag_lookup[oid_int] = {col: mags[j, k] for k, col in enumerate(obj_cols)}

mag_df       = pd.DataFrame([{'objId': oid, **m} for oid, m in mag_lookup.items()])
mag_cols_all = [col for col in mag_df.columns if col.startswith('mag_')]
empty_cols   = [col for col in mag_cols_all if mag_df[col].isna().all()]
mag_df       = mag_df.drop(columns=empty_cols)
mag_cols     = [col for col in mag_cols_all if col not in empty_cols]
print(f"\nMagnitude lookup complete: {len(mag_df)} unique objects  |  Filters: {mag_cols}")

# ==== STEP 2: READ LAM1D FITS ====
all_dirs = sorted(glob.glob(os.path.join(lam1d_dir, "*_*")))
print(f"\nReading LAM1D FITS from {len(all_dirs)} directories...")

all_final_dfs = []
n_skipped     = 0

for base_dir in all_dirs:
    dirname = os.path.basename(base_dir.rstrip('/'))
    match   = re.match(r'^(\d+)_(\d+)$', dirname)
    if not match:
        continue
    catid, obj_group = match.group(1), match.group(2)

    fits_files = sorted(glob.glob(os.path.join(base_dir, '**', '*.fits'), recursive=True))
    if not fits_files:
        n_skipped += 1
        continue

    try:
        with fits.open(fits_files[0]) as hdul:
            target_df         = fits_to_df(hdul['TARGET'].data)
            classification_df = fits_to_df(hdul['CLASSIFICATION'].data)
            warnings_df       = fits_to_df(hdul['WARNINGS'].data)
            errors_df         = fits_to_df(hdul['ERRORS'].data)
            galaxy_df         = fits_to_df(hdul['GALAXY_CANDIDATES'].data)
            qso_df            = fits_to_df(hdul['QSO_CANDIDATES'].data)
            star_df           = fits_to_df(hdul['STAR_CANDIDATES'].data)
    except Exception as e:
        print(f"  Failed {dirname}: {e}")
        n_skipped += 1
        continue

    galaxy_df = galaxy_df.rename(columns={col: f"{col}_gal" for col in galaxy_df.columns if col != 'targetId'})
    qso_df    = qso_df.rename(columns={col: f"{col}_qso"    for col in qso_df.columns    if col != 'targetId'})
    star_df   = star_df.rename(columns={col: f"{col}_star"  for col in star_df.columns   if col != 'targetId'})

    best_galaxy_df = galaxy_df.sort_values('redshiftProba_gal', ascending=False).drop_duplicates('targetId')
    best_qso_df    = qso_df.sort_values('redshiftProba_qso',    ascending=False).drop_duplicates('targetId')
    best_star_df   = star_df.sort_values('templateProba_star',  ascending=False).drop_duplicates('targetId')

    final_df = pd.merge(target_df,     classification_df, on='targetId', how='inner')
    final_df = pd.merge(final_df,      warnings_df,       on='targetId', how='inner')
    final_df = pd.merge(final_df,      errors_df,         on='targetId', how='inner')
    final_df = pd.merge(final_df,      best_galaxy_df,    on='targetId', how='inner')
    final_df = pd.merge(final_df,      best_qso_df,       on='targetId', how='inner')
    final_df = pd.merge(final_df,      best_star_df,      on='targetId', how='inner')

    final_df['catid']     = catid
    final_df['obj_group'] = obj_group
    all_final_dfs.append(final_df)

if not all_final_dfs:
    raise ValueError("No data found — check lam1d_dir path and directory structure.")

print(f"Processed {len(all_final_dfs)} directories  ({n_skipped} skipped)")

# ==== STEP 3: COMBINE AND ATTACH MAGNITUDES ====
combined_df = pd.concat(all_final_dfs, ignore_index=True)
combined_df = combined_df.merge(mag_df[['objId'] + mag_cols], on='objId', how='left')
matched     = combined_df[mag_cols].notna().any(axis=1).sum()
print(f"Magnitudes matched: {matched} / {len(combined_df)} objects")

# ==== STEP 4: SAVE ====
combined_df.to_csv(f'{collections}_all_lam1d.csv', index=False)
print(f"Saved {collections}_all_lam1d.csv  ({len(combined_df)} objects)")

# ==== CLASS BREAKDOWN ====
print("\nClass breakdown:")
for cls in sorted(combined_df['class'].str.upper().unique()):
    n = (combined_df['class'].str.upper() == cls).sum()
    print(f"  {cls}: {n} objects")

# ==== PLOTS: MAG VS REDSHIFT / VELOCITY PER CLASS ====
plot_config = [
    ("GALAXY", "redshift_gal",  "LAM1D Redshift",        1),
    ("QSO",    "redshift_qso",  "LAM1D Redshift",        1),
    ("STAR",   "velocity_star", "LAM1D Velocity [km/s]", 1e-3),
]

unique_catids = sorted(combined_df['catid'].unique())
colors        = plt.cm.Set1(np.linspace(0, 1, max(len(unique_catids), 3)))
catid_colors  = dict(zip(unique_catids, colors))

for class_name, y_col, y_label, y_scale in plot_config:
    df_cls = combined_df[combined_df['class'].str.upper() == class_name].copy()
    if df_cls.empty:
        print(f"No {class_name} objects, skipping plot.")
        continue

    best_mag_col = df_cls[mag_cols].notna().sum().idxmax()
    filter_label = best_mag_col.replace('mag_', '')

    # ==== EXCLUDE OUTLIERS FOR PLOT ONLY ====
    mag_vals = df_cls[best_mag_col]
    y_vals   = df_cls[y_col] * y_scale
    mag_lo, mag_hi = np.nanpercentile(mag_vals.dropna(), [1, 99])
    y_lo,   y_hi   = np.nanpercentile(y_vals.dropna(),   [1, 99])
    plot_mask = (
        mag_vals.between(mag_lo, mag_hi) &
        y_vals.between(y_lo, y_hi)
    )
    df_plot = df_cls[plot_mask]

    plt.figure(figsize=(8, 6))
    for cid in unique_catids:
        df_cid = df_plot[df_plot['catid'] == cid]
        if df_cid.empty:
            continue
        plt.scatter(df_cid[best_mag_col], df_cid[y_col] * y_scale, s=2, alpha=0.5,
                    color=catid_colors[cid], label=f'catid={cid}')

    plt.xlabel(f'Magnitude ({filter_label}) [AB]')
    plt.ylabel(y_label)
    plt.title(f'Collections={collections}  |  {class_name}: Magnitude vs {y_label}\nRepo={repo}')
    plt.legend(loc='best', markerscale=5)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(f'{collections}_{class_name}_mag_vs_{y_col}.png', dpi=150, bbox_inches='tight')
    plt.show()
```

**Output**:
```
Building magnitude lookup from 632 visits...
  Visit 632/632: 128470  (44085 unique objects so far)
Magnitude lookup complete: 44085 unique objects  |  Filters: ['mag_g_gaia', 'mag_bp_gaia', 'mag_rp_gaia', 'mag_g_ps1', 'mag_r_ps1', 'mag_i_ps1', 'mag_z_ps1', 'mag_y_ps1']

Reading LAM1D FITS from 32 directories...
Processed 32 directories  (0 skipped)
Magnitudes matched: 31107 / 31107 objects
Saved S25A_April2026_all_lam1d.csv  (31107 objects)

Class breakdown:
  GALAXY: 16147 objects
  QSO: 214 objects
  STAR: 14746 objects
```

![GALAXY magnitude vs redshift](figures/S25A_April2026_GALAXY_mag_vs_redshift_gal.png)

![QSO magnitude vs redshift](figures/S25A_April2026_QSO_mag_vs_redshift_qso.png)

![STAR magnitude vs velocity](figures/S25A_April2026_STAR_mag_vs_velocity_star.png)
