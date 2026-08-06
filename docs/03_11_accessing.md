# Accessing PFS Data Products

## LSST Butler

PFS data is primarily accessed using the [LSST Gen3 Butler](https://pipelines.lsst.io/modules/lsst.daf.butler/index.html),
which provides a uniform interface for reading and writing pipeline products without needing to know the exact file names or paths of every PFS data product on disk.

All PFS data products are stored in `collections` within a `Butler` repository.
A `collection` is a grouping of PFS data tied to a specific
processing run or observing programme — that allows `Butler` to locate the correct version of the data seamlessly with a few specific commands.

## Setting up Butler

Before any data can be analyzed, one must first provide the location of the 2D DRP datastore repository where the reduced data products are stored. For our reference dataset (see [Overview of PFS Data Products](03_10_overview.md) for details), the datastore is located at `/shared/pfs/programs/S25A-000QF/2d/`:

```
$ ls /shared/pfs/programs/S25A-000QF/2d/

S25A_April2026      butler.yaml      customPfsConfig  run21_June2025   run22_July2025
S25A_November2025   butler.yaml.bak  gen3.sqlite3     run23_August2025 run24_November2025
run25_February2026  run26_June2026
```

The `butler.yaml` and `gen3.sqlite3` mark this directory as the root of the butler repository. Each sub-directory (e.g. `S25A_April2026`, `run26_June2026`) corresponds to a different `collection` — a named set of data products from a particular processing run or observing semester. We will use `S25A_April2026` as our reference `collection` going forward, which contains all reduced data observed during the S25A semester (Feb-July 2025) and reduced on April 2026. As improvements to the pipeline are made, newer reductions will be available in the future.

```python
from lsst.daf.butler import Butler

repo        = "/shared/pfs/programs/S25A-000QF/2d/"  # path to the 2d DRP repository
collections = "S25A_April2026"                       # collection name

butler = Butler(repo, collections=collections)
```

Now that `Butler` is ready, we can proceed to look at the individual data products.