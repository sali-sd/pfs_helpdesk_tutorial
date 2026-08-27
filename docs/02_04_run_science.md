# Process Science Data

## Basic Information

---

With the calibration products built, we can now process the science data. There are a few pipelines available:

- **observing**:
  > It processes a visit through merging arms, producing `postISRCCD`, `pfsArm`, `lines`, `detectorMap`, `pfsMerged`, `sky1d`, and `fiberNorms`.
  > This uses a basic, single-exposure cosmic-ray identification algorithm, which is not as reliable as the one used by `reduceExposure`. It is intended for use while observing, when visit groupings aren't known.
  > The `fiberNorms` dataset is only produced for quartz exposures. Unlike the `fiberNorms_calib` product, this is a residual normalization equal to the ratio of the observed quartz spectrum to the `fiberNorms_calib` spectrum (after applying screen responses and other corrections).
- **reduceExposure**:
  > It processes a visit through merging arms, producing `postISRCCD`, `pfsArm`, `lines`, `detectorMap`, `pfsMerged`, and `sky1d`. This can be used to process quartz exposures (or science exposures when flux calibration is not wanted).
- **calibrateExposure**:
  > It adds the flux calibration to `reduceExposure`, producing `pfsFluxReference`, `fluxCal` and `pfsCalibrated`. This can be used to process single science exposures. This is not demonstrated below, but its use is similar to that for `reduceExposure`.
- **science**:
  > It adds the spectral coaddition, producing `pfsCoadd`. This can be used to process multiple science exposures together.



## Define Collections

---

Because we need to be able to distinguish coadds formed from different combinations of visits, it’s necessary to define the inputs to the coaddition before running the `science` pipeline.

This is not required for the `reduceExposure` or `calibrateExposure` pipelines, but defining the inputs can provide a convenient way to reference them.

### Combination for Science Data

For the science data (e.g., `OBJECT` data), the combination can be defined as

```bash
# Define by data type:
defineCombination.py $DATASTORE PFS object --where "visit.target_name = 'OBJECT'"

# Define by specifying the observation dates:
defineCombination.py $DATASTORE PFS run20241025 --where "visit.day_obs = 20241025"
```

A combination can be defined with a `--where` option, which takes the same query string syntax as the `-d` option of `pipetask run`.

Alternatively, a combination can be defined by simply listing the exposure identifiers or specifying the observing dates:

```bash
# Define by listing visit identifiers
defineCombination.py $DATASTORE PFS someVisits 123 124 125
```

Although we have provided here some silly examples, it is recommended that descriptive names be used for the combination (e.g., `ssp-cosmos-deep-march2025` or `ssp-ga-2025-2028`). Note that these combination names are shared, so if the name is not of general interest to all users of your data repository, then it might be good to prefix it with your username (e.g., `foobar/playingAround-20250318`).



## Process the Data

---

Now we can run the pipeline to process a specific single exposure:

```bash
# Single Exposure
pipetask run \
--register-dataset-types -j $CORES -b $DATASTORE \
--instrument $INSTRUMENT \
-i PFS/defaults,"$RERUN"/calib \
-o "$RERUN"/reduceExposure \
-p '$DRP_STELLA_DIR/pipelines/reduceExposure.yaml' \
-d "visit = 123456"
```

Alternatively, you can run the science pipeline for an entire data collection:

```bash
# Science Pipeline
pipetask run \
--register-dataset-types -j $CORES -b $DATASTORE \
--instrument $INSTRUMENT \
-i PFS/defaults,"$RERUN"/calib \
-o "$RERUN"/science \
-p '$DRP_STELLA_DIR/pipelines/science.yaml' \
-d "combination = 'object'"
```

Notice that in the first case we’re running the `reduceExposure` pipeline on a selected exposure. The `science` pipeline is similar but on the `object` combinations that we defined earlier.

Note that we do not have to run the `reduceExposure` pipeline before we run the `science` pipeline (a single command is sufficient to run the entire pipeline): the `science` pipeline knows how to produce all the necessary intermediate datasets itself, and the above two commands are completely independent: they do not share any intermediate datasets.

However, we could have first run the `reduceExposure` pipeline and then fed its outputs into the `science` pipeline by including `$RERUN/reduceExposure` in the list of input collections for the `science` pipeline.

## Introduction to Reduction Steps

**NOTE: This section is work in progress.**

---

This section will include more detailed descriptions of each of the reduction steps in the `science` pipeline.

## Retrieve Data Products

---

There are some important differences in the data products produced by the Gen3 pipeline compared to the Gen2 pipeline. For the sake of efficiency (both in terms of processing time and reduced file numbers), the single-spectrum Gen2 products (`pfsSingle` and `pfsObject`) are written as multiple-spectrum Gen3 products per `cat_id` (`pfsCalibrated` and `pfsCoadd`). The equivalent of a `pfsObject` can be retrieved directly from the `pfsCoadd` dataset:

```python
from lsst.daf.butler import Butler
butler = Butler.from_config($DATASTORE, collection=["$RERUN/object"])
pfsObject = butler.get("pfsCoadd.single", cat_id=1, combination="object", parameters=dict(objId=55))
```

Note that the `objId` needs to be specified in the `parameters` dictionary, rather than as a separate argument to the `get` method, because it’s a parameter for the formatter that reads the dataset and not a dimension of the dataset itself.

!!! warning
        Refrain from retrieving `pfsCoadd.single` in a loop, as it is **EXTREMELY inefficient**.

!!! note
        In LSST version 26.0.2, the `butler` command was `butler = Butler($DATASTORE, collection=["$RERUN/object"])`, but in the later LSST versions, this is recommended to be `butler = Butler.from_config($DATASTORE, collection=["$RERUN/object"])`. Although the former expression may still work, `mypy` will deny this construction with reporting "class Butler is an abstract class. Abstract classes must not be instantiated". <br> **In the next section for data analysis, we will only use the latest construction.**