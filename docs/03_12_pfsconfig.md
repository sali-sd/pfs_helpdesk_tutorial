# pfsConfig

## Overview

`pfsConfig` records the *realized* fiber configuration for a specific **visit** (exposure).
It is the observed counterpart to `pfsDesign`, capturing where each fiber
actually ended up on the focal plane (as opposed to where it was intended to be). The pfsConfig files are the primary destination of all object related information, e.g. RA/Dec, catalog ID, target type, fiber status, object fluxes (from public catalogs).

Filename format: `pfsConfig_PFS_{visit}_{collection}.fits`

Example from proposal `S25A-000QF`, visit 137292 on the Science Platform:

```
/shared/pfs/programs/S25A-000QF/2d/run26_June2026/pfsConfig/20260111/137292/
    pfsConfig_PFS_137292_run26_June2026.fits
```

**FITS structure:**


| HDU | Name       | Type         | Description                                     |
| --- | ---------- | ------------ | ----------------------------------------------- |
| #0  | PDU        | Header       | Actual telescope boresight RA/Dec (degrees)     |
| #1  | CONFIG     | Binary table | Per-fiber target and position data              |
| #2  | PHOTOMETRY | Binary table | Per-fiber flux measurements in multiple filters |


**CONFIG table columns (key fields):**


| Column        | Type           | Description                                            |
| ------------- | -------------- | ------------------------------------------------------ |
| `fiberId`     | 32-bit int     | Fiber identifier (starts at 1)                         |
| `catId`       | 32-bit int     | Source catalog identifier                              |
| `objId`       | 64-bit int     | Unique object identifier                               |
| `ra`, `dec`   | 64-bit float   | Target position (degrees)                              |
| `targetType`  | 32-bit int     | Target class (e.g. SCIENCE, SKY, FLUXSTD,...)          |
| `fiberStatus` | 32-bit int     | Fiber health (e.g. GOOD, BROKENFIBER, BLOCKED,...)     |
| `pfiNominal`  | 2×32-bit float | Intended fiber position on the focal plane (mm)        |
| `pfiCenter`   | 2×32-bit float | Actual measured fiber position on the focal plane (mm) |
| `proposalId`  | string         | Subaru proposal ID (e.g. `S24B-001QN`)                 |
| `obCode`      | string         | Observing Block code within a proposal                 |


**PHOTOMETRY table columns (key fields):**


| Column       | Units | Description                                                     |
| ------------ | ----- | --------------------------------------------------------------- |
| `fiberFlux`  | nJy   | Flux within ~1 arcsec fiber aperture (seeing-corrected)         |
| `psfFlux`    | nJy   | Flux from PSF fitting to infinite radius                        |
| `totalFlux`  | nJy   | Total flux (PSF for point sources; extended model for galaxies) |
| `filterName` | —     | Filter name specifying the transmission curve                   |


The fluxes above are collected from public catalogs such as HSC SSP, PS1, GAIA.

## Checking all Visits in Collection

Here we show how to set up `Butler` and list all available visits in a `collection`. Simply specify under **USER-DEFINED PARAMETERS** the 2d DRP data repository location and `collection` name:

```python
from lsst.daf.butler import Butler

# ==== USER-DEFINED PARAMETERS ====
repo        = "/shared/pfs/programs/S25A-000QF/2d/"  # path to the 2d DRP repository
collections = "run26_June2026"                       # collection name

# ==== QUERY ALL VISITS FROM BUTLER AND PRINT ALL VISITS ====
butler      = Butler(repo, collections=collections)
all_visits = sorted({ref.dataId['visit'] for ref in butler.registry.queryDatasets('pfsMerged')})
print(f"Total visits: {len(all_visits)}")
print(f"Visits: {all_visits}")
```

**Output**:

