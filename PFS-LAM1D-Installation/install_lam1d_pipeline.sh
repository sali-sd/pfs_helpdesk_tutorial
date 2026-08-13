#!/bin/bash
# =============================================================================
# PFS 1D Pipeline installer (conda-based, no root required)
# Installs: drp_1d 1.18.0 + drp_1dpipe 1.18.0
# =============================================================================
set -e  # stop immediately on any error

# ── Versions ──────────────────────────────────────────────────────────────────
D1D_VERSION="1.18.0"
D1D_BRANCH="pfs-1.18.0"
D1DP_VERSION="1.18.0"
D1DP_BRANCH="1.18.0"
DAMD_VERSION="master"
ENV_NAME="pfs-pipeline-${D1DP_VERSION}"

# ── Directories ───────────────────────────────────────────────────────────────
# Source tarballs and git clones go here (separate from the conda env)
WORK_DIR="${HOME}/pfs-pipeline-src"
mkdir -p "${WORK_DIR}"

# ── Helpers ───────────────────────────────────────────────────────────────────
GREEN="\033[32m"
RESET="\033[m"
section() { echo -e "\n${GREEN}── $1 ──${RESET}"; }

# ── Check prerequisites ───────────────────────────────────────────────────────
section "Checking prerequisites"
for cmd in gcc g++ make curl git unzip cmake conda; do
    command -v "$cmd" &>/dev/null || { echo "ERROR: '$cmd' not found. Please install it first."; exit 1; }
done
echo "All prerequisites found."
echo "cmake: $(cmake --version | head -1)"
echo "gcc:   $(gcc --version | head -1)"

# ── Create and activate conda environment ────────────────────────────────────
section "Creating conda environment: ${ENV_NAME}"
eval "$(conda shell.bash hook)"
conda create -y -n "${ENV_NAME}" python=3.11
conda activate "${ENV_NAME}"

# All C++ libraries will be installed into the conda env prefix,
# so cmake can find them automatically when building drp_1d.
INSTALL_PREFIX="${CONDA_PREFIX}"

echo "Python: $(which python3) ($(python3 --version))"
echo "pip:    $(which pip)"
echo "Prefix: ${INSTALL_PREFIX}"

# ── PCRE2 10.42 ──────────────────────────────────────────────────────────────
# Required by SWIG for regex support
section "Building PCRE2 10.42"
cd "${WORK_DIR}"
curl -L https://github.com/PCRE2Project/pcre2/releases/download/pcre2-10.42/pcre2-10.42.tar.gz \
    --output pcre2-10.42.tar.gz
tar xzf pcre2-10.42.tar.gz
cd pcre2-10.42
./configure --prefix="${INSTALL_PREFIX}"
make -j "$(nproc)"
make install

# ── SWIG 4.1.1 ───────────────────────────────────────────────────────────────
# System has SWIG 4.0.2 but drp_1d requires >= 4.1, so we build 4.1.1
section "Building SWIG 4.1.1"
cd "${WORK_DIR}"
curl -L 'https://sourceforge.net/projects/swig/files/swig/swig-4.1.1/swig-4.1.1.tar.gz/download' \
    --output swig-4.1.1.tar.gz
tar xzf swig-4.1.1.tar.gz
cd swig-4.1.1
./configure --prefix="${INSTALL_PREFIX}" --with-pcre2-prefix="${INSTALL_PREFIX}"
make -j "$(nproc)"
make install

# ── Boost 1.74.0 ─────────────────────────────────────────────────────────────
section "Building Boost 1.74.0"
cd "${WORK_DIR}"
curl -L http://downloads.sourceforge.net/project/boost/boost/1.74.0/boost_1_74_0.tar.gz \
    --output boost_1_74_0.tar.gz
tar xzf boost_1_74_0.tar.gz
cd boost_1_74_0
./bootstrap.sh \
    --with-libraries=system,filesystem,program_options,thread,timer,chrono,test \
    --prefix="${INSTALL_PREFIX}"
./b2 -j "$(nproc)" link=shared install

# ── OpenBLAS 0.3.19 ──────────────────────────────────────────────────────────
section "Building OpenBLAS 0.3.19"
cd "${WORK_DIR}"
curl -L https://github.com/xianyi/OpenBLAS/archive/v0.3.19.tar.gz \
    --output openBLAS-0.3.19.tar.gz
