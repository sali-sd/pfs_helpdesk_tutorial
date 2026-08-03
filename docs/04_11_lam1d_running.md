# Running the LAM 1D Pipeline

Once the pipeline is installed (see [Installing the Pipeline](04_09_lam1d_install.md)), activate the conda environment and run `drp_1dpipe` with the appropriate arguments.

---

## Basic command

```bash
conda activate pfs-pipeline-1.18.0

drp_1dpipe -j <cores> -n0 \
    --workdir <path/to/working/directory> \
    --coadd_file <path/to/input/pfsCoadd/file> \
    -o <path/to/output/directory> \
    -p <path/to/parameters/file>
```

**Example:**

```bash
drp_1dpipe -j 20 -n0 \
    --workdir /home/sali/1dval/lam1d \
    --coadd_file /lfs_pfs/Subaru/PFS/data/datastore_20260226/PFS/science/run26/coadd.20260430/brn/20260528T144720Z/pfsCoadd/10094/pfsCoadd_PFS_brn_run26_10094_1_PFS_science_run26_coadd_20260430_brn_20260528T144720Z.fits \
    -o /home/sali/1dval/lam1d/results \
    -p /home/sali/1dval/lam1d/parameters_ex.json
```

---

## Main parameters

| Parameter                | Description                                                                                                                                                               |
| ------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `-j <cores>`             | Number of CPU cores to use in parallel. Use `$(nproc)` to use all available cores, or specify a number (e.g. `-j 20`). Each spectrum takes about 8–10 minutes to process. |
| `-n0`                    | No limit on the number of spectra per bunch — processes all spectra in the input file in one go. Increase if memory is limited.                                           |
| `--workdir`              | Path to the working directory. Must contain a `calibration/` subdirectory with `LSF/`, `templates/`, `linecatalogs/` etc. inside it.                                      |
| `--coadd_file`           | Full path to the input `pfsCoadd` FITS file containing the coadded spectra to process                                                                                     |
| `-o`                     | Output directory where results (`pfsCoZcandidates` FITS files) will be written.                                                                                           |
| `-p`                     | Full path to the JSON parameter file controlling pipeline parameters (wavelength range, line fitting options etc.)                                                        |
| `--scheduler` (optional) | Job scheduler: `local` (default), `pbs`, or `slurm`. Use `pbs` or `slurm` for cluster batch submission.                                                                   |
| `--loglevel` (optional)  | Logging verbosity: `DEBUG`, `INFO` (default), `WARNING`, `ERROR`, `CRITICAL`                                                                                              |

---

## Config file

The full list of available parameters and their default values is defined in [drp_1dpipe/auxdir/parameters_sgq.json](https://github.com/Subaru-PFS/drp_1dpipe/blob/master/drp_1dpipe/auxdir/parameters_sgq.json) on the pipeline GitHub page. The user only needs to specify parameters they want to override — any parameter not included in the parameter file falls back to the pipeline's default values.

A working example parameter file (`parameters_ex.json`) is provided in the [PFS-LAM1D-Installation repository](https://github.com/sali-sd/PFS-LAM1D-Installation). It explicitly sets only three parameters:

- `lambdaRange` — wavelength range to process: `[4000, 9600]` Å
- `lsf.gaussianVariableWidthFileName` — path to the LSF file relative to the `calibration/` directory: `LSF/lsf_lowres_fixed.fits`
- `spectrumModel_galaxy.lineMeasSolver.lineMeasSolve.lineModel.lineTypeFilter` — set to `"no"` to measure all spectral lines (both emission and absorption) for galaxies, without restricting to a specific line type

All other parameters fall back to the pipeline defaults.

### Confirming parameters used

Once the pipeline is running, the full set of parameters used (defaults + overrides) is written to `parameters.json` in the output directory, alongside `config.json`, `data/`, `log/`, and `report.json`.

---

## Calibration files

Calibration files (templates, line catalogs, LSF files, IGM/ISM tables) are required and must be passed via `--workdir`. The calibration files for version `1.18.0` are included in the [PFS-LAM1D-Installation repository](https://github.com/sali-sd/PFS-LAM1D-Installation), though these files may be updated over time. The latest calibration files are available at:

```
https://pfs.ipmu.jp/internal/devarch/lam-drp1d/
```

Access requires PFS project credentials.

---

## Outputs

The pipeline writes one `pfsCoZcandidates` FITS file per `pfsCoadd` input file into the output directory (`-o`). Each file contains redshift candidates, probability distributions, and line measurements for all spectra in the input file.

For a full description of the output data format and all output products, see the [PFS datamodel](https://github.com/Subaru-PFS/datamodel/blob/master/datamodel.txt).

Log files are written to `<output>/log/` and can be monitored during the run:

```bash
tail -f <output>/log/scheduler.log
tail -f <output>/log/pre_process.log
```
