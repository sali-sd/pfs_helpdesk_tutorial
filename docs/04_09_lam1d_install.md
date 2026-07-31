# Installing the LAM 1D Pipeline

The LAM 1D pipeline (`drp_1dpipe` / `pylibamazed`) is the Subaru PFS 1D data reduction pipeline developed by LAM (Laboratoire d'Astrophysique de Marseille). It performs redshift fitting and line measurements on coadded PFS spectra.

- **Pipeline**: [drp_1dpipe](https://github.com/Subaru-PFS/drp_1dpipe)
- **Core library**: [drp_1d (pylibamazed)](https://github.com/Subaru-PFS/drp_1d)

An installation script and full documentation are available at:
**[https://github.com/sali-sd/PFS-LAM1D-Installation](https://github.com/sali-sd/PFS-LAM1D-Installation)**

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

| Location                                | Contents                                                                        |
| --------------------------------------- | ------------------------------------------------------------------------------- |
| `~/anaconda3/envs/pfs-pipeline-1.18.0/` | Conda environment with all installed software                                   |
| `~/pfs-pipeline-src/`                   | Downloaded source tarballs and build files (can be deleted after installation)  |

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

A `Dockerfile-almalinux9` is provided in the [drp_1dpipe repository](https://github.com/Subaru-PFS/drp_1dpipe) for users who prefer a containerised environment. This approach requires Docker and root (or sudo) access, making it better suited to personal machines than shared HPC clusters.

### Building the image

Clone the repository and build the image, passing the desired pipeline versions as build arguments:

```bash
git clone https://github.com/Subaru-PFS/drp_1dpipe.git
cd drp_1dpipe

docker build \
    --build-arg D1D_VERSION=pfs-1.18.0 \
    --build-arg D1DP_VERSION=1.18.0 \
    -f Dockerfile-almalinux9 \
    -t pfs-lam1d:1.18.0 .
```

This produces a Docker image named `pfs-lam1d:1.18.0`. The build takes **30–60 minutes** as it compiles all C++ dependencies from source inside the container.

### What the image contains

The image is based on AlmaLinux 9 and installs everything at the system level (into `/usr/local`):

- System tools: `gcc-c++`, `cmake` 3.26.5, SWIG 4.1.1
- C++ libraries: Boost 1.74, OpenBLAS 0.3.19, GSL 2.5, FFTW 3.3.8, Eigen 3.4.0, LBFGSpp 0.4.0
- Python 3.11 with: numpy, astropy, scipy, pytest, jsonschema, and the PFS datamodel
- `drp_1d` (pylibamazed) and `drp_1dpipe` — compiled and installed system-wide

### Running the pipeline in the container

Mount your data and calibration directories into the container and run `drp_1dpipe` directly:

```bash
docker run --rm \
    -v /path/to/calibration:/calibration \
    -v /path/to/data:/data \
    -v /path/to/output:/output \
    pfs-lam1d:1.18.0 \
    drp_1dpipe -j 4 -n0 \
        --workdir /calibration \
        --coadd_file /data/pfsCoadd.fits \
        -o /output \
        -p /calibration/config.json
```

The `-v` flags mount local directories into the container. Results written to `/output` inside the container will appear in `/path/to/output` on your machine.
