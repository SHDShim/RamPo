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

If you already have PeakPo 7.10.x installed and a conda environment named `pkpo710`, you can install RamPo in that environment.

```bash
conda activate pkpo710
```

```bash
pip install rampo
```

## Running RamPo

```bash
conda activate pkpo710
```

```bash
rampo
```

## Typical Workflow

1. Open an `.spe` file by clicking `Open SPE` button.
2. Set the excitation laser wavelength.
3. In the top toolbar, click the `CCD` button and the zoom-out button to rescale the spectrum display.
4. In the `Spectrum` > `Process` tab, click `Select ROI` and draw a rectangle in the top image to define the ROI for spectrum integration.
5. In the same tab, adjust the parameters in `Smoothing` if smoothing is needed.
6. In the same tab, to define the background, click `Add area` and draw a rectangle on the lower spectrum plot to mark a range for background data points. Repeat this for several areas, ideally including both the left and right ends of the spectrum. Once you have selected enough background points, click `Fig BG` to fit the background. Check the `Bg show` box to display the fit, and check `BgSub` to subtract the background.
7. For mapping, open the `Map` tab and click `Load SPE files` to select the map files. For ASU data, make sure you choose `*-raw.spe` files. Select `Row-major` for ASU data and `Snake` for APS data in the dropdown menu. Make sure `Nx` and `Ny` are correctly detected by RamPo. If not, update the values and then click `Compute Map`.
8. In the `Map` tab, click `Select ROI` to choose the spectral range where intensity mapping will be performed.
9. Use Diff, Seq, Waterfall, or PeakFit tools as needed.
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

Current citation placeholder:

> RamPo - Raman spectroscopy analysis software for high-pressure experiments.

See [rampo/rampo/citation.py](/Users/danshim/Python-git/RamPo/rampo/rampo/citation.py).
See [rampo/rampo/citation.py](rampo/rampo/citation.py).
