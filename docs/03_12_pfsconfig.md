# pfsConfig

## Overview

`pfsConfig` records the *realized* fiber configuration for a specific **visit** (exposure).
It is the observed counterpart to `pfsDesign`, capturing where each fiber
actually ended up on the focal plane (as opposed to where it was intended to be). The pfsConfig files are the primary destination of all object related information, e.g. RA/Dec, catalog ID, target type, fiber status, object fluxes (from public catalogs).

Filename format: `pfsConfig_PFS_{visit}_{collection}.fits`

Example from proposal `S25A-000QF`, visit 122041 on the Science Platform:
```
/shared/pfs/programs/S25A-000QF/2d/S25A_April2026/pfsConfig/20250323/122041/
    pfsConfig_PFS_122041_S25A_April2026.fits
```

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

The fluxes above are collected from public catalogs such as HSC SSP, PS1, GAIA.

## Visit Analysis

Here we show how to set up the butler, list all available visits in a collection, and load `pfsConfig` for a specific visit:

```python
from lsst.daf.butler import Butler

repo        = "/shared/pfs/programs/S25A-000QF/2d/"  # path to the 2d DRP repository
collections = "S25A_April2026"                       # collection name
butler      = Butler(repo, collections=collections)

# Find all visits in the collection
all_visits = sorted({ref.dataId['visit'] for ref in butler.registry.queryDatasets('pfsMerged')})
print(f"Total visits: {len(all_visits)}")
print(f"Visits: {all_visits}")

# Load pfsConfig for a specific visit
visit     = 123476
pfsConfig = butler.get('pfsConfig', dict(visit=visit))
```

## Fiber Distribution

The following code shows the distribution of all fibers (SCIENCE, SKY, FLUX STANDARDS) on the focal plane for a given visit. Simply specify under **USER-DEFINED PARAMETERS** the 2d DRP data repository location and collection name, along with the visit number (or increment through visits in the collection using a simple index):

```python
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from lsst.daf.butler import Butler
from pfs.datamodel import TargetType

# ==== USER-DEFINED PARAMETERS ====
repo        = "/shared/pfs/programs/S25A-000QF/2d/"  # path to the 2d DRP repository
collections = "S25A_April2026"                       # collection name
VISIT            = 123476 # Inspects and plots fiber positions in specified visit
VISIT_INDEX      = 0      # Used if VISIT is None. Increment through visits in collections (0 = first, 1 = second, etc.)
PRINT_ALL_VISITS = False  # Set to True to print all visit numbers in collections

# ==== FIND ALL VISITS ====
butler     = Butler(repo, collections=collections)
all_visits = sorted({ref.dataId['visit'] for ref in butler.registry.queryDatasets('pfsMerged')})
print(f"Total visits in Collections ({collections}): {len(all_visits)}")
if PRINT_ALL_VISITS:
    print(f"All visits: {all_visits}")

if VISIT is not None:
    if VISIT not in all_visits:
        raise ValueError(f"Visit {VISIT} not found in collections '{collections}'")
    visit = VISIT
    print(f"Using specified visit={visit}")
else:
    visit = all_visits[VISIT_INDEX]
    print(f"Selected visit index {VISIT_INDEX}: visit={visit}")

# ==== LOAD PFSCONFIG ====
pfsConfig = butler.get('pfsConfig', dict(visit=visit))
sci       = pfsConfig.select(targetType=TargetType.SCIENCE,  fiberStatus=1)
sky       = pfsConfig.select(targetType=TargetType.SKY,      fiberStatus=1)
fluxstd   = pfsConfig.select(targetType=TargetType.FLUXSTD,  fiberStatus=1)

# ==== FLUX + MAGNITUDES (SCIENCE ONLY) ====
filter_names = list(sci.filterNames[0])
first_filter = filter_names[0]
print(f"\nFilter used for sorting: {first_filter}")

total_flux = np.array([list(f) for f in sci.totalFlux], dtype=float)
psf_flux   = np.array([list(f) for f in sci.psfFlux],   dtype=float)
flux       = np.where((total_flux > 0) & np.isfinite(total_flux), total_flux, psf_flux)
with np.errstate(divide='ignore', invalid='ignore'):
    mag = np.where(flux > 0, -2.5 * np.log10(flux) + 31.4, np.nan)

df = pd.DataFrame({
    'objId':                  np.array(sci.objId).astype('<i8'),
    'catId':                  np.array(sci.catId).astype('<i4'),
    'spectrograph':           np.array(sci.spectrograph).astype('<i4'),
    f'mag_{first_filter}_AB': mag[:, 0],
})

df_sorted_bright = df.sort_values(f'mag_{first_filter}_AB', ascending=True,  na_position='last').head(5)
df_sorted_faint  = df.sort_values(f'mag_{first_filter}_AB', ascending=False, na_position='last').head(5)

print(f"\nTop 5 brightest objects ({first_filter}):")
print(df_sorted_bright.to_string(index=False))
print(f"\nTop 5 faintest objects ({first_filter}):")
print(df_sorted_faint.to_string(index=False))

# ==== FIBER POSITION PLOT ====
fig, ax = plt.subplots(figsize=(7, 7))
fig.subplots_adjust(top=0.90, bottom=0.10, left=0.12, right=0.97)

ax.scatter(sci.ra,     sci.dec,     s=6,  marker='o', color='black',    label=f'SCIENCE ({len(sci.ra)})',      zorder=3)
ax.scatter(sky.ra,     sky.dec,     s=12, marker='^', color='limegreen', label=f'SKY ({len(sky.ra)})',          zorder=2)
ax.scatter(fluxstd.ra, fluxstd.dec, s=12, marker='s', color='orangered', label=f'FLUXSTD ({len(fluxstd.ra)})', zorder=2)

ax.set_xlabel('RA [deg]')
ax.set_ylabel('Dec [deg]')
ax.set_title(f'Fiber Positions  Visit={visit}\nCollections ({collections})')
ax.legend(loc='upper right', fancybox=True, framealpha=0.5)
ax.invert_xaxis()
ax.minorticks_on()
plt.show()
```

