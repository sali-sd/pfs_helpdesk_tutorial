# (Optional) Build Calibration Frames

!!! Note
    Before running the science data processing, the pipeline requires calibration data. **The observatory provides calibration products from the PFS Science Platform (SP) for each run**, so users do not necessarily need to generate the calibration data themselves. The simplest approach is to use these pre-provided calibration products, in which case **the majority of this section can be skipped**.

## Importing Calibrations from PFS SP

---

Calibration data for each observing run is available from PFS SciencePlatform (SP) ([https://hscpfs.mtk.nao.ac.jp](https://hscpfs.mtk.nao.ac.jp)).

A calibration set is typically copied to SP a few weeks after a run, not during or immediately after it.
The calibrations are stored in the observatory filler directory, which is accessible to all users, for example:
`/shared/pfs/programs/S25A-000QF/2d/run21_June2025/calibs`. The exact directory name differs by run and semester.

For the S25B semester, the proposal ID will be `S25B-000QF`, and the run ID will be `run24_xxx`.
In practice, the directory name should be straightforward to identify.

You can copy the entire directory to your local disk. On the SP, see the getting-started document for instructions on copying files from SP.

You can then import the calibration data to a new data repository:

```bash
export NEW_DATASTORE='new_datastore'
butler create $NEW_DATASTORE --seed-config $OBS_PFS_DIR/gen3/butler.yaml --dimension-config $OBS_PFS_DIR/gen3/dimensions.yaml --override
butler register-instrument $NEW_DATASTORE lsst.obs.pfs.PrimeFocusSpectrograph
butler import --transfer copy --export-file path/to/calibs/export.yaml $NEW_DATASTORE calibs/
```

In addition to the calibrations, raw data and `pfsConfig` files must already have been ingested (see the [data ingestion page](02_02_run_ingestion.md)).

You are then ready to launch your own processing run.

## Building Calibrations Yourself

---

Assume the following default setup:

- The user is working in the public data repository `$WORKDIR/pfs/data/datastore` and using a publicly installed pipeline.
- The data repository has the `PFS/defaults` collection, which links to `PFS/raw/pfsConfig`, `PFS/raw/sps`, and `PFS/calib` (see the [data ingestion page](02_02_run_ingestion.md)).

Then the user can setup the following environment variables for conveniences and consistensy.

```bash
DATASTORE="$WORKDIR/pfs/data/datastore"
DATADIR="$WORKDIR/pfs/data"
CORES=16
INSTRUMENT="lsst.obs.pfs.PrimeFocusSpectrograph"
RERUN="u/$(whoami)"
BEGINDATE="2025-09-01T00:00:00"
ENDDATE="2025-10-10T23:59:59"                      # A time period that covers an observing run, e.g. RUN24
```

In this case, you may want to use a rerun directory based on your username so that multiple users do not interfere with one another.

Note that even if you complete all of the following steps, some calibrations, such as near-IR darks, may still be unavailable. Calibration is under active development and will continue to evolve. If you encounter issues caused by missing calibrations, please contact us.

## Build Bias

---

We begin by building the calibration products, starting with the bias frames:

```bash
pipetask run \
--register-dataset-types \                                # register the dataset types from the pipeline
-j $CORES \                                               # number of cores to use in parallel
-b $DATASTORE \                                           # datastore directory to use
--instrument $INSTRUMENT \                                # the instrument PFS
-i PFS/defaults \                                         # input collections (comma-separated)
-o "$RERUN"/calib/bias_gen \                              # output CHAINED collection
-p $DRP_STELLA_DIR/pipelines/bias.yaml \                  # pipeline configuration file to use
-d "instrument='PFS' AND visit.target_name = 'BIAS'" \    # or, for example: -d "visit IN (123456..123466)"
--fail-fast                                               # immediately stop the ingestion process if error
```

The `pipetask run` command is used to run a pipeline.   
A task is an operation within the pipeline, characterized by a set of dimensions that defines its parallelization level, together with a set of inputs and outputs. An instance of a task running on a single unit of data at that parallelization level is called a "quantum".

A pipeline is built from a "quantum graph", which tracks the inputs and outputs between tasks.

When you run a pipeline with `pipetask run`, it first builds the pipeline and reports the number of quanta that will be run for each task:

```bash
lsst.ctrl.mpexec.cmdLineFwk INFO: QuantumGraph contains 12 quanta for 2 tasks, graph ID: '1726845383.   6842682-77840''
Quanta     Tasks    
------ -------------
    10          isr
     2 cpBiasCombine
```

The bias pipeline contains only two tasks.

In this example, the pipeline operates on five exposures, each with `b` and `r` arms, so there are 10 `isr` quanta (instrument signature removal for each camera image) and 2 `cpBiasCombine` quanta (combining the bias frames for each camera).

An example of a more complex pipeline summary, for a full science run on 17 exposures, is shown later.

- The `-j` option specifies the number of cores to use in parallel.
- The `-b` option specifies the datastore to use.
- The `--instrument` option specifies the instrument. The correct value for PFS is `lsst.obs.pfs.PrimeFocusSpectrograph`.
- The `-i` option specifies the input collections as a comma-separated list. In this case, we are using the default collection that already links the raw data and the baseline calibrations. Additional collections will be added later as needed.
- The `-o` option specifies an output `CHAINED` collection. The pipeline writes output datasets to timestamped `RUN` collections, and these are chained together under the named output collection.
- The `-p` option specifies the pipeline configuration file to use. This is a `YAML` file in `drp_stella/pipelines` that defines the pipeline. A pipeline is composed of multiple tasks, each of which may operate on a different set of dimensions. The pipeline configuration can also define task-specific overrides, including alternative dataset names for task connections. An example of this appears later.
- The `-d` option specifies the data-selection query. The syntax is similar to an SQL `WHERE` clause, with some extensions. In this example, we select all visits from the PFS instrument with `visit.target_name = 'BIAS'`. In practice, a narrower selection is usually preferable, because this query may match visits from multiple nights and observing conditions. Strings must be enclosed in single quotes (`'`). Ranges can also be specified, for example `visit IN (12..34:5)`, which means all visits from 12 to 34 inclusive in steps of 5.
The `visit` dimension can be used directly to refer to the visit number, but a variety of related fields are also available, including:
  > - `visit.exposure_time`: exposure time in seconds
  > - `visit.observation_type`: type of observation (e.g., `BIAS`, `DARK`, `FLAT`, `ARC`)
  > - `visit.target_name`: target name
  > - `visit.science_program`: science program name
  > - `visit.tracking_ra`, `tracking_dec`: boresight position (ICRS)
  > - `visit.zenith_angle`: zenith angle in degrees
  > - `visit.lamps`: comma-separated list of lamps that were on
  > - Other dimensions can also be used, for example: `visit IN (12..34:5) AND arm = 'r' AND spectrograph = 3`.
- Configuration overrides can be specified with the `-c` option[1](#diff_gen2_c). For example, `-c isr:doCrosstalk=False` disables the crosstalk correction.
- The `--register-dataset-types` option registers the dataset types defined by the pipeline in the `butler` registry.

This only needs to be done once for each pipeline; it can be omitted in subsequent runs of the same pipeline.

Some additional options are useful for debugging:

- `--skip-existing-in <COLLECTION>`: Do not re-produce a dataset if it is already present in the specified collection.   
This is useful when you want to resume from where a previous run stopped.   
Usually, `<COLLECTION>` is the same as the output collection.
- `--clobber-outputs`: Overwrite any existing datasets for a task, usually logging or metadata by-products of running the task.
- `--pdb`: Drop into the Python debugger when an exception occurs.   
This does not work with parallel processing, so make sure you are not also using `-j`.

Used together, these three options are very effective when debugging Python exceptions in a pipeline run.

Once the pipeline has run and produced the bias frame, the calibration products must be certified:

```bash
butler certify-calibrations $DATASTORE "$RERUN"/calib/bias_gen "$RERUN"/calib/bias bias --begin-date $BEGINDATE --end-date $ENDDATE
```

This command tells the `butler` to certify the bias datasets in `"$RERUN"/calib/bias_gen` as calibration products in the `"$RERUN"/calib/bias` calibration collection.

The `--begin-date` and `--end-date` options specify the validity range of the calibration products.
In this example, the range is intended to cover a run such as run24, but the dates and times should be chosen carefully according to the instrument's calibration requirements.

To manage calibrations, you may sometimes need to certify or decertify individual datasets.
This capability is not available through the standard LSST command-line tools, but local scripts can be used for this purpose. Here are some examples based on Subaru data:

```bash
butlerDecertify.py $DATASTORE "$RERUN"/calib/bias dark --begin-date 2024-08-24T00:00:00 --id instrument=PFS arm=r spectrograph=2
butlerDecertify.py $DATASTORE "$RERUN"/calib/bias dark --begin-date 2024-05-01T00:00:00 --end-date 2024-08-23T23:59:59 --id instrument=PFS arm=r spectrograph=2
butlerCertify.py $DATASTORE "$RERUN"/calib/bias_gen "$RERUN"/calib/bias dark --begin-date 2024-05-01T00:00:00 --id instrument=PFS arm=r spectrograph=2
```

!!! warning
    Certifying a dataset as a calibration product tags it in the database as a calibration product and associates it with a validity timespan. It does not copy the dataset: the dataset is still a part of the `$RERUN/bias/<timestamp> RUN` collection, and removing that collection will remove the calibration dataset from the datastore.

However, that `RUN` collection also contains many intermediate datasets that consume unnecessary space, in particular the `biasProc` datasets, which are produced by the `isr` task in the bias pipeline. These can be removed with the following command:

```bash
butlerCleanRun.py $DATASTORE $RERUN/bias_gen/* biasProc
```

This leaves each `$RERUN/bias_gen/<timestamp>` collection containing only the bias dataset and a small amount of metadata. Note that the `pipetask` command specifies an output collection of `$RERUN/bias_gen`, while `butlerCleanRun.py` is run on `$RERUN/bias_gen/*`; this prunes all timestamped `RUN` collections contained in the `$RERUN/bias_gen` `CHAINED` collection.

You can also use the `butler remove-runs` command to completely remove `RUN` collections and `butler remove-collections` to remove `CHAINED` collections.

Finally, you may want to create a collection, `"$RERUN"/calib`, to hold the bias and all other calibrations created in this tutorial:

```bash
butler collection-chain $DATASTORE "$RERUN"/calib "$RERUN"/calib/bias
```



## Build Dark

---

Once the bias calibration product has been built and certified, you can move on to the darks, which follow the same pattern:

First run the builder:

```bash
pipetask run \
--register-dataset-types -j $CORES -b $DATASTORE \
--instrument $INSTRUMENT \
-i PFS/defaults,"$RERUN"/calib \
-o "$RERUN"/calib/dark_gen \
-p $DRP_STELLA_DIR/pipelines/dark.yaml \
-d "instrument='PFS' AND visit.target_name = 'DARK'" \
--fail-fast 
```

Then certify the products, clean up unneeded files, and prepend the result to the `"$RERUN"/calib` collection:

```bash
butler certify-calibrations $DATASTORE "$RERUN"/calib/dark_gen "$RERUN"/calib/dark dark --begin-date $BEGINDATE --end-date $ENDDATE
butlerCleanRun.py $DATASTORE "$RERUN"/calib/dark_gen/* darkProc
butler collection-chain $DATASTORE "$RERUN"/calib --mode=prepend "$RERUN"/calib/dark
```



## Build Flat

---

Building flats follows the same pattern.

First run the builder:

```bash
pipetask run \
--register-dataset-types -j $CORES -b $DATASTORE \
--instrument $INSTRUMENT \
-i PFS/defaults,"$RERUN"/calib \
-o "$RERUN"/calib/flat_gen \
-p $DRP_STELLA_DIR/pipelines/flat.yaml \
-d "instrument='PFS' AND visit.target_name = 'FLAT'" \
--fail-fast 
```

Then certify the products:

```bash
butler certify-calibrations $DATASTORE "$RERUN"/calib/flat_gen "$RERUN"/calib/flat flat --begin-date $BEGINDATE --end-date $ENDDATE
butlerCleanRun.py $DATASTORE "$RERUN"/calib/flat_gen/* flatProc
butler collection-chain $DATASTORE "$RERUN"/calib --mode=prepend "$RERUN"/calib/flat
```



## Build Detector Map

---

A detector map (`detectorMap`) maps the fiber trace and wavelength solution to `(x, y)` positions on the detector. It is derived from quartz and arc-lamp data. Once the bias, dark, and flat frames have been prepared, the next step is to determine the detector map.

The first step is to bootstrap a `detectorMap` from an arc exposure and a quartz exposure.
This is an advanced operation, because it requires inspecting images to estimate the offsets between the baseline optical model and the observed data. In general, most users should not need to do this, because the Subaru Observatory and the SSP team will provide suitable detector maps.

```bash
pipetask run \
--register-dataset-types -j $CORES -b $DATASTORE \
--instrument $INSTRUMENT \
-i PFS/defaults,"$RERUN"/calib \
-o "$RERUN"/calib/bootstrap_gen \
-p $DRP_STELLA_DIR/pipelines/bootstrap.yaml \
-d "instrument='PFS' AND exposure IN (11,22)" \
--fail-fast \
-c isr:doCrosstalk=False \
-c bootstrap:profiles.profileRadius=2 \
-c bootstrap:profiles.profileSwath=2500 \
-c bootstrap:profiles.profileOversample=3 \
-c bootstrap:spatialOrder=2 \
-c bootstrap:spectralOrder=2 \
-c bootstrap:spatialOffset=-10 \
-c bootstrap:spectralOffset=0 \
-c bootstrap:findLines.threshold=30.0
```

Then certify the products:

```bash
butler certify-calibrations $DATASTORE "$RERUN"/calib/bootstrap_gen "$RERUN"/calib/bootstrap detectorMap_bootstrap --begin-date $BEGINDATE --end-date $ENDDATE
butlerCleanRun.py $DATASTORE $RERUN/calib/bootstrap/* postISRCCD
butler collection-chain $DATASTORE "$RERUN"/calib --mode=prepend "$RERUN"/calib/bootstrap
```

Here, the pipeline requires the `PFS/raw/pfsConfig` collection, which is already included in `PFS/defaults`, because the `PfsConfig` files are needed to determine which fibers are illuminated. Note that the arc and quartz exposures are both specified within the same `-d` option.

The Gen3 middleware does not support multiple `-d` options for specifying them independently, but the task can distinguish them using the `lamps` field in the exposure.

The bootstrap pipeline writes a `detectorMap_bootstrap` dataset for each camera. In practice, it is often necessary to run the bootstrap pipeline separately for each camera, because the `spatialOffset`, `spectralOffset`, and `findLines.threshold` parameters may differ between cameras. Appropriate offsets should be determined by inspecting the images.

Once you have a rough detector map, you can refine it to produce the final detector map:

```bash
pipetask run \
--register-dataset-types -j $CORES -b $DATASTORE \
--instrument $INSTRUMENT \
-i PFS/defaults,"$RERUN"/calib \
-o "$RERUN"/calib/detectorMap_gen \
-p $DRP_STELLA_DIR/pipelines/detectorMap.yaml \
-d "instrument='PFS' AND visit.target_name IN ('ARC', 'FLAT')" \
-c measureCentroids:connections.calibDetectorMap=detectorMap_bootstrap \
-c fitDetectorMap:fitDetectorMap.doSlitOffsets=True \
-c fitDetectorMap:fitDetectorMap.order=4 \
-c fitDetectorMap:fitDetectorMap.soften=0.03 \
--fail-fast
```

Quartz (`FLAT`) exposures provide useful constraints on the detector map in addition to the arc-lamp (`ARC`) exposures.

Here, two pipeline connections have been modified. The `measureCentroids` task’s `calibDetectorMap` input provides the positions used to measure the centroids of arc lines. Normally, this would be set to the calibration detector map (`detectorMap_calib`), but that does not yet exist at this stage. Instead, it is configured to use the bootstrap detector map (`detectorMap_bootstrap`).

Similarly, the `fitDetectorMap` task’s `slitOffsets` input is configured to use the slit offsets from the bootstrap detector map.

The detector-map pipeline writes a `detectorMap_candidate` dataset for each camera.

The certification step is slightly different from the previous stages:

```bash
certifyDetectorMaps.py INTEGRATION "$RERUN"/calib/detectorMap_gen "$RERUN"/calib/detectorMap --instrument PFS --begin-date $BEGINDATE --end-date $ENDDATE
butlerCleanRun.py $DATASTORE "$RERUN"/calib/detectorMap_gen/* postISRCCD
butler collection-chain $DATASTORE "$RERUN"/calib --mode=prepend "$RERUN"/calib/detectorMap
```

The `certifyDetectorMaps.py` script is used to certify the detector-map datasets instead of the standard `butler certify-calibrations` command. This script copies `detectorMap_candidate` to `detectorMap_calib` and certifies it.

## Build Fiber Profile

---

The fiber profile (`fiberProfiles`) describes the spatial profile of each fiber. Every fourth fiber is illuminated while the others are masked by "dots", and the profiles are then measured using a dedicated quartz dataset.

The `fitFiberProfiles` pipeline fits profiles to multiple exposures simultaneously. It is the preferred method for building fiber profiles because it allows the profile to be measured to large distances from the fiber center.

The procedure is as follows:

```bash
# Create a `profiles_run` dimension value and associate the exposures with it for the `b`, `r`, and `n` arms
defineFiberProfilesInputs.py $DATASTORE PFS run24 --update \
--bright 130192..130198 --dark 130184..130190 \
--bright 130787..130793 --dark 130779..130785 \
--bright 130943..130949 --dark 130935..130941 \
--bright 131090..131096 --dark 131082..131088

# Run `fitFiberProfiles`
pipetask run \
--register-dataset-types -j $CORES -b $DATASTORE \
--instrument $INSTRUMENT \
-i PFS/defaults,PFS/fiberProfilesInputs,"$RERUN"/calib \
-o "$RERUN"/calib/fitFiberProfiles \
-p $DRP_STELLA_DIR/pipelines/fitFiberProfiles.yaml \
-d "profiles_run = 'run24' AND arm IN ('b', 'r', 'n')" \
-c fitProfiles:profiles.profileRadius=10 \
-c fitProfiles:profiles.profileOversample=3 \
-c fitProfiles:profiles.profileSwath=500 \
--fail-fast

# Certify the `fiberProfiles` product
butler certify-calibrations $DATASTORE "$RERUN"/calib/fitFiberProfiles "$RERUN"/calib/calibfiberProfiles --begin-date $BEGINDATE --end-date $ENDDATE
butlerCleanRun.py $DATASTORE "$RERUN"/calib/fitFiberProfiles/* postISRCCD
butler collection-chain $DATASTORE "$RERUN"/calib --mode=prepend "$RERUN"/calib/calibfiberProfiles
```

Because it involves multiple groups of exposures, the `fitFiberProfiles` pipeline requires the inputs to be defined in advance. The `defineFiberProfilesInputs.py` script is used to register the different exposure groups.

When working with real data, there are typically four groups of exposures, and each group contains both "bright" exposures, in which selected fibers are deliberately illuminated, and "dark" exposures, in which all fibers are hidden.

A dataset describing the exposure roles is written to the `PFS/fiberProfilesInputs` collection, so this collection must be included in the inputs to the `fitFiberProfiles` pipeline.

The `profiles_run` value can then be used in the data-selection query, because it links all required exposures.



## Build Fiber Norm

---

The fiber norm (`fiberNorms`) is the relative spectral normalization of each fiber, measured from quartz exposures:

```bash
pipetask run \
--register-dataset-types -j $CORES -b $DATASTORE \
--instrument $INSTRUMENT \
-i PFS/defaults,"$RERUN"/calib \
-o "$RERUN"/calib/fiberNorms_gen \
-p $DRP_STELLA_DIR/pipelines/fiberNorms.yaml \
-d "instrument='PFS' AND visit.target_name = 'FLAT' AND dither = 0.0" \
--fail-fast

# Certify the `fiberNorms` product
butler certify-calibrations $DATASTORE "$RERUN"/calib/fiberNorms_gen "$RERUN"/calib/fiberNorms fiberNorms_calib --begin-date $BEGINDATE --end-date $ENDDATE
butlerCleanRun.py $DATASTORE "$RERUN"/calib/fiberNorms_gen/* postISRCCD
butler collection-chain $DATASTORE "$RERUN"/calib --mode=prepend "$RERUN"/calib/fiberNorms
```

The `fiberNorms` pipeline combines the extracted spectra from multiple quartz exposures and writes the output as `fiberNorms_calib`.