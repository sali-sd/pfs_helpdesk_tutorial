# Setup Environment and Run Integration Test

After the process is complete, run the following commands to set up the environment (choose the appropriate `loadLSST` script according to your shell):

```bash
source $WORKDIR/$(whoami)/packages/stack_30/loadLSST.bash
setup pfs_pipe2d
```

(Optional) In most cases, users can directly use the shared installation of `drp_pfs_data`. Only in case that one wants to install curated calibs, then for individual users, they should replace the default `drp_pfs_data` package with a local version:

```bash
setup -jr $WORKDIR/$(whoami)/packages/drp_pfs_data
```

The integration test provides a check that the pipeline has been installed and is working properly. It is not a necessary part of the installation. It takes about half an hour to run.

Start the integration test in a new directory:

```bash
mkdir -p /$WORKDIR/$(whoami)/packages/integrationTest
cd $WORKDIR/$(whoami)/packages/integrationTest
pfs_integration_test.sh -c 4 .
```

!!! note
    `-c` specifies the number of cores to be used for parallel processing.