# Accessing PFS Data Products

PFS data is primary accessed using the [LSST Gen3 Butler](https://pipelines.lsst.io/modules/lsst.daf.butler/index.html),
which provides a uniform interface for reading and writing pipeline products without needing to know the exact file names or paths of every PFS data product on disk.

All PFS data products are stored in **collections** within a butler repository.
A collection is a grouping of PFS data tied to a specific
processing run or observing programme — that allows the butler to locate the correct version of the data seamlessly with a few specific commands.

**Setting up the butler:**

```python
from lsst.daf.butler import Butler

repo        = "/shared/pfs/programs/S25A-000QF/2d/"  # path to the datastore (PFS Filler Program)
collections = "S25A_April2026"                        # named processing collection

butler = Butler(repo, collections=collections)
```

**Querying available visits:**

```python
all_visits = sorted({ref.dataId['visit'] for ref in butler.registry.queryDatasets('pfsMerged')})
print(f"Total visits in collection: {len(all_visits)}")
```

**Loading a data product:**

```python
pfsConfig = butler.get('pfsConfig', dict(visit=122041))
pfsMerged = butler.get('pfsMerged', dict(visit=122041))
```

The string passed to `butler.get()` (e.g. `'pfsConfig'`, `'pfsMerged'`) is the
**dataset type name** — it corresponds directly to the product names described in
the sections below.
