# Zenodo DOI Release Checklist

Use this checklist when preparing a DOI-bearing RamPo release through the
GitHub-Zenodo integration.

## Before Creating the GitHub Release

1. Confirm that `rampo/rampo/version.py`, `CITATION.cff`, and the GitHub
   release tag all use the same PEP 440 version string.
2. Confirm that `README.md` describes the current user-facing behavior.
3. Confirm that `LICENSE` and `pyproject.toml` both identify the license as
   GPL-3.0-only.
4. Confirm that `.zenodo.json` has the correct title, creator list, license,
   keywords, and description.
5. Run the package build check:

   ```bash
   python -m build
   ```

6. Install the built wheel in a clean environment and confirm that the command
   starts:

   ```bash
   python -m venv /tmp/rampo-release-test
   source /tmp/rampo-release-test/bin/activate
   pip install dist/rampo-<version>-py3-none-any.whl
   rampo
   ```

## Creating the DOI

1. Enable the GitHub-Zenodo integration for `SHDShim/RamPo`.
2. Create a GitHub release from the target tag.
3. Wait for Zenodo to archive the release and mint the DOI.
4. Copy the Zenodo DOI into the GitHub release notes.
5. Update the `README.md` citation section and, if desired, add the DOI to
   `CITATION.cff` after the DOI is available.

## Suggested Citation Template

```text
Shim, S.-H. Dan (2026). RamPo: Raman spectroscopy analysis software for
high-pressure experiments (Version <version>) [Computer software]. Zenodo.
https://doi.org/<doi>
```
