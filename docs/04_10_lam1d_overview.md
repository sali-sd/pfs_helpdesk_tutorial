# Overview of LAM 1D Data Products

## What is the LAM 1D DRP?

The **LAM 1D DRP** (Data Reduction Pipeline) is a spectral analysis pipeline developed by the Laboratoire d'Astrophysique de Marseille (LAM). It operates downstream of the PFS 2D DRP and takes flux-calibrated, coadded spectra as input to perform:

- **Redshift determination** — fitting galaxy, QSO, and stellar templates to estimate redshifts or radial velocities
- **Object classification** — classifying each spectrum as `GALAXY`, `QSO`, or `STAR` with associated probabilities
- **Emission and absorption line measurements** — measuring line fluxes, widths, equivalent widths, and velocities
- **Quality assessment** — flagging spectra with warnings and errors at each stage of the pipeline

The core fitting engine is the **`drp_1d`** library (also known as `pylibamazed`), developed and maintained by LAM.

## Input and Output

The LAM 1D DRP consumes the flux-calibrated coadded spectra from the 2D DRP and produces redshift candidate collections:

| Input | Description |
|-------|-------------|
| `pfsCoadd` | Coadded, flux-calibrated spectra across multiple visits |

| Output | Description |
|--------|-------------|
| `pfsCoZCandidates` | Coadded redshift candidates collection, following `pfsCoadd` logic — one file per `catId` |

`pfsCoZCandidates` is the output for science analysis. It bundles results for all objects in a catalog into a single file per `catId`, containing redshift candidates, classification probabilities, PDF grids, line measurements, and quality flags for each object.

## Version Keywords

The PDU of every `pfsCoZCandidates` file records the software versions used to produce it:

| Keyword | Description |
|---------|-------------|
| `D1D_VER` | Version of the `drp_1d` library |
| `D1DP_VER` | Version of the `drp_1dpipe` pipeline |
| `DAMD_VER` | Version of the PFS data model |
| `D2D_VER` | Version of `stella` (2D DRP) |
| `OBS_VER` | Version of `obs_pfs` |
| `U_PARAM` | User parameters (JSON string) |
