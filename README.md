# RamPo

RamPo is a desktop application for processing Raman spectroscopy data, with a workflow adapted from PeakPo and refocused for high-pressure Raman experiments.

## Current Scope

RamPo is designed around Raman spectroscopy for high pressure research.

Key points:

- input data: `.spe` Raman files
- 2D detector view: CCD image
- reference library concept: `RAPO` files for pressure-dependent Raman mode shifts (under development)
- session/save model: JSON-based snapshots stored in `<filename>-rampo/`

## Main Features

- open and navigate SPE files
- convert wavelength-calibrated SPE data to Raman shift using the excitation laser wavelength
- define CCD row ROI and extract summed spectra from the ROI
- apply despike + Savitzky-Golay smoothing
- fit Raman background with polynomial fitting using user-defined background areas
- save background, bg-subtracted, smoothed, and ROI-derived spectra
- compare spectra with Diff
- process file sets with Map and Seq
- display and manage Waterfall spectra
- perform PeakFit analysis
- save and restore numbered backup snapshots

## Installation

RamPo requires Python 3.10 or newer.

```bash
pip install rampo
```

## Running RamPo

```bash
rampo
```

## Typical Workflow

1. Open an `.spe` file by clicking `Open SPE` button.
2. Set the excitation laser wavelength.
3. Use the top mouse toolbar to switch between `Zoom`, `ROI`, and `Peak`.
4. In `Spectrum`, use `ROI` on the top CCD image to define the CCD row ROI for spectrum extraction.
5. Still in `Spectrum`, leave mouse mode in `ROI` and drag on the 1D spectrum to add background-fit areas. Repeat as needed, then click `Fit BG`. Check `Bg show` to display the fitted background and `BgSub` to subtract it.
6. Adjust `Smoothing` options if despike or Savitzky-Golay smoothing is needed.
7. For mapping, open the `Map` tab and click `Load SPE files` to select the map files. For ASU data, choose `*-raw.spe` files. Select `Row-major` for ASU data and `Snake` for APS data. Confirm `Nx` and `Ny`, then click `Compute Map`.
8. In `Map` or `Seq`, click the top `ROI` mouse mode, drag the spectral range on the main spectrum plot, and RamPo will return to `Zoom` after the ROI is set.
9. Use Diff, Waterfall, or PeakFit tools as needed. In PeakFit, switch to top `Peak` mode to add or remove peaks on the spectrum.
10. Press `Save` to create a numbered snapshot in the session folder.

## Save / Restore Behavior

RamPo saves analysis state into a folder named:

```text
<filename>-rampo
```

Inside that folder, numbered snapshot folders are created:

```text
0/
1/
2/
...
```

Each numbered backup is intended to be self-contained and stores the JSON session state together with processed outputs such as spectra and related analysis files.

## Notes

- Some disabled UI elements are intentionally kept visible as placeholders for future development.

## Citation

> RamPo - Raman spectroscopy analysis software for high-pressure experiments.

The citation string shipped with the package is defined in `rampo/rampo/citation.py`.
