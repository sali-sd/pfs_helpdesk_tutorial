# Pipeline Installation

## Install Pipeline

---

The basic information of the PFS 2D DRP for this section includes:

1. LSST version: v28 (as of 2025/03/17)
2. pfs_pipe2d branch: master

**Step 1**: We should fetch pfs_pipe2d Gen3:

```bash
cd $WORKDIR/(username)/
git clone http://github.com/Subaru-PFS/pfs_pipe2d
```

**Step 2**: We should check out to the lastest version:

```bash
cd pfs_pipe2d
git checkout $(git describe --tags `git rev-list --tags --max-count=1`)
```

**Step 3**: We should create the target folder and start the installation:

```bash
mkdir -p $WORKDIR/(username)/pfs/stack_28
cd $WORKDIR/(username)/pfs_pipe2d/bin
./install_pfs.sh -t current $WORKDIR/(username)/pfs/stack_28
```

## Install Flux Model Data

---

**Step 1**: Set up the pipe2d environment:

Source the appropriate `loadLSST.*` script for your shell.

```bash
source $WORKDIR/(username)/packages/stack_28/loadLSST.bash
setup pfs_pipe2d
```

**Step 2**: We should fetch the flux model data:

```bash
mkdir -p $WORKDIR/(username)/source/
cd $WORKDIR/(username)/source/
wget https://hscdata.mtk.nao.ac.jp/hsc_bin_dist/pfs/fluxmodeldata-ambre-20230608.tar.gz
tar xzf fluxmodeldata-ambre-20230608.tar.gz -C .
```

**Step 3**: We can start the installation process

```bash
cd $WORKDIR/(username)/source/fluxmodeldata-ambre-20230608
./install.py --prefix=$WORKDIR/(username)/packages/
```

Then we should declare the `fluxmodeldata` package to `eups` by the following command:

```bash
eups declare fluxmodeldata 20230608 -r /path/to/fluxmodeldata
```

## (Optional) Individual Users: Install `drp_pfs_data` Package

---

!!! note
    We expect that this requirement will be removed soon. It's only necessary if you will set up your own repository, specifically, for installing the "curated calibs".

If the PFS pipeline was installed for all users on a server in a public directory, e.g., `$WORKDIR/pfs/`, then for individual users, a local version of `drp_pfs_data` package -- other than the one included in the `pfs_pipe2d` installation above -- is needed.

We can install the local `drp_pfs_data` package as follows:

```bash
cd $WORKDIR/(username)/packages/
git clone https://github.com/Subaru-PFS/drp_pfs_data.git --single-branch
cd drp_pfs_data
git fetch --tags
git checkout $(git describe --tags `git rev-list --tags --max-count=1`)
```
