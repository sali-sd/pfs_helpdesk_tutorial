# Data Ingestion

## Data Archive

---

When working with local data, you must first download it from the Subaru data archive for your open-use program, specifically from the [STARS2](https://stars2.naoj.hawaii.edu) database. The archive provides access to science images, calibration data, and `PfsConfig` files.

!!! note
    Details on data retrieval will be provided by the STARS team on the day following your observation.

Typically, you will download a TAR file from the STARS2 website. After that, follow the steps below to extract and access the data on UNIX or macOS:

```bash
# Step 1: Create a directory for downloads
mkdir $WORKDIR/$(whoami)/download_dir 
# Step 2: Copy the downloaded TAR file to the directory
cp S2Query.tar $WORKDIR/$(whoami)/download_dir 
# Step 3: Navigate to the directory
cd $WORKDIR/$(whoami)/download_dir 
# Step 4: Extract the TAR file
tar -xvf S2Query.tar 
# Step 5: Run the unpacking script
./zadmin/unpack.py
```

Platform-specific instructions:

- UNIX: Use wget for downloading.
- macOS: Use curl for downloading.
- Windows: An FTP manager is required for data transfer.

You will also need the `pfsConfig` files created for your program. These custom `pfsConfig` files are available under your program directory, for example, `/shared/pfs/programs/S25A-000QF/2d/customPfsConfig`. Copy these files to your local disk and then ingest them.

## Ingestion to `butler`

---

You can ingest data into the `butler` repository.
There are two types of data that need to be ingested: raw images and `PfsConfig` files.

These are ingested using two separate commands:

```bash
# Assume that we define the destination datastore (`DATASTORE`) and the directory containing the input data (`DATADIR`):
DATASTORE="$WORKDIR/$(whoami)/data/datastore"
DATADIR="$WORKDIR/$(whoami)/data"

# Ingest the raw images taken in March 2026
butler ingest-raws $DATASTORE $DATADIR/raw/2026-03-*/*/PFS*.fits --ingest-task lsst.obs.pfs.gen3.PfsRawIngestTask --transfer link --fail-fast
# Ingest the PfsConfig files for the March 2026 run
ingestPfsConfig.py $DATASTORE PFS PFS/raw/pfsConfig $DATADIR/raw/2026-03-*/pfsConfig/pfsConfig-*.fits --transfer link
```

If you are using `PFSF` files provided by the observatory, they are equivalent to `pfsConfig` files, and a similar command can be used:

```bash
ingestPfsConfig.py $DATASTORE PFS PFS/raw/pfsConfig $DATADIR/raw/2026-03-*/pfsConfig/PFSF*.fits --transfer link
```

For details on the ingested data, refer to the [Appendix](05_01_app_datamodel.md) or the [datamodel](https://github.com/Subaru-PFS/datamodel/tree/master).

For example, the filenames have the following meanings:

- **PFSA12345611.fits**:
  > A raw `science` exposure with `visit=123456`, taken at `site=summit` with `spectrograph=1` using the blue arm (`armNum=1`).
- **PFSB12345623.fits**:
  > A raw `up-the-ramp` exposure with `visit=123456`, taken at `site=summit` with `spectrograph=2` using the IR arm (`armNum=3`).
- **pfsConfig-0xad349fe21234abcd-123456.fits**:
  > A realization of a `PfsDesign` with `pfsDesignId=ad349fe21234abcd` for `visit=123456`.
- **PFSF12345600.fits**:
  > A realization of a `PfsDesign` used by the observatory for `visit=123456`. In the final two digits, `00` indicates the original full `PfsConfig` (`PFSF`) file; `01`-`99` indicate customized `PFSF` files containing fibers associated with a specific proposal ID together with calibration fibers (for example, sky and flux fibers). The observatory will provide the customized `PFSF` files with `01`-`99` in the final two digits. If the `PFSF` file contains only one proposal ID or one calibration frame, the `00` file will be distributed. The ingestion procedure is the same as for a `PfsConfig` file.

The parameters in the commands include:

- `--transfer`: The method used to add data to the repository. The options include `link`, `copy`, and `move`, which specify whether the data is symlinked, duplicated, or physically relocated, respectively.
- `--fail-fast`: Stops the ingestion process immediately if an error occurs. This is useful for debugging. If you do not need this behavior, omit this option.

The ingestion process places the files (referred to as "datasets" in the `butler`) in the repository and records them in the registry database. Each file is placed in a **collection**, which can be thought of as a directory-like grouping in the `butler` (and, when using a traditional filesystem datastore, it is implemented as a directory).

The raw data is placed in the collection `PFS/raw/sps`, while the `PfsConfig` files are placed in the collection `PFS/raw/pfsConfig`.

For each observing program the custom pfsConfig files can be found on the [Science Platform](https://hscpfs.mtk.nao.ac.jp/portal/):  
`/shared/pfs/programs/$PROPOSAL_ID/2d/customPfsConfig/`

## Troubleshooting

When ingesting data into `DATASTORE`, all files for a single visit should be ingested with a single command. For example, the following commands ingest two files from `visit=123456` separately and will fail:

```bash
# The second command will fail
butler ingest-raws $DATASTORE $DATADIR/raw/2026-03-18/sps/PFSA12345601.fits --ingest-task lsst.obs.pfs.gen3.PfsRawIngestTask --transfer link --fail-fast
butler ingest-raws $DATASTORE $DATADIR/raw/2026-03-18/sps/PFSA12345602.fits --ingest-task lsst.obs.pfs.gen3.PfsRawIngestTask --transfer link --fail-fast
```

The correct approach is to use wildcards so that all files from `visit=123456` are included at once:

```bash
butler ingest-raws $DATASTORE $DATADIR/raw/2026-03-18/*/PFS*123456*.fits --ingest-task lsst.obs.pfs.gen3.PfsRawIngestTask --transfer link --fail-fast
```

If you need to re-ingest one or more visits, you can prune the previously ingested data and then repeat the procedure above:

```bash
butler prune-datasets $DATASTORE PFS/raw/sps --datasets=raw --unstore --where="instrument='PFS' AND visit=123456"
# Additional dimensions can be specified by using an SQL expression
butler prune-datasets $DATASTORE PFS/raw/sps --datasets=raw --unstore --where="instrument='PFS' AND visit IN (123456,123457) AND arm='n' AND spectrograph='3'"
```

## Dataset

Each dataset is specified by a `dataId`, which is a dictionary of key-value pairs representing the dimensions.

For example,

- A `raw` image may have a `dataId` such as {'`instrument`': '`PFS`', '`visit`': `123`, '`arm`': '`r`', '`spectrograph`': `3`}.
- A `PfsConfig` file is valid for an entire exposure, so it may have a `dataId` such as {'`instrument`': '`PFS`', '`visit`': `123`}.

**IMPORTANT**: In general, users should treat the files in the datastore as a `butler` implementation detail, and use the `butler` commands and Python API to access the data products.

There are some kinds of datastores that do not use a traditional filesystem (e.g., the S3 datastore), and so the files may not be directly accessible.

!!! warning
    The registry database tracks all files in the datastore. Do not delete files from the datastore without using the appropriate `butler` commands.

You can see what raw datasets are in the datastore with the following command:

```bash
butler query-datasets $DATASTORE --collections PFS/raw/sps
```

The result looks something like this:

```bash
type     run                         id                 instrument arm dither pfs_design_id spectrograph detector   visit
---- ------------- ------------------------------------ ---------- --- ------ ------------- ------------ -------- --------
raw  PFS/raw/all 27217522-a357-5071-a32b-af97b5b8bee6          PFS   b  0.0             1            1        0        0
raw  PFS/raw/all 0ce0cbea-fe7c-589e-8259-30060bf20500          PFS   b  0.0             1            1        0        1
[...]
raw  PFS/raw/all 570092eb-f571-5631-8d20-11acbeabc640          PFS   r  0.0             3            1        1        26
raw  PFS/raw/all f8e3ae71-2cdf-5e55-bc42-4a4fb913770c          PFS   r  0.0             4            1        1        27
```

Datasets can be accessed from Python using the `butler` API:

```bash
from lsst.daf.butler import Butler

butler = Butler.from_config($DATASTORE, collections="PFS/raw/sps")
raw = butler.get("raw", instrument="PFS", visit=12, arm="r", spectrograph=1)
rawImage = raw.getImage()
```

The raw data returned from the `butler` is of type `PfsRaw`, which provides a common interface for both CCD and NIR detectors.

You can use `butler.get("raw.exposure", ...)` to get the exposure from the raw data directly.

## The Default Collection

You can create a `CHAIN` collection, `PFS/defaults`, to combine all of the collections created earlier:

```bash
butler collection-chain $DATASTORE PFS/defaults PFS/raw/pfsConfig PFS/raw/sps PFS/calib
```

This is the collection that users will probably use for most pipeline tasks.
