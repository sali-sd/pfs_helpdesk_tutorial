# Overview of PFS Data Products

This section describes the main PFS spectroscopic data products produced by the 2D DRP pipeline. They are all stored as FITS files and follow a strict naming convention based on observation identifiers.

We will show how PFS data products are stored, can be accessed and analyzed using **Butler**. Data on the [PFS Science Platform](https://hscpfs.mtk.nao.ac.jp/portal/) will be used as reference, specifically data products from proposal ID `S25A-000QF`, which is part of the **PFS Filler Program** and available to everyone that signs up to the Science Platform.

While we use the above data for demonstration, the method of accessing and analyzing PFS data products using **Butler** is universally applicable to all 2D DRP pipeline reduced data.

The relevant parameters and properties of PFS data products are highlighted as necessary, but for a detailed description please refer to the [PFS Data Model documentation](https://github.com/Subaru-PFS/datamodel/blob/master/datamodel.txt).

Finally we note here that in this section we will provide explanations and code for quick analysis of PFS data products, we also encourage users to follow the [PFS Science Platform Getting-Started Notebook](https://hscpfs.mtk.nao.ac.jp/portal/) — a Jupyter Notebook that provides a step-by-step guide and a granular understanding of each PFS data product.