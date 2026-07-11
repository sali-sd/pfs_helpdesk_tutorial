# pfsCoadd Spectrum + LAM 1D Spectral Lines

The following code plots the `pfsCoadd` spectrum of a single object overlaid with the LAM 1D best-fit model, and marks detected spectral lines. It requires the `{collections}_all_lam1d.csv` file produced by the object table code in the [pfsCoZCandidates](04_12_lam1d_zcandidates.md) section — run that code once before using this plotter.

The code supports three modes of object selection:

- **By `objid`** — plots that object directly, auto-detecting its class from the CSV
- **By class + redshift/velocity** — finds the object in the CSV closest to a target redshift (GALAXY/QSO) or velocity (STAR)
- **By class + `browse_index`** — steps through all objects of a given class sorted by descending redshift/velocity

Once an object is loaded, the code fetches the `pfsCoadd` spectrum via the Butler and reads the corresponding LAM 1D FITS file directly from disk. The main plot shows the observed spectrum (black) and the LAM 1D model fit (red) with detected line positions marked. For GALAXY and QSO objects, up to four zoom panels below the main plot show the top-ranked lines by SNR, with the line name, SNR, and equivalent width displayed. A summary table of the top 10 lines by SNR is also printed to the terminal.

```python
import os
import glob
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import ndimage
from lsst.daf.butler import Butler
from pfs.datamodel import PfsCoZCandidates

# ==== FILE LOCATION PARAMETERS ====
repo        = "/shared/pfs/programs/S25A-000QF/2d/"
collections = "S25A_April2026"
lam1d_dir   = "/shared/pfs/programs/S25A-000QF/lam1d/S25A_April2026/modified" # Ensure this directory matches the COLLECTIONS

# ==== CHOOSE CLASS AND INDEX/REDSHIFT/VELOCITY OR OBJID ====
# Note: Set to None if you do not want to use a particular parameter

class_name           = "GALAXY"   # 'GALAXY', 'QSO' or 'STAR'
browse_index         = 0          # 0 = highest redshift/velocity, increment to browse
search_redshift      = 0.30       # GALAXY/QSO: find closest object to this redshift, overrides browse_index
search_velocity_kms  = None       # STAR: find closest object to this velocity [km/s], overrides browse_index
objid                = None       # if set, overrides everything else and plots target spectrum directly. Input None if browsing data using above options

# ==== PLOT PARAMETERS ====
MEDIAN_FILTER_SIZE = 1  # 1 = no filtering, increment for smoothing as desired
arms               = ['b', 'r']   # options: 'b', 'r', 'n' or any combination of arms to plot

# ==== PFSCOADD+LAM1D PLOTTING FUNCTION ====
def plot_pfscoadd_lam1d(
    repo, collections, lam1d_dir,
    class_name, browse_index, search_redshift, search_velocity_kms, objid,
    MEDIAN_FILTER_SIZE, arms,
):
    ARM_RANGES = {
        'b': (380,  650),
        'r': (630,  970),
        'n': (940, 1260),
    }

    # ==== RESOLVE OBJECT ====
    if objid is not None:
        objid  = int(objid)
        df_all = pd.read_csv(f"{collections}_all_lam1d.csv")
        df_all['objId'] = df_all['objId'].astype(np.int64)
        matches = df_all[df_all['objId'] == np.int64(objid)]
        if matches.empty:
            raise ValueError(f"objId {objid} not found in {collections}_all_lam1d.csv")
        row        = matches.iloc[0]
        class_name = row['class'].upper()
        print(f"Auto-detected class: {class_name} for objId={objid}")

    elif search_redshift is not None or search_velocity_kms is not None:
        df          = pd.read_csv(f"{collections}_all_lam1d.csv")
        df['objId'] = df['objId'].astype(np.int64)
        df          = df[df['class'].str.upper() == class_name.upper()].reset_index(drop=True)
        redshift_column = {"GALAXY": "redshift_gal", "QSO": "redshift_qso", "STAR": "velocity_star"}[class_name.upper()]
        if class_name.upper() == "STAR":
            if search_velocity_kms is None:
                raise ValueError("class_name is STAR but search_velocity_kms is not set")
            target_val = search_velocity_kms * 1000
            label_str  = f"velocity={search_velocity_kms} km/s"
        else:
            if search_redshift is None:
                raise ValueError(f"class_name is {class_name} but search_redshift is not set")
            target_val = search_redshift
            label_str  = f"z={search_redshift}"
        closest_idx = (df[redshift_column] - target_val).abs().idxmin()
        row         = df.loc[closest_idx]
        objid       = int(row['objId'])
        found_val   = row[redshift_column] * (1e-3 if class_name.upper() == "STAR" else 1)
        found_unit  = "km/s" if class_name.upper() == "STAR" else ""
        print(f"Target {label_str} → closest object at {redshift_column}={found_val:.4f} {found_unit}  (idx={closest_idx})")

    else:
        df          = pd.read_csv(f"{collections}_all_lam1d.csv")
        df['objId'] = df['objId'].astype(np.int64)
        df          = df[df['class'].str.upper() == class_name.upper()].reset_index(drop=True)
        redshift_column = {"GALAXY": "redshift_gal", "QSO": "redshift_qso", "STAR": "velocity_star"}[class_name.upper()]
        df_sorted       = df.sort_values(redshift_column, ascending=False).reset_index(drop=True)
        print(f"Loaded {len(df_sorted)} {class_name} objects from {collections}_all_lam1d.csv")
        print(f"Sorted by {redshift_column} descending  |  Showing index {browse_index} of {len(df_sorted)-1}")
        row   = df_sorted.iloc[browse_index]
        objid = int(row['objId'])

    # ==== REDSHIFT/VELOCITY COLUMN PER CLASS ====
    redshift_column  = {"GALAXY": "redshift_gal", "QSO": "redshift_qso", "STAR": "velocity_star"}[class_name.upper()]
    catid            = int(row['catid'])
    obj_group        = int(row['obj_group'])
    redshift_value   = row[redshift_column]
    redshift_label   = f"velocity={redshift_value/1000:.1f} km/s" if class_name.upper() == "STAR" else f"z={redshift_value:.4f}"
    mag_cols_present = [col for col in row.index if col.startswith('mag_')]
    best_mag_col     = next((col for col in mag_cols_present if pd.notna(row[col])), None)
    mag_str          = f"{best_mag_col.replace('mag_', '')}={row[best_mag_col]:.2f}" if best_mag_col else "mag=N/A"

    # ==== PROBABILITIES ====
    redshift_proba_col = {"GALAXY": "redshiftProba_gal", "QSO": "redshiftProba_qso", "STAR": "templateProba_star"}[class_name.upper()]
    class_proba_col    = {"GALAXY": "probaGalaxy",       "QSO": "probaQSO",          "STAR": "probaStar"}[class_name.upper()]
    redshift_proba_str = f"{row[redshift_proba_col]:.3f}" if redshift_proba_col in row.index and pd.notna(row[redshift_proba_col]) else "N/A"
    class_proba_str    = f"{row[class_proba_col]:.3f}"    if class_proba_col    in row.index and pd.notna(row[class_proba_col])    else "N/A"

    print(f"ObjId={objid}  CatID={catid}  ObjGroup={obj_group}  {redshift_column}={redshift_value:.4f}  {mag_str}  zProba={redshift_proba_str}  classProba={class_proba_str}")

    # ==== BUTLER + COMBINATION ====
    butler      = Butler(repo, collections=collections)
    datarefs    = list(butler.registry.queryDatasets('pfsCoadd'))
    combination = datarefs[0].dataId['combination']

    # ==== LOAD DATA ====
    print(f"Loading pfsCoadd and LAM1D for catid={catid} obj_group={obj_group}...")
    pfscoadd  = butler.get("pfsCoadd", combination=combination, cat_id=catid,
                           instrument='PFS', obj_group=obj_group)
    base_dir  = f"{lam1d_dir}/{catid}_{obj_group}"
    fits_path = sorted(glob.glob(f"{base_dir}/**/*.fits", recursive=True))
    if not fits_path:
        raise ValueError(f"No LAM1D FITS file found in {base_dir}")
    coZCands  = PfsCoZCandidates.readFits(fits_path[0])

    # ==== FETCH OBJECT ====
    pfsobject = pfscoadd[int(objid)]

    try:
        zCand = coZCands[int(objid)]
    except KeyError:
        raise ValueError(f"objId {objid} not found in LAM1D FITS")

    # ==== MODEL AND LINES ====
    top4 = None
    if class_name.upper() == "STAR":
        print("STAR object — LAM1D model fit uses stellar templates (no emission lines)")
        model      = zCand.get_classified_model()
        line_names = []
        line_waves = []
    else:
        model = zCand.get_classified_model()
        lines = zCand.qso.lines if class_name.upper() == "QSO" else zCand.galaxy.lines
        if lines is not None:
            line_names      = lines['lineName'].tolist()
            line_waves      = lines['lineWave'].tolist()
            lines_df        = lines.to_pandas()
            lines_df['SNR'] = lines_df['lineFlux'] / lines_df['lineFluxError']
            top10           = lines_df.nlargest(10, 'SNR')
            top4            = top10.head(4)
            print(f"\n---- Top 10 Lines by SNR  (global z={redshift_value:.4f}) ----")
            print(f"  {'Line':<12}  {'SNR':>6}  {'EW':>8}  {'EW_err':>8}  {'lineZ':>7}  {'dz':>7}  {'sigma':>6}")
            print(f"  {'----':<12}  {'---':>6}  {'--':>8}  {'------':>8}  {'-----':>7}  {'--':>7}  {'-----':>6}")
            for _, r in top10.iterrows():
                dz = r['lineZ'] - redshift_value
                print(f"  {r['lineName']:<12}  {r['SNR']:>6.1f}  {r['lineEW']:>8.1f}  {r['lineEWError']:>8.1f}  {r['lineZ']:>7.4f}  {dz:>+7.4f}  {r['lineSigma']:>6.2f}")
            print()
        else:
            line_names = []
            line_waves = []
            print("No lines table available.\n")

    # ==== ARM MASK ====
    arm_mask = np.zeros(len(pfsobject.wavelength), dtype=bool)
    for arm in arms:
        lo, hi = ARM_RANGES[arm]
        arm_mask |= (pfsobject.wavelength >= lo) & (pfsobject.wavelength <= hi)

    xlim_lo = min(ARM_RANGES[arm][0] for arm in arms)
    xlim_hi = max(ARM_RANGES[arm][1] for arm in arms)

    # ==== MASK BAD PIXELS ====
    pixels_bad  = (pfsobject.mask & pfsobject.flags.get('BAD', 'CR', 'SAT', 'NO_DATA')) != 0
    pixels_good = arm_mask & ~pixels_bad

    # ==== YLIM ====
    flux_in_range = pfsobject.flux[pixels_good]
    p2, p98       = np.nanpercentile(flux_in_range, [2, 98])
    span          = p98 - p2
    ylim_lower    = p2  - 0.05 * span
    ylim_upper    = p98 + 0.15 * span

    # ==== PLOT ====
    has_zoom = top4 is not None and len(top4) > 0
    n_zoom   = len(top4) if has_zoom else 0

    if has_zoom:
        fig = plt.figure(figsize=(15, 7))
        gs  = fig.add_gridspec(2, 4, height_ratios=[2.5, 1],
                               top=0.88, bottom=0.08, left=0.05, right=0.98,
                               hspace=0.35, wspace=0.12)
        ax_main = fig.add_subplot(gs[0, :])
    else:
        fig, ax_main = plt.subplots(figsize=(12, 5))
        fig.subplots_adjust(top=0.88, bottom=0.1, left=0.07, right=0.97)

    ax_main.plot(pfsobject.wavelength[pixels_good],
                 ndimage.median_filter(pfsobject.flux[pixels_good], size=MEDIAN_FILTER_SIZE),
                 linewidth=0.5, color='black', label=f'PFSCoadd (Median Filter={MEDIAN_FILTER_SIZE})')
    ax_main.plot(pfsobject.wavelength[arm_mask],
                 ndimage.median_filter(model[arm_mask], size=MEDIAN_FILTER_SIZE),
                 linewidth=0.5, color='red',
                 label='LAM1D Stellar Template' if class_name.upper() == "STAR" else 'LAM1D Model',
                 alpha=0.7)
    ax_main.set_xlim([xlim_lo, xlim_hi])
    ax_main.set_ylim([ylim_lower, ylim_upper])
    ax_main.ticklabel_format(axis='y', style='sci', scilimits=(0, 0))

    # ==== EMISSION LINE MARKERS ====
    x_lo, x_hi = ax_main.get_xlim()
    y_top       = ax_main.get_ylim()[1]
    for lw, ln in zip(line_waves, line_names):
        if not (x_lo <= lw <= x_hi):
            continue
        ax_main.axvline(x=lw, color='red', linestyle='--', alpha=0.3, linewidth=0.5)
        ax_main.text(lw, y_top * 0.95, ln, rotation=90,
                     verticalalignment='top', horizontalalignment='right',
                     fontsize=7, color='red')

    arms_label = '+'.join(arms)
    ax_main.set_title(f'PFSCoadd {class_name}  ObjID={objid}  CatID={catid}  ObjGroup={obj_group}  {redshift_label}  zProba={redshift_proba_str}  classProba={class_proba_str}  {mag_str}  Arms={arms_label}\n'
                      f'Repo={repo}  Collections={collections}  Combination={combination}')
    ax_main.legend(loc='upper left', fancybox=True, framealpha=0.5)
    ax_main.minorticks_on()
    ax_main.set_xlabel('Wavelength [nm]')
    ax_main.set_ylabel('Flux [nJy]')

    # ==== ZOOM SUBPLOTS ====
    if has_zoom:
        for i in range(4):
            ax = fig.add_subplot(gs[1, i])
            if i < n_zoom:
                r      = top4.iloc[i]
                lw_ctr = r['lineWave']
                if class_name.upper() == "QSO":
                    hw = np.clip(round(r['lineSigma'] * 12), 6, 80)
                else:
                    hw = np.clip(round(r['lineSigma'] * 6), 3, 40)
                w_lo   = lw_ctr - hw
                w_hi   = lw_ctr + hw
                zmask  = pixels_good & (pfsobject.wavelength >= w_lo) & (pfsobject.wavelength <= w_hi)
                zarm   = (pfsobject.wavelength >= w_lo) & (pfsobject.wavelength <= w_hi)
                if zmask.sum() > 0:
                    ax.plot(pfsobject.wavelength[zmask],
                            ndimage.median_filter(pfsobject.flux[zmask], size=MEDIAN_FILTER_SIZE),
                            linewidth=0.8, color='black')
                    ax.plot(pfsobject.wavelength[zarm],
                            ndimage.median_filter(model[zarm], size=MEDIAN_FILTER_SIZE),
                            linewidth=0.8, color='red', alpha=0.7)
                    zp2, zp98 = np.nanpercentile(pfsobject.flux[zmask], [2, 98])
                    zspan     = zp98 - zp2
                    ax.set_ylim([zp2 - 0.1 * zspan, zp98 + 0.3 * zspan])
                ax.axvline(x=lw_ctr, color='red', linestyle='--', alpha=0.5, linewidth=0.8)
                ax.set_xlim([w_lo, w_hi])
                ax.set_title(f"{r['lineName']}  SNR={r['SNR']:.1f}\nEW={r['lineEW']:.1f}±{r['lineEWError']:.1f}", fontsize=7)
                ax.set_xlabel('Wavelength [nm]', fontsize=7)
                ax.tick_params(labelsize=7)
                ax.ticklabel_format(axis='y', style='sci', scilimits=(0, 0))
                ax.minorticks_on()
                if i == 0:
                    ax.set_ylabel('Flux [nJy]', fontsize=7)
            else:
                ax.set_visible(False)

    fig.savefig(f'{collections}_{class_name}_{objid}.png', dpi=150, bbox_inches='tight')
    plt.show()

# ==== RUN ====
plot_pfscoadd_lam1d(
    repo                = repo,
    collections         = collections,
    lam1d_dir           = lam1d_dir,
    class_name          = class_name,
    browse_index        = browse_index,
    search_redshift     = search_redshift,
    search_velocity_kms = search_velocity_kms,
    objid               = objid,
    MEDIAN_FILTER_SIZE  = MEDIAN_FILTER_SIZE,
    arms                = arms,
)
```

