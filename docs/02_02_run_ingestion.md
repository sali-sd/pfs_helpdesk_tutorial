# Data Ingestion

## Data Archive

---

When working with local data, you must first download them from the Subaru data archive for your open-use programs, specifically from the [STARS2](https://stars2.naoj.hawaii.edu) database. The archive provides access to science images, calibration data, and `PfsConfig` files.

!!! note
    Details on data retrieval will be provided by the STARS team on the day following your observation.

In principle, you need to download a TAR file from the STARS2 website. After that, follow the steps below to extract and access the data on UNIX or macOS:

``` Python
# Step 1: Create a directory for downloads
$ mkdir /download_dir 
# Step 2: Copy the downloaded TAR file to the directory
$ cp S2Query.tar /download_dir 
# Step 3: Navigate to the directory
$ cd /download_dir 
# Step 4: Extract the TAR file
$ tar -xvf S2Query.tar 
# Step 5: Run the unpacking script
$ ./zadmin/unpack.py
```

Platform-Specific Instructions:

- UNIX: Use wget for downloading.

- macOS: Use curl for downloading.

- Windows: An FTP manager is required for data transfer.

## Ingestion to `butler`

---

We can ingest data into the `butler` repository.
There are two kinds of data that we need to ingest: raw images and the `PfsConfig` files.

These are ingested using two separate commands:

``` bash
# Assume that we define a database to be ingested (DATASTORE) and the directory with the input data (DATADIR):
DATASTORE="$WORKDIR/pfs/data/datastore"
DATADIR="$WORKDIR/pfs/data"

# Ingest the raw images taken on Oct. 2024
$ butler ingest-raws $DATASTORE $DATADIR/raw/2024-10-*/*/PFS[A-B]*.fits --ingest-task lsst.obs.pfs.gen3.PfsRawIngestTask --transfer link --fail-fast
# Ingest the PfsConfig files for the Oct. 2024 run
$ ingestPfsConfig.py $DATASTORE PFS PFS/raw/pfsConfig $DATADIR/raw/2024-10-*/pfsConfig/pfsConfig-*.fits --transfer link
```

In case of `PFSF` files used by the observatroy, they are the same to `pfsConfig` files, and the similar command works:

```bash
ingestPfsConfig.py $DATASTORE PFS PFS/raw/pfsConfig $DATADIR/raw/2024-10-*/pfsConfig/PFSF*.fits --transfer link
```

The details of ingested data can be refered to the [Appendix](05_01_app_datamodel.md) or the [datamodel](https://github.com/Subaru-PFS/datamodel/tree/master).

For example, the file names have the meanings:

- **PFSA12345611.fits**:
  > Raw `science` exposure, `visit=123456`, taken on the `site=summit` with `spectrograph=1` using the blue arm (`armNum=1`)

- **PFSB12345623.fits**:
  > Raw `up-the-ramp` exposure, `visit=123456`, taken at the `site=summit` with `spectrograph=2` using the IR arm (`armNum=3`)

- **pfsConfig-0xad349fe21234abcd-123456.fits**:
  > The realisation of a `PfsDesign` with `pfsDesignId=ad349fe21234abcd` for `visit=123456`.

- **PFSF12345600.fits**:
  > The realisation of a `PfsDesign` used by the observatory for `visit=123456`. In the final two digits, `00` means the original full `PfsConfig` (`PFSF`) file; `01`-`99` are for the customized `PFSF` with the fibers belonging to only a specific proposal ID and calibration fibers (sky, flux, and etc.). The observatory will provide the customized `PFSF` file with `01`-`99` in the final two digits. If the `PFSF` file contain only one proposal ID or calibration frame the `00` files will be distributed. The ingestion process is similar to that for a `PfsConfig` file.
  
The parameters in the commands include:

- `--transfer`: The method by which data is added to the repository, including `link`, `copy`, and `move`, which specify whether the data is symlinked, duplicated, or physically relocated, respectively.
- `--fail-fast`: The process will immediately stop the ingestion process if an error occurs. This is useful for debugging. If this is not considered a useful feature, exclude this option.

The ingestion process places the files (referred to as “datasets” in the `butler`) in the repository and records them in the registry database. Each file is placed in a **collection**, which can be thought of as a *directory* in the `butler` (and in the case of the datastore on a traditional filesystem, it is implemented as a directory).

The raw data is placed in the collection <instrument\>/raw/all, while we’ve specified above that the `PfsConfig` files are placed in the collection `PFS/raw/pfsConfig`.

There are different kinds of [collections](https://pipelines.lsst.io/modules/lsst.daf.butler/organizing.html#collections):

- `RUN` collection always associates the datasets.
- `CALIBRATION` collections associate datasets with a timespan indicating the validity range.
- `CHAINED` collections provide a search path through multiple collections.

Each dataset is specified by a “`dataId`”, which is a dictionary of key-value pairs representing the dimensions.

For example,

- `raw` image may have a `dataId` like {'`instrument`': '`PFS`', '`visit`': `123`, '`arm`': '`r`', '`spectrograph`': `3`}.
- `PfsConfig` file is valid for an entire exposure, so may have a `dataId` like {'`instrument`': '`PFS`', '`visit`': `123`}.

**IMPORTANT**: In general, users should treat the files in the datastore as a `butler` implementation detail, and use the `butler` commands and Python API to access the data products.

There are some kinds of datastores that do not use a traditional filesystem (e.g., the S3 datastore), and so the files may not be directly accessible.

!!! warning
    The registry database tracks all files in the datastore. Do not delete files from the datastore without using the appropriate `butler` commands.

You can see what raw datasets are in the datastore with the following command:

```bash
butler query-datasets $DATASTORE --collections PFS/raw/all
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

butler = Butler.from_config($DATASTORE, collections="PFS/raw/all")
raw = butler.get("raw", instrument="PFS", visit=12, arm="r", spectrograph=1)
rawImage = raw.getImage()
```

The raw data returned from the `butler` is of type `PfsRaw`, which provides a common interface for both CCD and NIR detectors.

You can use `butler.get("raw.exposure", ...)` to get the exposure from the raw data directly.
