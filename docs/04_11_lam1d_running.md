# Running the LAM 1D Pipeline

Once the pipeline is installed (see [Installing the Pipeline](04_09_lam1d_install.md)), activate the conda environment and run `drp_1dpipe` with the appropriate arguments.

---

## Basic command

```bash
conda activate pfs-pipeline-1.18.0

drp_1dpipe -j <cores> -n0 \
    --workdir <path/to/calibration> \
    --coadd_file <path/to/pfsCoadd.fits> \
    -o <path/to/output> \
    -p <path/to/config.json>
```

**Example:**

```bash
drp_1dpipe -j 20 -n0 \
    --workdir /home/sali/1dval/lam1d \
    --coadd_file /lfs_pfs/Subaru/PFS/data/datastore_20260226/PFS/science/run26/coadd.20260430/brn/20260528T144720Z/pfsCoadd/10094/pfsCoadd_PFS_brn_run26_10094_1_PFS_science_run26_coadd_20260430_brn_20260528T144720Z.fits \
    -o /home/sali/1dval/results \
    -p /home/sali/1dval/lam1d/config_run26_brn_400_960.json
```

---

## Main parameters

| Parameter                | Description                                                                                                                                                               |
| ------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `-j <cores>`             | Number of CPU cores to use in parallel. Use `$(nproc)` to use all available cores, or specify a number (e.g. `-j 20`). Each spectrum takes about 8–10 minutes to process. |
| `-n0`                    | No limit on the number of spectra per bunch — processes all spectra in the input file in one go. Increase if memory is limited.                                           |
| `--workdir`              | Path to the working directory containing calibration files (`calibration/`, `LSF/`, templates, line catalogs etc.)                                                        |
| `--coadd_file`           | Full path to the input `pfsCoadd` FITS file containing the coadded spectra to process                                                                                     |
| `-o`                     | Output directory where results (`pfsZcandidates` FITS files) will be written. Created automatically if it does not exist.                                                 |
| `-p`                     | Full path to the JSON parameter file controlling algorithm settings (wavelength range, LSF file, line fitting options etc.)                                               |
| `--scheduler` (optional) | Job scheduler: `local` (default), `pbs`, or `slurm`. Use `pbs` or `slurm` for cluster batch submission.                                                                   |
| `--loglevel` (optional)  | Logging verbosity: `DEBUG`, `INFO` (default), `WARNING`, `ERROR`, `CRITICAL`                                                                                              |

---

## Config file

The `-p` parameter points to a JSON file that controls algorithm settings such as the wavelength range, LSF file, and line fitting options. A working template (`parameters_ex.json`) covering all three source types (galaxy, star, QSO) is provided in the [PFS-LAM1D-Installation repository](https://github.com/sali-sd/PFS-LAM1D-Installation) and can be modified as needed.

If no config file is provided, the pipeline runs with default parameters.

---

## Calibration files

Calibration files (templates, line catalogs, LSF files, IGM/ISM tables) are required and must be passed via `--workdir`. They are available for each release at:

```
https://pfs.ipmu.jp/internal/devarch/lam-drp1d/
```

Access requires PFS project credentials.

---

## Outputs

The pipeline writes one `pfsZcandidates` FITS file per `pfsCoadd` input file into the output directory (`-o`). Each file contains redshift candidates, probability distributions, and line measurements for all spectra in the input file.

Log files are written to `<output>/log/` and can be monitored during the run:

```bash
tail -f <output>/log/scheduler.log
tail -f <output>/log/pre_process.log
```