```
Total visits: 426
Visits: [137067, 137068, 137070, 137071, 137073, 137074, 137076, 137077, 137277, 137278, 137280, 137281, 137283, 137284, 137286, 137287, 137289, 137290, 137292, 137293, 137295, 137296, 137298, 137299, 137301, 137302, 137308, 137309, 137311, 137312, 137314, 137315, 137317, 137318, 137321, 137322, 137326, 137327, 137329, 137330, 137332, 137333, 137335, 137336, 137338, 137339, 137341, 137342, 137344, 137345, 137347, 137348, 137350, 137351, 137353, 137354, 137421, 137422, 137423, 137424, 137426, 137427, 137428, 137429, 137431, 137432, 137433, 137434, 137436, 137437, 137438, 137439, 137441, 137442, 137443, 137444, 137446, 137447, 137448, 137449, 137452, 137453, 137454, 137455, 137457, 137458, 137459, 137460, 137462, 137463, 137464, 137465, 137467, 137468, 137469, 137470, 137472, 137473, 137474, 137475, 137477, 137478, 137479, 137480, 137482, 137483, 137484, 137485, 137487, 137488, 137489, 137490, 137492, 137493, 137494, 137495, 137497, 137498, 137499, 137500, 137558, 137559, 137560, 137561, 137563, 137564, 137565, 137566, 137568, 137569, 137570, 137571, 137573, 137574, 137575, 137576, 137583, 137584, 137585, 137586, 137588, 137589, 137590, 137591, 137593, 137594, 137595, 137596, 137598, 137599, 137600, 137601, 137603, 137604, 137605, 137606, 137608, 137609, 137610, 137611, 137613, 137614, 137615, 137616, 137618, 137619, 137620, 137621, 137623, 137624, 137625, 137626, 137628, 137629, 137630, 137631, 137703, 137704, 137705, 137706, 137708, 137709, 137710, 137711, 137713, 137714, 137715, 137716, 137718, 137719, 137720, 137721, 137723, 137724, 137725, 137726, 137728, 137729, 137730, 137733, 137734, 137735, 137736, 137738, 137739, 137740, 137741, 137743, 137744, 137745, 137746, 137748, 137749, 137750, 137751, 137753, 137754, 137755, 137756, 137758, 137759, 137760, 137761, 137763, 137764, 137765, 137766, 137768, 137769, 137770, 137771, 137773, 137774, 137775, 137776, 137778, 137779, 137780, 137781, 138223, 138224, 138226, 138227, 138229, 138230, 138232, 138233, 138235, 138236, 138238, 138239, 138241, 138242, 138245, 138246, 138248, 138249, 138251, 138252, 138254, 138255, 138257, 138258, 138260, 138261, 138263, 138264, 138266, 138267, 138269, 138270, 138272, 138273, 138399, 138400, 138403, 138404, 138406, 138407, 138409, 138410, 138415, 138416, 138418, 138419, 138421, 138422, 138424, 138425, 138427, 138428, 138430, 138431, 138433, 138434, 138436, 138437, 138439, 138440, 138442, 138443, 138445, 138446, 138448, 138449, 138588, 138589, 138592, 138593, 138596, 138597, 138600, 138601, 138604, 138605, 138608, 138609, 138612, 138613, 138616, 138617, 138620, 138621, 138624, 138625, 138628, 138629, 138631, 138632, 138635, 138636, 138639, 138640, 138643, 138644, 138647, 138648, 138651, 138652, 138655, 138656, 138659, 138660, 138807, 138808, 138811, 138812, 138815, 138816, 138819, 138820, 138823, 138824, 138827, 138828, 138831, 138832, 138835, 138836, 138839, 138840, 138843, 138844, 138847, 138848, 138851, 138852, 138855, 138856, 138859, 138860, 138863, 138864, 138867, 138868, 138871, 138872, 138875, 138876, 138988, 138989, 138990, 138991, 138999, 139000, 139003, 139004, 139007, 139008, 139013, 139014, 139017, 139018, 139028, 139029, 139442, 139443, 139445, 139446, 139448, 139449, 139451, 139452, 139530, 139531, 139532, 139533, 139535, 139536, 139537, 139538, 139540, 139541, 139542, 139543, 139545, 139546, 139547, 139553, 139554, 139555, 139556, 139722, 139723, 139725, 139726]
```



