# PFS LAM1D Pipeline Installation

Installation script for the PFS 1D data reduction pipeline, developed by LAM (Laboratoire d'Astrophysique de Marseille). The links to the pipeline GitHub pages are below for reference:

- **Pipeline**: [drp_1dpipe](https://github.com/Subaru-PFS/drp_1dpipe)
- **Core library**: [drp_1d (pylibamazed)](https://github.com/Subaru-PFS/drp_1d)
- **Version installed**: 1.18.0 (adjustable)

---

## Requirements

**Operating system:** AlmaLinux 9 (tested and supported)

**Required tools** (other than Anaconda, all others should be included in AlmaLinux 9 by default):


| Tool           | Purpose                                               |
| -------------- | ----------------------------------------------------- |
| `conda`        | Python environment management (Miniconda or Anaconda) |
| `gcc` / `g++`  | C++ compiler for building native libraries            |
| `cmake` ≥ 3.15 | Build system                                          |
| `make`         | Build tool                                            |
| `git`          | Cloning source repositories                           |
| `curl`         | Downloading source tarballs                           |
| `unzip`        | Extracting zip archives                               |


**Disk space:** ~10 GB free in your home directory

**Note:** Root / sudo access is **not** required. Everything installs into your home directory.

---



## Installation

```bash
bash install_lam1d_pipeline.sh
```

The script takes approximately **30–60 minutes** to complete, as it compiles several C++ libraries from source.

When finished, activate the environment and confirm the version:

```bash
conda activate pfs-pipeline-1.18.0
drp_1dpipe --version
```



### What the script does

The script performs the following steps in order:

1. **Checks prerequisites** — verifies all required tools are available
2. **Creates a conda environment** — `pfs-pipeline-1.18.0` with Python 3.11
3. **Builds C++ dependencies from source** (all installed into the conda environment, no root needed):
  - PCRE2 10.42 — regex library required by SWIG
  - SWIG 4.1.1 — generates Python bindings for the C++ code
  - Boost 1.74.0 — C++ utility libraries
  - OpenBLAS 0.3.19 — optimised linear algebra (built with multi-architecture support)
  - GSL 2.5 — GNU Scientific Library
  - FFTW 3.3.8 — Fast Fourier Transform library
  - Eigen 3.4.0 — C++ linear algebra header library
  - LBFGSpp 0.4.0 — L-BFGS optimiser header library
4. **Installs Python packages** — numpy, astropy, cython, pandas, h5py, jsonschema, scipy, pytest, ninja
5. **Installs PFS datamodel** — from the Subaru-PFS GitHub
6. **Installs drp_1d (pylibamazed)** — the core C++ algorithms library, compiled against the dependencies above
7. **Installs drp_1dpipe** — the Python pipeline
8. **Runs the test suite** — verifies the installation is working correctly



### Install locations


| Location                                | Contents                                                                       |
| --------------------------------------- | ------------------------------------------------------------------------------ |
| `~/anaconda3/envs/pfs-pipeline-1.18.0/` | Conda environment with all installed software                                  |
| `~/pfs-pipeline-src/`                   | Downloaded source tarballs and build files (can be deleted after installation) |




### Selecting Pipeline Version

The following variables at the top of `install_lam1d_pipeline.sh` can be changed to choose the version of the pipeline to be installed:

```bash
D1D_VERSION="1.18.0"      # drp_1d version number (used for local directory naming only)
D1D_BRANCH="pfs-1.18.0"   # drp_1d git tag used for checkout (always prefixed with "pfs-")
D1DP_VERSION="1.18.0"     # drp_1dpipe version number (used for local directory naming only)
D1DP_BRANCH="1.18.0"      # drp_1dpipe git tag used for checkout
```

To find available versions, check the tags on each repository:

- [drp_1dpipe tags](https://github.com/Subaru-PFS/drp_1dpipe/tags)
- [drp_1d tags](https://github.com/Subaru-PFS/drp_1d/tags)

Note: `drp_1d` tags are always prefixed with `pfs-` (e.g. `pfs-1.18.0`), while `drp_1dpipe` tags are not (e.g. `1.18.0`).

---



## Running the pipeline

Once installed, activate the conda environment and run:

```bash
conda activate pfs-pipeline-1.18.0

drp_1dpipe -j <cores> -n0 \
    --workdir <path/to/working/directory> \
    --coadd_file <path/to/input/pfsCoadd/file> \
    -o <path/to/output/directory> \
    -p <path/to/parameters/file>
```

Example with real parameters:

```bash
drp_1dpipe -j 20 -n0 \
    --workdir /home/sali/1dval/lam1d \
    --coadd_file /lfs_pfs/Subaru/PFS/data/datastore_20260226/PFS/science/run26/coadd.20260430/brn/20260528T144720Z/pfsCoadd/10094/pfsCoadd_PFS_brn_run26_10094_1_PFS_science_run26_coadd_20260430_brn_20260528T144720Z.fits \
    -o /home/sali/1dval/lam1d/results \
    -p /home/sali/1dval/lam1d/parameters_ex.json
```



### Main parameters


| Parameter                | Description                                                                                                                                                               |
| ------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `-j <cores>`             | Number of CPU cores to use in parallel. Use `$(nproc)` to use all available cores, or specify a number (e.g. `-j 20`). Each spectrum takes about 8-10 minutes to process. |
| `-n0`                    | No limit on the number of spectra per bunch — processes all spectra in the input file in one go. Increase if memory is limited.                                           |
| `--workdir`              | Path to the working directory. Must contain a `calibration/` subdirectory with `LSF/`, `templates/`, `linecatalogs/` etc. inside it.                                      |
| `--coadd_file`           | Full path to the input `pfsCoadd` FITS file containing the coadded spectra to process                                                                                     |
| `-o`                     | Output directory where results (`pfsCoZcandidates` FITS files) will be written.                                                                                           |
| `-p`                     | Full path to the JSON parameter file controlling pipeline parameters (wavelength range, line fitting options etc.)                                                        |
| `--scheduler` (optional) | Job scheduler: `local` (default), `pbs`, or `slurm`. Use `pbs` or `slurm` for cluster batch submission.                                                                   |
| `--loglevel` (optional)  | Logging verbosity: `DEBUG`, `INFO` (default), `WARNING`, `ERROR`, `CRITICAL`                                                                                              |




### Config file

The full list of available parameters and their default values is defined in [drp_1dpipe/auxdir/parameters_sgq.json](https://github.com/Subaru-PFS/drp_1dpipe/blob/master/drp_1dpipe/auxdir/parameters_sgq.json) on the pipeline GitHub page. The user only needs to specify parameters they want to override — any parameter not included in the parameter file falls back to the pipeline's default values.

A working example parameter file (`parameters_ex.json`) is included in this repository. It explicitly sets only three parameters:

- `lambdaRange` — wavelength range to process: `[4000, 9600]` Å
- `lsf.gaussianVariableWidthFileName` — path to the LSF file relative to the `calibration/` directory: `LSF/lsf_lowres_fixed.fits`
- `spectrumModel_galaxy.lineMeasSolver.lineMeasSolve.lineModel.lineTypeFilter` — set to `"no"` to measure all spectral lines (both emission and absorption) for galaxies, without restricting to a specific line type

All other parameters fall back to the pipeline defaults.

Once the pipeline is running, the full set of parameters used (defaults + overrides) is written to `parameters.json` in the output directory, alongside `config.json`, `data/`, `log/`, and `report.json`.

### Calibration files

Calibration files (templates, line catalogs, LSF files, IGM/ISM tables) are required to run the pipeline. The calibration files used for version `1.18.0` of the pipeline are included in this repository, though please note that these files may be updated over time. The latest calibration files are available at:

```
https://pfs.ipmu.jp/internal/devarch/lam-drp1d/
```



### Outputs

The pipeline writes one `pfsCoZcandidates` FITS file per `pfsCoadd` fits file into the output directory. Each file contains redshift candidates, probability distributions, and line measurements for all spectra in the `pfsCoadd` file.

---



## Alternative: Docker installation

A `Dockerfile` is provided in the [drp_1dpipe repository](https://github.com/Subaru-PFS/drp_1dpipe) for users who prefer a containerised environment. This approach requires Docker and root access, making it better suited to personal machines than shared HPC clusters.