**Output**:
```
Target z=0.3 → closest object at redshift_gal=0.3000   (idx=2829)
ObjId=120731449862702300  CatID=10094  ObjGroup=14  redshift_gal=0.3000  g_ps1=21.63  zProba=1.000  classProba=1.000
Loading pfsCoadd and LAM1D for catid=10094 obj_group=14...

---- Top 10 Lines by SNR  (global z=0.3000) ----
  Line             SNR        EW    EW_err    lineZ       dz   sigma
  ----             ---        --    ------    -----       --   -----
  Halpha         108.9       5.7       0.1   0.3000  +0.0000    0.19
  [SII]6731       37.9       0.8       0.0   0.3000  +0.0000    0.18
  [NII]a          34.8       1.2       0.0   0.3000  +0.0000    0.19
  [OIII]a         31.2       1.5       0.1   0.3000  -0.0000    0.14
  [OII]3726       26.8       2.2       0.2   0.3000  +0.0000    0.12
  [SII]6716       26.6       1.0       0.0   0.3000  +0.0000    0.18
  [OII]3729       25.4       3.5       0.2   0.3000  +0.0000    0.12
  [OIII]b         16.3       0.5       0.0   0.3000  -0.0000    0.14
  Hbeta           16.1       1.3       0.1   0.3000  -0.0000    0.13
  [NII]b          10.3       0.4       0.0   0.3000  +0.0000    0.19
```

![pfsCoadd + LAM 1D spectrum for objId 120731449862702300](figures/S25A_April2026_GALAXY_120731449862702300.png)
