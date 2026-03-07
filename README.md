# RamPo

RamPo is a desktop application for processing Raman spectroscopy data, with a workflow adapted from PeakPo and refocused for high-pressure Raman experiments.

This repository is currently intended for private GitHub hosting during beta testing. The plan is to make it public after the beta phase is complete.

## Current Scope

RamPo is designed around Raman spectroscopy for high pressure research.

Key points:

- input data: `.spe` Raman files
- 2D detector view: CCD image
- 1D processed view: Raman spectrum in Raman shift (`cm$^{-1}$`)
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

## Running RamPo

From the repository root:

```bash
python3 -m rampo
```

The application entrypoint is:

- [rampo/__main__.py](rampo/__main__.py)

## Typical Workflow

1. Open an `.spe` file.
2. Set the excitation laser wavelength.
3. Define the CCD ROI.
4. Configure smoothing if needed.
5. Define background fit areas and fit the background.
6. Use Spectrum, Map, Diff, Seq, Waterfall, or PeakFit tools as needed.
7. Press `Save` to create a numbered snapshot in the session folder.

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

## Version

Current application version:

- `0.1.0`

See [rampo/rampo/version.py](/Users/danshim/Python-git/RamPo/rampo/rampo/version.py).
See [rampo/rampo/version.py](rampo/rampo/version.py).

## Citation

Current citation placeholder:

> Rampo - Raman spectroscopy analysis software for high-pressure experiments.

See [rampo/rampo/citation.py](/Users/danshim/Python-git/RamPo/rampo/rampo/citation.py).
See [rampo/rampo/citation.py](rampo/rampo/citation.py).

## Status

Private beta.

The codebase has been heavily adapted from PeakPo toward Raman spectroscopy. Further cleanup, renaming, and documentation refinement are still ongoing before public release.
