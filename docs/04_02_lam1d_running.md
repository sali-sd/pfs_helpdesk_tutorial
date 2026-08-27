# Running the LAM 1D Pipeline

Once the pipeline is installed (see [Installing the Pipeline](04_01_lam1d_install.md)), activate the conda environment and run `drp_1dpipe` with the appropriate arguments.

---

## Basic Command

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



## Main Parameters


| Parameter                | Description                                                                                                                                                               |
| ------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `-j <cores>`             | Number of CPU cores to use in parallel. Use `$(nproc)` to use all available cores, or specify a number (e.g. `-j 20`). Each spectrum takes about 8–10 minutes to process. |
| `-n0`                    | No limit on the number of spectra per bunch — processes all spectra in the input file in one go. Specify a smaller number (e.g. `-n 100`) if memory is limited.           |
| `--workdir`              | Path to the working directory. Must contain a `calibration/` subdirectory with `LSF/`, `templates/`, `linecatalogs/` etc. inside it.                                      |
| `--coadd_file`           | Full path to the input `pfsCoadd` FITS file containing the coadded spectra to process                                                                                     |
| `-o`                     | Output directory where results (`pfsCoZCandidates` FITS files) will be written.                                                                                           |
| `-p`                     | Full path to the JSON parameter file controlling pipeline parameters (wavelength range, line fitting options, etc.)                                                       |
| `--scheduler` (optional) | Job scheduler: `local` (default), `pbs`, or `slurm`. Use `pbs` or `slurm` for cluster batch submission.                                                                   |
| `--loglevel` (optional)  | Logging verbosity: `DEBUG`, `INFO` (default), `WARNING`, `ERROR`, `CRITICAL`                                                                                              |


---



## Parameter File

The full list of available parameters and their default values is defined in [drp_1dpipe/auxdir/parameters_sgq.json](https://github.com/Subaru-PFS/drp_1dpipe/blob/master/drp_1dpipe/auxdir/parameters_sgq.json) on the pipeline GitHub page. The user only needs to specify parameters they want to override — any parameter not included in the parameter file falls back to the pipeline's default values.

A working example parameter file (`parameters_ex.json`) is provided in the [PFS-LAM1D-Installation](https://github.com/sali-sd/pfs_helpdesk_tutorial/tree/main/PFS-LAM1D-Installation) folder of this repository. It explicitly sets only three parameters:

- `lambdaRange` — wavelength range to process: `[4000, 9600]` Å
- `lsf.gaussianVariableWidthFileName` — path to the LSF file relative to the `calibration/` directory: `LSF/lsf_lowres_fixed.fits`
- `spectrumModel_galaxy.lineMeasSolver.lineMeasSolve.lineModel.lineTypeFilter` — set to `"no"` to measure all spectral lines (both emission and absorption) for galaxies, without restricting to a specific line type

All other parameters fall back to the pipeline defaults.

---



## Calibration Files

Calibration files (templates, line catalogs, LSF files, IGM/ISM tables) are required and must be passed via `--workdir`. The latest calibration files are available at:

```
https://hscpfs.mtk.nao.ac.jp/nextcloud/s/jEqyZmicHXCNsi6?opendetails=
```

---



## Outputs

A successful run populates the output directory (`-o`) with the following:

```
<output>/
├── config.json
├── parameters.json
├── report.json
├── data/
│   └── pfsCoZcandidates-<catId>.fits
└── log/
```


| Path                                 | Description                                                                                                                                                                                                                                                                                                 |
| ------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `data/pfsCoZcandidates-<catId>.fits` | Main science product — one FITS file per `pfsCoadd` input, containing redshift candidates, probability distributions, and line measurements for all spectra. See [pfsCoZCandidates](04_04_lam1d_zcandidates.md) and the [PFS datamodel](https://github.com/Subaru-PFS/datamodel/blob/master/datamodel.txt). |
| `config.json`                        | Run configuration written by the pipeline (working directory, log directory, scheduler, concurrency, input `coadd_file`, output directory, parameter file path, stellar mode, etc.).                                                                                                                        |
| `parameters.json`                    | Full set of pipeline parameters actually used for the run (defaults plus any overrides from `-p`).                                                                                                                                                                                                          |
| `report.json`                        | Summary of the run: object counts and fractions by class (galaxy / qso / star), redshift-error counts/fractions per class, and aggregate line-measurement stats (line counts, positive-flux lines, etc.).                                                                                                   |
| `log/`                               | Log files for the run (scheduler, pre-processing, per-bunch jobs, merge). Useful for monitoring progress, e.g. `tail -f <output>/log/scheduler.log`.                                                                                                                                                        |


