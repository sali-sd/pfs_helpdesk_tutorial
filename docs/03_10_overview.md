# Overview of PFS Data Products

This section describes the main PFS data products produced by the 2D DRP pipeline. They are all stored as FITS files and follow a strict naming convention based on observation identifiers.

We will show how PFS data products are stored, can be accessed and analyzed using `Butler`. Data on the [PFS Science Platform](https://hscpfs.mtk.nao.ac.jp/portal/) will be used as reference, specifically data products from proposal ID `S25A-000QF`, which is part of the **Observatory Filler Program** and available to everyone who signs up to the Science Platform. The method of accessing and analyzing PFS data products using `Butler` is universally applicable to all 2D DRP pipeline reduced data.

As a reference, the following are all the pipeline data products:

```
apCorr                 cosmicray_config    fitFluxCal_log             fluxCal         lam1d_modified_updated  packages          pfsCoadd          pfsMergedLsf
calibs                 cosmicray_log       fitFluxCal_metadata        isr_config      mergeArms_config        pfsArm            pfsCoaddLsf       reduceExposure_config
coaddSpectra_config    cosmicray_metadata  fitFluxReference_config    isr_log         mergeArms_log           pfsArmLsf         pfsConfig         reduceExposure_log
coaddSpectra_log       detectorMap         fitFluxReference_log       isr_metadata    mergeArms_metadata      pfsCalibrated     pfsFluxReference  reduceExposure_metadata
coaddSpectra_metadata  fitFluxCal_config   fitFluxReference_metadata  lam1d_modified  objectGroupMap          pfsCalibratedLsf  pfsMerged         sky1d
```

Most of these files are not of much significance to the user as they are intermediate pipeline and QA products. The relevant PFS data products and their properties for the science user will be highlighted going forward, but for a detailed description please refer to the [PFS Data Model documentation](https://github.com/Subaru-PFS/datamodel/blob/master/datamodel.txt).

In this section we will provide explanations and code for quick analysis of PFS data products out of the box, but the user is also encouraged to follow the [PFS Science Platform Getting-Started Notebook](https://hscpfs.mtk.nao.ac.jp/portal/) — a Jupyter Notebook that provides a step-by-step guide and a granular understanding of each data product.