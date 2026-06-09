# AGENTS.md

## Project Context

This repository supports Python-based scientific computing for geophysics,
planetary science, mineral physics, and materials science workflows.

Prioritize reproducibility, numerical correctness, and clear scientific
communication. Prefer concise, formal, and technically precise explanations.

## Required Environment

Use the `dev26a` conda environment for all Python work in this repository.

Before running Python commands, tests, notebooks, packaging commands, or
dependency checks, activate or invoke this environment explicitly, for example:

```zsh
conda activate dev26a
```

or:

```zsh
conda run -n dev26a python -m pytest
```

Do not use the system Python or another conda environment unless the user
explicitly requests it.

## Package Installation

If required packages are missing from `dev26a`, ask the user for permission
before installing them.

After permission is granted, install packages into `dev26a` only. Prefer conda
packages when appropriate for scientific Python dependencies, and use pip only
when conda packages are unavailable or the project already expects pip.

Examples:

```zsh
conda install -n dev26a numpy scipy pandas matplotlib
```

```zsh
conda run -n dev26a python -m pip install package-name
```

## Python Scientific Computing

- Prefer NumPy, SciPy, Pandas, Matplotlib, and related scientific libraries for
  scientific workflows.
- Use `scipy.constants` for physical constants rather than hard-coded numerical
  values.
- Use `periodictable` for atomic and elemental properties rather than
  hard-coded atomic masses, densities, or related elemental parameters.
- Keep implementations compatible with NumPy-style vectorized workflows unless
  there is a clear reason not to.
- Avoid introducing hard-coded physical constants or elemental properties when
  authoritative library values are available.

## Jupyter Notebooks

Treat `.ipynb` files as the source of truth for notebook work.

If both a notebook and a same-named `.py` file exist, assume the `.py` file is
generated automatically by a Jupyter hook unless the user explicitly says
otherwise. Do not edit the generated `.py` file directly.

Keep notebooks reproducible and well structured, with clear separation between
configuration, data input, preprocessing, analysis, plotting, and export steps.

## Documentation and Style

- Use clear Markdown hierarchy and concise structure.
- Use LaTeX for mathematical expressions when needed.
- Prefer simple, well-structured English.
- Avoid unnecessary elaboration.

## Shell

The preferred shell is `zsh`.

Use shell commands that are reproducible and explicit about the `dev26a`
environment when Python behavior depends on installed packages.