tar xzf openBLAS-0.3.19.tar.gz
cd OpenBLAS-0.3.19
# DYNAMIC_ARCH=1 builds support for multiple CPU architectures, selected at runtime
make -j "$(nproc)" NO_LAPACK=1 DYNAMIC_ARCH=1
make install NO_LAPACK=1 DYNAMIC_ARCH=1 PREFIX="${INSTALL_PREFIX}"

# ── GSL 2.5 ──────────────────────────────────────────────────────────────────
section "Building GSL 2.5"
cd "${WORK_DIR}"
curl -L https://ftp.gnu.org/gnu/gsl/gsl-2.5.tar.gz --output gsl-2.5.tar.gz
tar xzf gsl-2.5.tar.gz
cd gsl-2.5
./configure --prefix="${INSTALL_PREFIX}"
make -j "$(nproc)"
make install

# ── FFTW 3.3.8 ───────────────────────────────────────────────────────────────
section "Building FFTW 3.3.8"
cd "${WORK_DIR}"
curl -L https://www.fftw.org/fftw-3.3.8.tar.gz --output fftw-3.3.8.tar.gz
tar xzf fftw-3.3.8.tar.gz
cd fftw-3.3.8
./configure --enable-shared --prefix="${INSTALL_PREFIX}"
make -j "$(nproc)"
make install

# ── Eigen 3.4.0 ──────────────────────────────────────────────────────────────
section "Installing Eigen 3.4.0"
cd "${WORK_DIR}"
curl -L https://gitlab.com/libeigen/eigen/-/archive/3.4.0/eigen-3.4.0.tar.gz \
    --output eigen-3.4.0.tar.gz
tar xzf eigen-3.4.0.tar.gz
cd eigen-3.4.0
mkdir -p build && cd build
cmake .. -DCMAKE_INSTALL_PREFIX="${INSTALL_PREFIX}"
make install

# ── LBFGSpp 0.4.0 ────────────────────────────────────────────────────────────
section "Installing LBFGSpp 0.4.0"
cd "${WORK_DIR}"
curl -L https://github.com/yixuan/LBFGSpp/archive/refs/tags/v0.4.0.zip \
    --output LBFGSpp-0.4.0.zip
unzip -qq LBFGSpp-0.4.0.zip
cd LBFGSpp-0.4.0
mkdir -p build && cd build
cmake .. -DCMAKE_INSTALL_PREFIX="${INSTALL_PREFIX}"
make install

# ── Python packages ───────────────────────────────────────────────────────────
section "Installing Python packages"
pip install --upgrade pip
pip install numpy astropy cython pandas h5py jsonschema scipy pytest pytest-mock ninja

# ── PFS datamodel ─────────────────────────────────────────────────────────────
section "Installing PFS datamodel (${DAMD_VERSION})"
cd "${WORK_DIR}"
git clone https://github.com/Subaru-PFS/datamodel.git
cd datamodel
git checkout "${DAMD_VERSION}"
pip install .

# ── drp_1d (pylibamazed) ──────────────────────────────────────────────────────
section "Installing drp_1d ${D1D_VERSION}"
cd "${WORK_DIR}"
git clone https://github.com/Subaru-PFS/drp_1d.git "drp_1d_${D1D_VERSION}"
cd "drp_1d_${D1D_VERSION}"
git checkout "${D1D_BRANCH}"
pip install . -C cmake.define.CMAKE_PREFIX_PATH="${INSTALL_PREFIX}"

# ── drp_1dpipe ────────────────────────────────────────────────────────────────
section "Installing drp_1dpipe ${D1DP_VERSION}"
cd "${WORK_DIR}"
git clone https://github.com/Subaru-PFS/drp_1dpipe.git "drp_1dpipe_${D1DP_VERSION}"
cd "drp_1dpipe_${D1DP_VERSION}"
git checkout "${D1DP_BRANCH}"
pip install .

# ── Run tests ─────────────────────────────────────────────────────────────────
section "Running tests"
cd "${WORK_DIR}/drp_1dpipe_${D1DP_VERSION}"
python -m pytest

# ── Done ──────────────────────────────────────────────────────────────────────
section "Installation complete!"
echo ""
echo "To use the pipeline, activate the conda environment:"
echo ""
echo "  conda activate ${ENV_NAME}"
echo "  drp_1dpipe --version"
echo ""
echo "Source builds are in: ${WORK_DIR}"
