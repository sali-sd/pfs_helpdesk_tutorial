# Preparation

## Supported Machines and Environments

The current Gen3 2D DRP (later than `w.2026.07`) is supported on `AlmaLinux 9` only.

The PFS 2D DRP pipeline is built upon the LSST pipeline, and requires that it be installed. These pipelines use Python 3.13 features; lower python versions (python &ge; `3.9`) may be acceptable for using the `datamodel` package without the pipeline.

Support for additional systems may be added in the future.

### Prerequisites

The LSST v30 prerequisites are listed in the official [webpage](https://pipelines.lsst.io/install/prereqs.html#system-prereqs). For AlmaLinux 9, `patch` and `git` are required:

```bash
sudo dnf install patch git
```

