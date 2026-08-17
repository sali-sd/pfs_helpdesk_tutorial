# Science Platform Data Processing Status

All PFS data taken each semester is reduced by PFS team and made available through the [Science Platform](https://hscpfs.mtk.nao.ac.jp/portal/) to users. Here will be provide an up to date status on the data processing for each semester and any missing data. This report is also available through the Science Platform itself and the corresponding release notes therein, though we summarise it here for convenience.

As improvements to the 2d and 1d pipelines are made, the same data can be re-processed multiple times with significant improvements in quality in subsequent releases. As such we recommend using the latest re-processed data.

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

For each run or reprocessing release, any known missing files, incomplete products, or visits excluded from the release (e.g. poor quality / bad weather) are noted below.

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


In addition, the following visits were excluded by a data-quality cut (mostly poor observing conditions / bad weather):

123489, 122048, 122638, 123062, 123065, 123133, 123134, 123138, 123273, 123307, 123372, 123373, 123413, 123414, 123421, 123422, 123498, 123499, 123607, 123608, 123610, 123611, 123613, 123640, 123644, 123649, 123650, 123652, 123653, 123657, 123658, 123660, 123661, 123665, 123666, 123668, 123669, 123671, 123672, 123675, 123676, 123678, 123679, 123681, 123682

### `run22`

There is no missing 2D arm data from processing failures. For 1D data, see the `run25` notes below.

The following visits were excluded by a data-quality cut (mostly poor observing conditions; some very short calibration exposures are also in this list):

125942, 125943, 125944, 125945, 125947, 125948, 125949, 125950, 126416, 126417, 126418, 126455, 126457, 126458, 126466, 126495, 126496, 126543, 126555, 126586, 126587, 126588, 126589, 126648, 126649, 126910, 126911, 126913, 126914, 126918, 126919, 126921, 126922, 126924, 126925, 126927, 126928, 126930, 126931, 126933, 126934, 126941, 126942, 126944, 126945, 126947, 126948, 126419

### `run23`

There is no missing 2D arm data from processing failures. For 1D data, see the `run25` notes below.

The following visits were excluded by data-quality cuts (mostly poor observing conditions; a few visits with bad acquisitions are also included):

127635, 127642, 127743, 127744, 127746, 127747, 127749, 127750, 127752, 127753, 127755, 127756, 127758, 127765, 127766, 127768, 127769, 127771, 127772, 127774, 128047, 128048, 128260, 128261, 128263, 128264, 128266, 128276, 128277, 128280, 128297, 128298, 128300, 128301, 128420, 128428, 128429, 128434, 128441, 128442, 128444, 128445, 128450, 128451, 128453, 128454, 128456, 128457, 128459, 128460, 128600, 128615, 128620, 128722, 128723, 128725, 128726, 128867, 128868, 129223, 129224, 129225, 129227, 129228, 129251

### `S25A`

There is no missing 2D arm data from processing failures. For 1D data, see the `run25` notes below.

Only “good” science visits from `run21`–`run23` were processed through coadd. The quality-excluded visits listed under those runs are therefore also absent from this release (the release note does not reprint a separate exclusion list).

### `run24`

There is no missing 2D arm data from processing failures. For 1D data, see the `run25` notes below.

Only good science visits were processed through coadd (see the visit list in the release note / `fluxCalQA` plots). The release note does not publish a separate list of quality-excluded visits.

### `run25`

There are no missing 2D pipeline raw/arm files. However, a substantial fraction of objects present in `pfsCoadd` are missing from `pfsCoZCandidates`, i.e. 1D data (about 20–30% of files are strongly affected; the fraction depends on the object mix). For the observatory filler (`catId=10094`, modified config), examples include:


| objGroup | N objects (`pfsCoadd`) | N objects (`pfsCoZCandidates`) | Fraction retained |
| -------- | ---------------------- | ------------------------------ | ----------------- |
| 7        | 1462                   | 1182                           | 0.81              |
| 8        | 1217                   | 842                            | 0.69              |
| 12       | 1124                   | 629                            | 0.56              |
| 14       | 1593                   | 322                            | 0.20              |
| 16       | 1551                   | 926                            | 0.60              |


This incompleteness also affected earlier releases. It was later traced to mixed low- and medium-resolution spectra in the same `pfsCoadd` file (see `S25A` take #2 / `run26`).

About 20 additional visits were processed through `fluxCal` but discarded due to bad quality; those visit IDs are not listed in the release note.

### `S25A` take #2

A small number of files are missing from the release as summarized below. These are not due to processing errors but to data acquisition issues during the observations (i.e., the raw data are missing).


| Visit  | Missing arm + spectrograph |
| ------ | -------------------------- |
| 122148 | `n2`                       |
| 122522 | `n2`                       |
| 122896 | `n1`                       |
| 122951 | `n3`                       |
| 123314 | `n4`                       |


The same set of “good” visits as in `S25A` (November 2025) was used, so the quality-excluded visits from `run21`–`run23` remain excluded.

There is also the `pfsCoZCandidates` incompleteness from mixed-resolution coadds (same issue as `run25`); that problem is addressed from `run26` onward by producing separate `brn` and `bmn` coadds.

### `run26`

There are no missing raw/arm files. Separate `brn` / `bmn` coadds resolved the earlier problem of objects missing from `pfsCoZCandidates` when resolutions were mixed in one `pfsCoadd` file.

Science visits were processed through `pfsMerged`, then good visits were selected for coadds using `fluxCalQA`. Visits rejected from coaddition are not listed by ID in the release note; QA plots for those bad visits are included in the release.

### `run27`

No data (no observations for this run).

### `run28`

Processing still in progress.
