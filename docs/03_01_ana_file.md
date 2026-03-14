# File Access

After running the PFS 2D DRP, data reduction are performed and the spectrum products are constructed.

## The Location of Data Products

---

!!! note
    While you can access files written to a datastore configured on a regular filesystem, it is recommended to use the data `butler`. The contents of the `datastore`, including filenames and locations, are an implementation detail of the data `butler`, and subject to change without notice.


First, where can we find the product files? 
In this assumed working directory and user rerun, the output files are located under `$WORKDIR/pfs/data/datastore/u/$(whoami)/object/`. 

You can check by:

```
ls $WORKDIR/pfs/data/datastore/u/$(whoami)/object/
```

You may find a folder named by date and time, e.g., `20250218T070224Z`. This is one of the reruns for your `object` collection. 
If you run the processing multiple times, different folders with specific timestamps will be created.

Let's inspect the contents of  `20250218T070224Z/`:

```
$ ls 20250218T070224Z

apCorr                 cosmicray2_metadata         fitPfsFluxReference_metadata  mergeArms_log       pfsCoadd               reduceExposure_log
calexp                 detectorMap                 fluxCal                       mergeArms_metadata  pfsCoaddLsf            reduceExposure_metadata
coaddSpectra_config    fitFluxCal_config           isr_config                    packages            pfsFluxReference       sky1d
coaddSpectra_log       fitFluxCal_log              isr_log                       pfsArm              pfsMerged
coaddSpectra_metadata  fitFluxCal_metadata         isr_metadata                  pfsArmLsf           pfsMergedLsf
cosmicray2_config      fitPfsFluxReference_config  lines                         pfsCalibrated       postISRCCD
cosmicray2_log         fitPfsFluxReference_log     mergeArms_config              pfsCalibratedLsf    reduceExposure_config
```

You will see a bunch of directories. Refer to the release document as well as to the [datamodel](https://github.com/Subaru-PFS/datamodel/blob/master/datamodel.txt) for details.
Here is a brief summary of some of the most important files: `pfsArm` contains 1D-extracted, wavelength-calibrated spectra for each arm (`b`, `r`, `n`, `m`) separately. Here, `b`=blue, `r`=red, `n`=nearIR, and `m`=medium resolution red-arm. The arms are combined in a `pfsMerged` file. Note that the sky subtraction has been performed in `pfsMerged`. Then the pipeline applies the flux calibration and `pfsCalibrated` is a fully calibrated 1d spectrum for a visit. Finally, `pfsCoadd` is a coadd spectrum from multiple visits.
