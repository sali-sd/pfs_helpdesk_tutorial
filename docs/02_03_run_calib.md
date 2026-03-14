# (Optional) Build Calibration Frames

!!! Note
    Before running the science data processing, the pipeline requires calibration data. **The observatory provides calibration products from the PFS Science Platform (SP) for each run**, so users do not necessarily need to generate the calibration data themselves. The simplest approach is to use these pre-provided calibration products, in which case **the majority of this section can be skipped**.

## Importing Calibs from PFS SP

There is a set of calibration data available for each observing run from PFS SP (<https://hscpfs.mtk.nao.ac.jp>).

A calib set is copied to the SP typically a few weeks after a run (i.e., not during or right after a run).
The calibs are stored under the observatory filler directory, which everyone has access to, e.g.,
`/shared/pfs/programs/S25A-000QF/2d/run21_June2025/calibs`. The exact name differ for each run and semester.

For S25B semester, the proposal ID will be `S25B-000QF`, and the run ID will be `run24_xxx`.
The directory name should be obvious in any case.

You can copy the entire directory to your disk (see the SP getting-started document for how to copy files from SP).

You can then import the calibration data:

```bash
export NEW_DATASTORE='new_datastore'
butler create $NEW_DATASTORE --seed-config $OBS_PFS_DIR/gen3/butler.yaml --dimension-config $OBS_PFS_DIR/gen3/dimensions.yaml --override
butler register-instrument $NEW_DATA_STORE lsst.obs.pfs.PrimeFocusSpectrograph
butler import --transfer copy --export-file path/to/calibs/export.yaml $NEW_DATA_STORE calibs/
```

In addition to the calibs, you will also need `pfsConfig` files made for your program. These custom `pfsConfig` files are available under your program directory, e.g., `/shared/pfs/programs/S25A-000QF/2d/customPfsConfig`. Copy these files to yoru disk and then ingest them (see the [data ingestion page](02_02_run_ingestion.md)). Now, you are ready to launch your own processing run.

---

## Building Calibs by Yourself

First, let's assume the following default setup: the user is working in the public directory `$WORKDIR/pfs/` and using a publicly installed pipeline.

```bash
DATASTORE="$WORKDIR/pfs/data/datastore"
DATADIR="$WORKDIR/pfs/data"
CORES=16
INSTRUMENT="lsst.obs.pfs.PrimeFocusSpectrograph"
RERUN="u/$(whoami)"
```

In this case, you may want to set up the rerun directory specified by your username so that multiple users won't mix things up.

Note that even if you go over all of the following processes, there may still be missing calibrations such as near-IR darks. Active development work is under way, we expect the calibrations will evolve rapidly. If you encounter any issues due to missing calibs, please contact us.

## Build Bias

---

Next, we’ll build the calibration products, starting from the bias frames:

``` bash
pipetask run \
--register-dataset-types \                                # register the dataset types from the pipeline
-j $CORES \                                               # number of cores to use in parallel
-b $DATASTORE \                                           # datastore directory to use
--instrument $INSTRUMENT \                                # the instrument PFS
-i PFS/raw/sps,PFS/calib \                                # input collections (comma-separated)
-o "$RERUN"/bias \                                        # output CHAINED collection
-p $DRP_STELLA_DIR/pipelines/bias.yaml \                  # pipeline configuration file to use
-d "instrument='PFS' AND visit.target_name = 'BIAS'" \ # or, for example: -d "visit IN (123456..123466)" \
--fail-fast                                               # immediately stop the ingestion process if error
```

The `pipetask run` command is used to run a pipeline. \
A task is an operation within the pipeline, characterized by a set of dimensions that define the level at which it parallelizes, and a set of inputs and outputs. An instance of a task running on a single set of data at its parallelization level is called a "quantum".

A pipeline is built from the "quantum graph", which tracks the inputs and outputs between various tasks.

When you run a pipeline with `pipetask run`, it first builds the pipeline and reports the number of quanta that will be run for each task:

```bash
lsst.ctrl.mpexec.cmdLineFwk INFO: QuantumGraph contains 12 quanta for 2 tasks, graph ID: '1726845383.   6842682-77840''
Quanta     Tasks    
------ -------------
    10          isr
     2 cpBiasCombine
```

The bias pipeline has only two tasks.

In this case, they are operating on 5 exposures, each with `b` and `r` arms, so there are 10 `isr` quanta (instrument signature removal from each camera image) and 2 `cpBiasCombine` quanta (combining the bias frames from each of the cameras).

The summary for a more complicated pipeline (running the full science pipeline on 17 exposures) is shown later.

- `-j` option specifies the number of cores to use in parallel.

- `-b` option specifies the datastore to use.

- `--instrument` option specifies the instrument. The proper specification for PFS is `lsst.obs.pfs.PrimeFocusSpectrograph`

- `-i` option specifies the input collections (comma-separated). In this case, we are using the raw data and the calibration data (for the defects). Later we’ll add other collections as we need them.

- `-o` option specifies an output `CHAINED` collection. The pipeline will write the output datasets to a `RUN` collection named after this, with a timestamp appended (e.g., `$RERUN/bias/20240918T181715Z`), all chained together in the nominated output collection.

- `-p` option specifies the pipeline configuration file to use. This is a `YAML` file in `drp_stella/pipelines` that describes the pipeline to run. A pipeline is composed of multiple tasks, each operating on a (potentially different) set of dimensions. The pipeline configuration can also specify configuration overrides for each task, including different dataset names to use as connections between the tasks (useful for providing slightly different versions of the same dataset; there’ll be an example of this later).

- `-d` option specifies the data selection query. The query syntax is similar to the `WHERE` clause in SQL, with some extensions. In this case, we are selecting all the visits that have a target name of BIAS and are from the PFS instrument; this is not generally recommended in the usual case, since it would encompass visits taken on multiple nights and different conditions, rather than selecting visits from, say, the beginning of a single night. Strings must be quoted with single quotes (`'`). Ranges can be specified, like `visit IN (12..34:5)`, which means all visits from 12 to 34 (inclusive) in steps of 5.
The `visit` dimension can be used directly to mean the visit number, but also has a variety of additional fields that can be used, including:
  > - `visit.exposure_time`: exposure time in seconds
  > - `visit.observation_type`: type of observation (e.g., `BIAS`, `DARK`, `FLAT`, `ARC`)
  > - `visit.target_name`: target name
  > - `visit.science_program`: science program name
  > - `visit.tracking_ra`, `tracking_dec`: boresight position (ICRS)
  > - `visit.zenith_angle`: zenith angle in degrees
  > - `visit.lamps`: comma-separated list of lamps that were on
  > - Other dimensions can also be used, for example: `visit IN (12..34:5) AND arm = 'r' AND spectrograph = 3`.

- Configuration overrides can be specified with the `-c` option<sup>[1](#diff_gen2_c)</sup>. For example, `-c isr:doCrosstalk=False` turns off the crosstalk correction.

- `--register-dataset-types` option is used to register the dataset types from the pipeline in the `butler` registry.

It is only necessary to run this once for each pipeline, and then it can be dropped for future runs of the same pipeline.

Some additional helpful options when debugging are:

- `--skip-existing-in <COLLECTION>`: don’t re-produce a dataset if it’s present in the specified collection. \
This is helpful when you want to pick up from where a previous run stopped. \
Usually the `<COLLECTION>` specified here is the same as the output collection.

- `--clobber-outputs`: clobber any existing datasets for a task (usually logging or metadata by-products of running the task).

- `--pdb`: drop into the python debugger on an exception. \
This won’t work with parallel processing, so check that you’re not also using `-j`.

The above three options (used together) are very useful when debugging a python exception in a pipeline run.

Once the pipeline has run and produced the bias frame, we need to certify the calibration products:

```bash
butler certify-calibrations $DATASTORE "$RERUN"/bias PFS/calib bias --begin-date 2000-01-01T00:00:00 --end-date 2050-12-31T23:59:59
```

This command tells the `butler` to certify the bias datasets in the `$RERUN/bias` collection as calibration products in the `PFS/calib` calib collection.

The `--begin-date` and `--end-date` options specify the validity range of the calibration products.
In the above example, we're specifying a very broad range as an example, but the dates and times should be chosen carefully according to the calibration needs of the instrument.

To manage calibrations, it may be necessary to certify and decertify individual datasets.
This capability is not available with LSST’s command-line tools, but we have some scripts that can do this. Here are some examples from working on Subaru data:

```bash
butlerDecertify.py /work/datastore PFS/calib dark --begin-date 2024-08-24T00:00:00 --id instrument=PFS arm=r spectrograph=2
butlerDecertify.py /work/datastore PFS/calib dark --begin-date 2024-05-01T00:00:00 --end-date 2024-08-23T23:59:59 --id instrument=PFS arm=r spectrograph=2
butlerCertify.py /work/datastore price/pipe2d-1036/dark/run16 PFS/calib dark --begin-date 2024-05-01T00:00:00 --id instrument=PFS arm=r spectrograph=2
```

---

!!! warning
    Certifying a dataset as a calibration product tags it in the database as a calibration product and associates it with a validity timespan. It does not copy the dataset: the dataset is still a part of the `$RERUN/bias/<timestamp> RUN` collection, and removing that collection will remove the calibration dataset from the datastore.

---

However, that RUN collection also contains a bunch of intermediate datasets which are unnecessarily consuming space, in particular the `biasProc` datasets (which are the outputs of running the isr task in the bias pipeline). We can remove these with the following command:

```bash
butlerCleanRun.py $DATASTORE $RERUN/bias/* biasProc
```

This will leave the `$RERUN/bias/<timestamp>` collection containing only the bias dataset and some other small metadata datasets. Note that our pipetask command specifies an output collection of `$RERUN/bias`, but we're specifying `$RERUN/bias/*` for the `butlerCleanRun.py` command, which will delete all the timestamped `RUN` collections in the `$RERUN/bias CHAINED` collection.

You can also use the `butler remove-runs` command to completely remove `RUN` collections and `butler remove-collections` to remove `CHAINED` collections.

## Build Dark

---

With the bias calibration product built and certified, we can move on to the dark, which follow the same pattern:

First run the builder:

```bash
pipetask run \
--register-dataset-types -j $CORES -b $DATASTORE \
--instrument $INSTRUMENT \
-i PFS/raw/all,PFS/calib \
-o "$RERUN"/dark \
-p $DRP_STELLA_DIR/pipelines/dark.yaml \
-d "instrument='PFS' AND visit.target_name = 'DARK'" \
--fail-fast 
```

Then, certify the products:

```bash
butler certify-calibrations $DATASTORE "$RERUN"/dark PFS/calib dark --begin-date 2000-01-01T00:00:00 --end-date 2050-12-31T23:59:59
butlerCleanRun.py $DATASTORE $RERUN/dark/* darkProc
```

## Build Flat

---

Building Flats follows the same pattern.

First run the builder:

```bash
pipetask run \
--register-dataset-types -j $CORES -b $DATASTORE \
--instrument $INSTRUMENT \
-i PFS/raw/all,PFS/calib \
-o "$RERUN"/flat \
-p $DRP_STELLA_DIR/pipelines/flat.yaml \
-d "instrument='PFS' AND visit.target_name = 'FLAT'" \
--fail-fast 
```

Then, certify the products:

```bash
butler certify-calibrations $DATASTORE "$RERUN"/flat PFS/calib flat --begin-date 2000-01-01T00:00:00 --end-date 2050-12-31T23:59:59
butlerCleanRun.py $DATASTORE $RERUN/flat/* flatProc
```

## Build Detector Map

---

A detector map (`detectorMap`) is the mapping of fiber trace and wavelength to (x, y) position on the detector, which is generated by using quartz and arc lamp dataset. The bias, dark, and flat frames characterize the detector, so now it’s time to determine the detector map.

We first bootstrap a `detectorMap` from an arc and quartz.
This is somewhat of a black-belt operation, because it requires looking at images to determine approximate offsets between the base optical model and reality. In general, it should not be necessary for general users to have to do this, as the Subaru Observatory and the SSP team will provide suitable detectorMaps.

```bash
pipetask run \
--register-dataset-types -j $CORES -b $DATASTORE \
--instrument $INSTRUMENT \
-i PFS/raw/all,PFS/raw/pfsConfig,PFS/calib 
-o "$RERUN"/bootstrap \
-p $DRP_STELLA_DIR/pipelines/bootstrap.yaml' \
-d "instrument='PFS' AND exposure IN (11,22)" \
--fail-fast \
-c isr:doCrosstalk=False \
-c bootstrap:profiles.profileRadius=2 \
-c bootstrap:profiles.profileSwath=2500 \
-c bootstrap:profiles.profileOversample=3 \
-c bootstrap:spectralOffset=-10
```

Then, certify the products:

```bash
butler certify-calibrations $DATASTORE "$RERUN"/bootstrap PFS/bootstrap detectorMap_bootstrap --begin-date 2000-01-01T00:00:00 --end-date 2050-12-31T23:59:59
butlerCleanRun.py $DATASTORE $RERUN/bootstrap/* postISRCCD
```

Here, we have added the `PFS/raw/pfsConfig` collection to the input since we need the `PfsConfig` files to determine which fibers are illuminated. Note that the arc and quartz are both specified as inputs in the same `-d` option.

The Gen3 middleware does not support multiple `-d` options to specify them independently, but the task can determine which is which from the `lamps` field in the exposure.

The bootstrap pipeline writes a `detectorMap_bootstrap` dataset for each camera, and we’re certifying that in the `PFS/bootstrap` collection (so it’s independent of the best-quality detectorMaps we’ll certify in `PFS/calibs`).

When working with the data, it will probably be necessary to run the bootstrap pipeline on each camera separately, so that different `-c bootstrap:spectralOffset=<WHATEVER>` values can be used for each camera.
The suitable offsets should be determined by looking at the images.

Now we have a rough detectorMap, we can refine it and create the proper detectorMap:

```bash
pipetask run \
--register-dataset-types -j $CORES -b $DATASTORE \
--instrument $INSTRUMENT \
-i PFS/raw/all,PFS/raw/pfsConfig,PFS/bootstrap,PFS/calib \
-o "$RERUN"/detectorMap \
-p '$DRP_STELLA_DIR/pipelines/detectorMap.yaml' \
-d "instrument='PFS' AND visit.target_name IN ('ARC', 'FLAT')" \
-c measureCentroids:connections.calibDetectorMap=detectorMap_bootstrap \
-c fitDetectorMap:fitDetectorMap.doSlitOffsets=True \
-c fitDetectorMap:fitDetectorMap.order=4 \
-c fitDetectorMap:fitDetectorMap.soften=0.03 \
--fail-fast
```

Note that quartz (`FLAT`) exposures provide useful information for constraining the detectorMap, in addition to the arc lamp (`ARC`) exposures.

Then, certify the products:

```bash
certifyDetectorMaps.py INTEGRATION $RERUN/detectorMap PFS/calib --instrument PFS --begin-date 2000-01-01T00:00:00 --end-date 2050-12-31T23:59:59
butlerCleanRun.py $DATASTORE $RERUN/detectorMap/* postISRCCD
```

Here, we have modified two connections in the pipeline. The `measureCentroids` task’s `calibDetectorMap` input is a detectorMap that provides the position at which to measure the centroids of the arc lines.

Usually this is set to the calibration detectorMap (detectorMap_calib), but we don’t have one of those yet.

Instead, we will configure this to use the bootstrap detectorMap (`detectorMap_bootstrap`) instead; notice also that we’re including the `PFS/ boostrap` collection in the input.

Similarly, the `fitDetectorMap` task’s `slitOffsets` input is set to use the slit offsets from the bootstrap detectorMap.

The detectorMap pipeline writes a `detectorMap_candidate` dataset for each camera.

The `certifyDetectorMaps.py` script is used to certify the detectorMap datasets instead of the usual `butler certify-calibrations` command.

This script copies the `detectorMap_candidate` as a `detectorMap_calib` and certifies it.

## Build Fiber Profile

---

The fiber profile (`fiberProfiles`) is the profile of fibers along the spatial direction. We illuminate every four fibers and hide the rest behind “dots”, and then measure the profiles of fibers using a dedicated quartz dataset.

The `fitFiberProfiles` pipeline fits a profile to multiple exposures simultaneously, and is the preferred pipeline to use for building fiber profiles because it allows measuring the profile out to large distance from the fiber center.

Here’s how you run them:

```bash
# Creates a profiles_run dimension value and associates those exposures with it.
defineFiberProfilesInputs.py $DATASTORE PFS run18_brn \
--bright 113855..113863 --dark 113845..113853 \
--bright 113903..113911 --dark 113893..113901 \
--bright 114190..114198 --dark 114180..114188 \
--bright 114238..114246 --dark 114228..114236

# fitFiberProfiles:
pipetask run \
--register-dataset-types -j $CORES -b $DATASTORE \
--instrument $INSTRUMENT \
-i PFS/raw/all,PFS/fiberProfilesInputs,PFS/raw/pfsConfig,PFS/calib \
-o "$RERUN"/fitFiberProfiles \
-p '$DRP_STELLA_DIR/pipelines/fitFiberProfiles.yaml \
-d "profiles_run = 'run18_brn'" \
-c fitProfiles:profiles.profileRadius=10 \
-c fitProfiles:profiles.profileOversample=3 \
-c fitProfiles:profiles.profileSwath=500 \
--fail-fast

# certify the fiberProfile product
butler certify-calibrations $DATASTORE "$RERUN"/fitFiberProfiles PFS/calibfiberProfiles --begin-date 2000-01-01T00:00:00 --end-date 2050-12-31T23:59:59
butlerCleanRun.py $DATASTORE $RERUN/fitFiberProfiles/* postISRCCD
```

Because it involves multiple groups of exposures, the `fitFiberProfiles` pipeline requires defining the inputs to the pipeline ahead of time.
The `defineFiberProfilesInputs.py` script is used to define the inputs for the different groups of exposures.

When working on real data, we typically have four groups of several exposures each, and each group contains “bright” (select fibers deliberately exposed) and “dark” (all fibers hidden) exposures.

A file describing the roles of the exposures is written in the`<instrument>/fiberProfilesInputs` collection, so this must be included in the inputs for the `fitFiberProfiles` pipeline.

We can use the `profiles_run` value in the data selection query, as that is linked to all the required exposures.

## Build Fiber Norm

---

The Fiber Norm (`fiberNorms`) is the spectral normalization of each fiber, measured from a quartz:

```bash
pipetask run \
--register-dataset-types -j $CORES -b $DATASTORE \
--instrument $INSTRUMENT \
-i PFS/raw/all,PFS/raw/pfsConfig,PFS/calib \
-o "$RERUN"/fiberNorms \
-p '$DRP_STELLA_DIR/pipelines/fiberNorms.yaml' \
-d "instrument='PFS' AND visit.target_name = 'FLAT' AND dither = 0.0" \
--fail-fast

# certify the fiberNorm product
butler certify-calibrations $DATASTORE "$RERUN"/fiberNorms PFS/calib fiberNorms_calib --begin-date 2000-01-01T00:00:00 --end-date 2050-12-31T23:59:59
butlerCleanRun.py $DATASTORE $RERUN/fiberNorms/* postISRCCD
```

The `fiberNorms` pipeline combines the extracted spectra from multiple quartz exposures, and writes the output as
`fiberNorms_calib`.
