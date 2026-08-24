# Science Platform Data Processing Status

All PFS data taken each semester is reduced by the PFS team and made available through the [Science Platform](https://hscpfs.mtk.nao.ac.jp/portal/) to users. Preliminary data releases are initially made following each observing run (carried out across ~2 months, e.g. run21, run22, run23), followed by a complete semester wide data release (e.g. S25A). As improvements to the 2D and 1D pipelines are made, the PFS team may re-process data from earlier semesters (e.g. S25A take#2). The latest re-processed data will thus provide the best results in almost all cases.

Here we provide an up to date status on the data processing for each semester and any missing data. The full data release reports are available through the Science Platform and we recommend users to consult them. Below is a brief summary:

## Data Delivery Status


| Run            | Observing period | 2D results  | LAM 1D results | Calibrations | Release     |
| -------------- | ---------------- | ----------- | -------------- | ------------ | ----------- |
| `run21`        | Mar–Apr 2025     | Complete    | Complete       | Complete     | Jun 2025    |
| `run22`        | May–Jun 2025     | Complete    | Complete       | Complete     | Jul 2025    |
| `run23`        | Jun–Jul 2025     | Complete    | Complete       | Complete     | Aug 2025    |
| `S25A`         | run21–23         | Complete    | Complete       | Complete     | Nov 2025    |
| `run24`        | Sep 2025         | Complete    | Complete       | Complete     | Nov 2025    |
| `run25`        | Nov 2025         | Complete    | Complete       | Complete     | Feb 2026    |
| `S25A` take #2 | run21–23         | Complete    | Complete       | Complete     | Apr 2026    |
| `run26`        | Jan 2026         | Complete    | Complete       | Complete     | Jun 2026    |
| `run27`        | Mar 2026         | No Data     | No Data        | No Data      | No Data     |
| `run28`        | May 2026         | In Progress | In Progress    | In Progress  | In Progress |


## Missing Data

For each run or reprocessing release, any known missing files or incomplete products are noted below.

### `run21`

The following arms are missing due to processing failures. Due to the way flux calibration works, visits with missing `r`/`m` arms do not contribute to the coadd.


| Visit  | Missing arm + spectrograph    |
| ------ | ----------------------------- |
| 122148 | `n2`                          |
| 122195 | `b1` `b2` `b4` `m2`           |
| 122196 | `b1` `b2` `b4` `m2`           |
| 122305 | `r4`                          |
| 122522 | `n2`                          |
| 122733 | `b1` `b2` `b4` `r1` `r2` `r4` |
| 122734 | `b1` `b2` `b4` `r1` `r2` `r4` |
| 122776 | `b4` `r4`                     |
| 122777 | `b4` `r4`                     |
| 122778 | `b4` `r4`                     |
| 122779 | `b4` `r4`                     |
| 122896 | `n1`                          |
| 122951 | `n3`                          |
| 123314 | `n4`                          |


### `run22`

There is no missing 2D arm data from processing failures. For 1D data, see the `run25` notes below.

### `run23`

There is no missing 2D arm data from processing failures. For 1D data, see the `run25` notes below.

### `S25A`

There is no missing 2D arm data from processing failures. For 1D data, see the `run25` notes below.

### `run24`

There is no missing 2D arm data from processing failures. For 1D data, see the `run25` notes below.

### `run25`

There are no missing 2D pipeline raw/arm files. However, a substantial fraction of objects present in `pfsCoadd` are missing from `pfsCoZCandidates`, i.e. 1D data (about 20–30% of files are strongly affected; the fraction depends on the object mix). For the observatory filler (`catId=10094`, modified config), examples include:


| objGroup | N objects (`pfsCoadd`) | N objects (`pfsCoZCandidates`) | Fraction retained |
| -------- | ---------------------- | ------------------------------ | ----------------- |
| 7        | 1462                   | 1182                           | 0.81              |
| 8        | 1217                   | 842                            | 0.69              |
| 12       | 1124                   | 629                            | 0.56              |
| 14       | 1593                   | 322                            | 0.20              |
| 16       | 1551                   | 926                            | 0.60              |


This incompleteness also affected earlier releases. It was later traced to mixed low- and medium-resolution spectra in the same `pfsCoadd` file. A fix is implemented from`run26` onwards.

### `S25A` take #2

A small number of files are missing from the release as summarized below. These are not due to processing errors but to data acquisition issues during the observations (i.e., the raw data are missing).


| Visit  | Missing arm + spectrograph |
| ------ | -------------------------- |
| 122148 | `n2`                       |
| 122522 | `n2`                       |
| 122896 | `n1`                       |
| 122951 | `n3`                       |
| 123314 | `n4`                       |


There is also the `pfsCoZCandidates` incompleteness from mixed-resolution coadds (same issue as `run25`). that problem is addressed from `run26` onward.

### `run26`

There are no missing raw/arm files. Separate `brn` / `bmn` coadds resolved the earlier problem of objects missing from `pfsCoZCandidates` when resolutions were mixed in one `pfsCoadd` file. In all releases from this run onwards, all data will be split into `brn` and `bmn` combinations that the user will have to specify.

### `run27`

No data (no observations for this run).

### `run28`

Processing still in progress.