## Viewing Fiber Distribution in a Visit

The following code shows the distribution of all fibers (SCIENCE, SKY, FLUX STANDARDS) on the focal plane for a given visit. As before, specify the 2d DRP data repository location and `collection` name, along with the visit number (or increment through visits in the `collection` using a simple index):

```python
import numpy as np
import matplotlib.pyplot as plt
from lsst.daf.butler import Butler
from pfs.datamodel import TargetType

# ==== USER-DEFINED PARAMETERS ====
repo        = "/shared/pfs/programs/S25A-000QF/2d/"  # path to the 2d DRP repository
collections = "run26_June2026"                       # collection name
VISIT       = 137292 # Inspects and plots fiber positions in specified visit
VISIT_INDEX = 0      # Used if VISIT is None. Increment through visits in collections (0 = first, 1 = second, etc.)

# ==== QUERY ALL FULLY-PROCESSED VISITS FROM BUTLER ====
butler     = Butler(repo, collections=collections)
all_visits = sorted({ref.dataId['visit'] for ref in butler.registry.queryDatasets('pfsMerged')})
print(f"Total visits in Collections ({collections}): {len(all_visits)}")

if VISIT is not None:
    if VISIT not in all_visits:
        raise ValueError(f"Visit {VISIT} not found in collections '{collections}'")
    visit = VISIT
    print(f"Using specified visit={visit}")
else:
    visit = all_visits[VISIT_INDEX]
    print(f"Selected visit index {VISIT_INDEX}: visit={visit}")

# ==== LOAD FIBER CONFIGURATION FOR THE SELECTED VISIT ====
pfsConfig = butler.get('pfsConfig', dict(visit=visit))
sci       = pfsConfig.select(targetType=TargetType.SCIENCE,  fiberStatus=1)
sky       = pfsConfig.select(targetType=TargetType.SKY,      fiberStatus=1)
fluxstd   = pfsConfig.select(targetType=TargetType.FLUXSTD,  fiberStatus=1)

# ==== PLOT RA/DEC POSITIONS OF ALL FIBER TYPES FOR THE SELECTED VISIT ====
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
plt.savefig(f'pfsConfig_fiber_distribution_visit={visit}.png', dpi=150, bbox_inches='tight')
plt.show()
```

**Output**:

```
Total visits in Collections (run26_June2026): 426
Using specified visit=137292
```

![Fiber positions for visit 137292](figures/pfsConfig_fiber_distribution_visit=137292.png)

## List all Visits (Exposures) for an Object

If you have the `objId` of a specific object you have observed, the following code prints a summary of all visits that contain that object, including its catalog ID and magnitude.

```python
import numpy as np
from astropy.io import fits
from lsst.daf.butler import Butler
from pfs.datamodel import TargetType

# ==== USER-DEFINED PARAMETERS ====
repo        = "/shared/pfs/programs/S25A-000QF/2d/"  # path to the 2d DRP repository
collections = "run26_June2026"                       # collection name
objid       = 89100543080260387                      # input object id

# ==== GET ALL PFSCONFIG FILE REFERENCES FROM BUTLER ====
butler     = Butler(repo, collections=collections)
all_visits = sorted({ref.dataId['visit'] for ref in butler.registry.queryDatasets('pfsMerged')})
all_refs   = list(butler.registry.queryDatasets('pfsConfig',
                  where=f"visit IN ({','.join(str(v) for v in all_visits)})"))

# ==== SCAN ALL PFSCONFIG FILES TO FIND WHICH VISITS CONTAIN THE OBJECT ====
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
print(f"ObjId={objid} found in {len(objid_visits)} visit(s): {objid_visits}")

# ==== LOAD OBJECT DETAILS FROM THE FIRST MATCHING VISIT ====
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
ObjId=89100543080260387 found in 2 visit(s): [137292, 137293]

Object info (from visit 137292):
  ObjId        = 89100543080260387
  CatId        = 10094
  Spectrograph = 3
  Mag (g_ps1) = 20.816 AB
```

