# Installing the LAM 1D Pipeline

The LAM 1D pipeline is the PFS 1D data reduction pipeline developed by LAM (Laboratoire d'Astrophysique de Marseille). It performs redshift fitting and line measurements on coadded PFS spectra.

- **Pipeline**: [drp_1dpipe](https://github.com/Subaru-PFS/drp_1dpipe)
- **Core library**: [drp_1d (pylibamazed)](https://github.com/Subaru-PFS/drp_1d)
- **Datamodel**: [datamodel.txt](https://github.com/Subaru-PFS/datamodel/blob/master/datamodel.txt)

See the above pipeline repositories and datamodel page for a full description of the pipeline, its input parameters and output data products.

An installation script and full documentation are available at: **[https://github.com/sali-sd/PFS-LAM1D-Installation](https://github.com/sali-sd/PFS-LAM1D-Installation)**

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

!!! note
    Root / sudo access is **not** required. Everything installs into your home directory.

---



## Installation

Download the installation script from the [PFS-LAM1D-Installation repository](https://github.com/sali-sd/PFS-LAM1D-Installation):

```bash
curl -O https://raw.githubusercontent.com/sali-sd/PFS-LAM1D-Installation/main/install_lam1d_pipeline.sh
```

Then run it:

```bash
bash install_lam1d_pipeline.sh
```

The script takes approximately **30–60 minutes** to complete, as it compiles several C++ libraries from source.

When finished, activate the environment and confirm the version:

```bash
conda activate pfs-pipeline-1.18.0
drp_1dpipe --version
```

---



## What the script does

The script performs the following steps automatically:

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

---



## Install locations


| Location                                | Contents                                                                       |
| --------------------------------------- | ------------------------------------------------------------------------------ |
| `~/anaconda3/envs/pfs-pipeline-1.18.0/` | Conda environment with all installed software                                  |
| `~/pfs-pipeline-src/`                   | Downloaded source tarballs and build files (can be deleted after installation) |


---



## Selecting a pipeline version

The version installed can be changed by editing the variables at the top of `install_lam1d_pipeline.sh` before running it:

```bash
D1D_VERSION="1.18.0"      # drp_1d version number (used for local directory naming only)
D1D_BRANCH="pfs-1.18.0"   # drp_1d git tag used for checkout (always prefixed with "pfs-")
D1DP_VERSION="1.18.0"     # drp_1dpipe version number (used for local directory naming only)
D1DP_BRANCH="1.18.0"      # drp_1dpipe git tag used for checkout
```

To find available versions, check the tags on each repository:

- [drp_1dpipe tags](https://github.com/Subaru-PFS/drp_1dpipe/tags)
- [drp_1d tags](https://github.com/Subaru-PFS/drp_1d/tags)

!!! note
    `drp_1d` tags are always prefixed with `pfs-` (e.g. `pfs-1.18.0`), while `drp_1dpipe` tags are not (e.g. `1.18.0`).

---



## Alternative: Docker installation

A `Dockerfile-almalinux9` is provided in the [drp_1dpipe repository](https://github.com/Subaru-PFS/drp_1dpipe) for users who prefer a containerised environment. This approach requires Docker and root (or sudo) access, making it better suited to personal machines than shared clusters. Installation instructions are provided in the above pipeline repository page. 