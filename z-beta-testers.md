# RamPo Beta Tester Instructions

This document explains how to download RamPo from GitHub to your computer, activate the `pkpo710` conda environment, and run the program.

## 1. Download RamPo From GitHub

If you have been given access to the private GitHub repository:

1. Open the repository page in your web browser.
2. Click the green `Code` button.
3. Choose one of the following:

### Option A: Download ZIP

1. Click `Download ZIP`.
2. Save the ZIP file to your computer.
3. Extract the ZIP file to a folder you can easily find later.

Example locations:

- Windows: `C:\Users\<your-name>\Documents\RamPo`
- Mac: `/Users/<your-name>/Documents/RamPo`

### Option B: Clone With Git

If Git is already installed, copy the repository URL from the `Code` button and run:

```bash
git clone <repo-url>
```

This will create a local folder named `RamPo`.

## 2. Open a Terminal

### On Windows

Use one of these:

- `Anaconda Prompt`
- `Miniforge Prompt`
- `Terminal` inside VS Code if conda works there

### On macOS

Use:

- `Terminal`

## 3. Go to the RamPo Folder

Change into the folder that contains the downloaded repository.

Example:

```bash
cd path/to/RamPo
```

Examples:

```bash
cd C:\Users\<your-name>\Documents\RamPo
```

```bash
cd /Users/<your-name>/Documents/RamPo
```

## 4. Activate the Conda Environment

Activate the existing `pkpo710` environment:

```bash
conda activate pkpo710
```

If that does not work, first initialize conda in that shell, then try again.

Examples:

```bash
conda init
```

Then close and reopen the terminal, and run:

```bash
conda activate pkpo710
```

## 5. Run RamPo

From inside the repository folder, run:

```bash
python -m rampo
```

If `python` does not work in that shell, try:

```bash
python3 -m rampo
```

## 6. Daily Use

Each time you want to run RamPo:

1. Open `Terminal` or `Anaconda Prompt`
2. Go to the RamPo folder
3. Activate `pkpo710`
4. Run:

```bash
python -m rampo
```

## 7. Updating to a Newer Beta Version

### If you downloaded ZIP

1. Download the new ZIP from GitHub
2. Extract it
3. Replace the old RamPo folder with the new one

### If you cloned with Git

Inside the RamPo folder, run:

```bash
git pull
```

Then activate the environment and run again:

```bash
conda activate pkpo710
python -m rampo
```

## 8. If RamPo Does Not Start

Please report:

- your operating system
- whether you used ZIP download or `git clone`
- the exact command you ran
- the full error message shown in the terminal

If possible, also include:

- one sample `.spe` file that caused the problem
- a screenshot of the error message

## 9. Important Note for Beta Testers

RamPo is under active beta testing. Some UI elements are intentionally disabled because they are reserved for future development.
