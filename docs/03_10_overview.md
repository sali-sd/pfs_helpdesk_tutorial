# Overview of PFS Data Products

This section describes the main PFS spectroscopic data products produced by the 2D DRP pipeline. They are all stored as FITS files and follow a strict naming convention based on observation identifiers.

We will show how PFS data products are stored, can be accessed and analyzed using **Butler**. Data on the [PFS Science Platform](https://hscpfs.mtk.nao.ac.jp/portal/) will be used as reference, specifically data products from proposal ID `S25A-000QF`, which is part of the **PFS Filler Program** and available to everyone that signs up to the Science Platform. The method of accessing and analyzing PFS data products using **Butler** is universally applicable to all 2D DRP pipeline reduced data.

As a reference, the following are all the pipeline data products:

```
apCorr                 fitFluxCal_log             mergeArms_config    pfsCoaddLsf
calibs                 fitFluxCal_metadata        mergeArms_log       pfsConfig
coaddSpectra_config    fitFluxReference_config    mergeArms_metadata  pfsFluxReference
coaddSpectra_log       fitFluxReference_log       objectGroupMap      pfsMerged
coaddSpectra_metadata  fitFluxReference_metadata  packages            pfsMergedLsf
cosmicray_config       fluxCal                    pfsArm              reduceExposure_config
cosmicray_log          isr_config                 pfsArmLsf           reduceExposure_log
cosmicray_metadata     isr_log                    pfsCalibrated       reduceExposure_metadata
detectorMap            isr_metadata               pfsCalibratedLsf    sky1d
fitFluxCal_config      lam1d_modified             pfsCoadd
```

Most of these files are not of much significance to the user as they are intermediate pipeline and QA products. The relevant PFS data products and their properties for the science user will be highlighted going forward, but for a detailed description please refer to the [PFS Data Model documentation](https://github.com/Subaru-PFS/datamodel/blob/master/datamodel.txt).

Finally we note here that in this section we will provide explanations and code for quick analysis of PFS data products out of the box; the user is also encouraged to follow the [PFS Science Platform Getting-Started Notebook](https://hscpfs.mtk.nao.ac.jp/portal/) — a Jupyter Notebook that provides a step-by-step guide and a granular understanding of each data product.