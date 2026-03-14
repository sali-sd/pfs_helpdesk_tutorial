# Upgrade the Pipeline

After installing the pipeline, users can easily upgrade the 2D DRP packages with the `eups` command. This fetches compiled tarball packages from the server hosted by the PFS team in Mitaka and installs them into the current LSST stack.

!!! Attention
    Occasionally, a new version requires a fresh `datastore` directory. In that case, you will need to rebuild the data directory. \
    Rarely, a new version requires a new LSST stack. In that case, you will need to repeat the entire installation. \
    In either case, the upgrade process does not notify you about these changes, so it is always a good idea to check the [changelog](https://hscpfs.mtk.nao.ac.jp/pfs-drp-2d/changelog/) before upgrading.

## Check available packages

The first step is to set up the LSST environment and add the PFS repository server to the `EUPS_PKGROOT` environment variable:

```bash
source $WORKDIR/$(whoami)/packages/stack_30/loadLSST.bash
EUPS_PKGROOT="https://hscpfs.mtk.nao.ac.jp/pfs-drp-2d/src|https://hscpfs.mtk.nao.ac.jp/pfs-drp-2d/Linux64|$EUPS_PKGROOT"
```

To browse the available versions, use the following `eups` command:

```bash
eups distrib list pfs_pipe2d
```

## Install the latest version

After identifying the latest version number of the `pfs_pipe2d` package, run the following commands to start the installation:

```bash
setup sconsUtils
eups distrib install pfs_pipe2d <version> -t current
```

This process will upgrade all the following packages:

```text
Subaru-PFS/datamodel
Subaru-PFS/pfs_utils
Subaru-PFS/drp_pfs_data
Subaru-PFS/obs_pfs
Subaru-PFS/drp_stella_data
Subaru-PFS/drp_stella
Subaru-PFS/pfs_pipe2d
```

The `-t current` option tags the `pfs_pipe2d` version you installed by this command as the default choice when you run:

```bash
setup pfs_pipe2d
```