**Output**:

```
Total visits in Collections (S25A_April2026): 632
Using specified visit=123476

Filter used for sorting: g_ps1

Top 5 brightest objects (g_ps1):
             objId  catId  spectrograph  mag_g_ps1_AB
121031447176721742  10094             2     17.981820
120551448544214427  10094             4     18.751546
121691448092058861  10094             1     18.781657
120951452624792300  10094             4     18.903479
120581452346316466  10094             2     18.907853

Top 5 faintest objects (g_ps1):
             objId  catId  spectrograph  mag_g_ps1_AB
120671447895508750  10094             3     26.434644
121261444908351362  10094             1     25.316608
121141456199749830  10094             3     24.789236
121471455299111416  10094             3     24.756075
121521454101227474  10094             1     24.626719
```

![Fiber positions for visit 123476](figures/pfsConfig_visit=123476.png)

## Search Visits by Object ID

If you have the `objId` of a specific object you have observed and would like to know details of that object, the following code prints a summary of all visits that contain that object, including its catalog ID and magnitude.

```python
import numpy as np
from astropy.io import fits
from lsst.daf.butler import Butler
from pfs.datamodel import TargetType

# ==== USER-DEFINED PARAMETERS ====
repo        = "/shared/pfs/programs/S25A-000QF/2d/"  # path to the 2d DRP repository
collections = "S25A_April2026"                       # collection name
objid       = 120731449862702300

# ==== FIND ALL VISITS VIA PFSMERGED, THEN GET PFSCONFIG REFS ====
butler     = Butler(repo, collections=collections)
all_visits = sorted({ref.dataId['visit'] for ref in butler.registry.queryDatasets('pfsMerged')})
all_refs   = list(butler.registry.queryDatasets('pfsConfig',
                  where=f"visit IN ({','.join(str(v) for v in all_visits)})"))
print(f"Total visits in Collections ({collections}): {len(all_visits)}")

# ==== FAST SCAN VIA DIRECT FITS READ ====
objid_visits = []
info_ref     = None

for ref in all_refs:
    uri = butler.getURI(ref)
    with fits.open(uri.path) as hdul:
        objids = hdul[1].data['objId']
        if objid in objids:
            objid_visits.append(ref.dataId['visit'])
            if info_ref is None:
                info_ref = ref

if not objid_visits:
    raise ValueError(f"objId {objid} not found in any pfsConfig in collections '{collections}'")

objid_visits = sorted(set(objid_visits))
print(f"\nObjId={objid} found in {len(objid_visits)} visit(s): {objid_visits}")

# ==== GET FULL INFO FROM FIRST VISIT ====
pfsConfig    = butler.get('pfsConfig', dict(visit=objid_visits[0]))
sci          = pfsConfig.select(targetType=TargetType.SCIENCE, fiberStatus=1)
sci_mask     = sci.objId == objid
idx          = np.where(sci_mask)[0][0]
filter_names = list(sci.filterNames[0])
first_filter = filter_names[0]
total_flux   = np.array([list(f) for f in sci.totalFlux], dtype=float)
psf_flux     = np.array([list(f) for f in sci.psfFlux],   dtype=float)
flux         = np.where((total_flux > 0) & np.isfinite(total_flux), total_flux, psf_flux)
with np.errstate(divide='ignore', invalid='ignore'):
    mag = np.where(flux > 0, -2.5 * np.log10(flux) + 31.4, np.nan)

print(f"\nObject info (from visit {objid_visits[0]}):")
print(f"  ObjId        = {int(sci.objId[idx])}")
print(f"  CatId        = {int(sci.catId[idx])}")
print(f"  Spectrograph = {int(sci.spectrograph[idx])}")
print(f"  Mag ({first_filter}) = {mag[idx, 0]:.3f} AB")
```

**Output**:

```
Total visits in Collections (S25A_April2026): 632

ObjId=120731449862702300 found in 4 visit(s): [123476, 123477, 123478, 123479]

Object info (from visit 123476):
  ObjId        = 120731449862702300
  CatId        = 10094
  Spectrograph = 3
  Mag (g_ps1) = 21.635 AB
```
