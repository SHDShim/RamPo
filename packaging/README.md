# RamPo desktop packaging

RamPo uses PyInstaller to create native application bundles. Builds must run on
the target operating system; PyInstaller does not cross-compile Windows and
macOS applications.

## Generated artifacts

| Platform | Portable application | Installer |
|---|---|---|
| macOS Apple Silicon | `RamPo-<version>-macOS-arm64.app.zip` | `RamPo-<version>-macOS-arm64.dmg` |
| macOS Intel | `RamPo-<version>-macOS-x86_64.app.zip` | `RamPo-<version>-macOS-x86_64.dmg` |
| Windows x64 | `RamPo-<version>-Windows-x64-portable.zip` | `RamPo-<version>-Windows-x64-Setup.exe` |

The version is read from the repository's root `version.py` file.

## GitHub Actions

The `Build desktop installers` workflow runs manually or whenever a `v*` tag
is pushed. It builds on native GitHub-hosted runners and retains the artifacts
for 30 days.

1. Open **Actions** in GitHub.
2. Select **Build desktop installers**.
3. Select **Run workflow**.
4. Download the three artifact groups after all jobs pass.

Unsigned Windows builds and ad-hoc-signed macOS builds are suitable for
testing. Public distribution should use the signing secrets described below.

## Local macOS build

Install the executable-build dependencies into `dev26a`:

```zsh
conda run -n dev26a python -m pip install -e ".[executable]"
```

Build the `.app.zip` and `.dmg`:

```zsh
conda run -n dev26a bash packaging/build_macos.sh
```

Without a Developer ID identity, PyInstaller applies an ad-hoc signature. This
is sufficient for local testing but not for normal public distribution through
Gatekeeper.

## Local Windows build

Install Inno Setup 6 or later, then install the Python build dependencies into
the Windows `dev26a` environment:

```powershell
conda run -n dev26a python -m pip install -e ".[executable]"
conda run -n dev26a powershell -ExecutionPolicy Bypass -File packaging\build_windows.ps1
```

The PowerShell script builds the PyInstaller directory, portable archive, and
Inno Setup installer.

## macOS signing and notarization

Configure these GitHub repository secrets to produce a Developer ID-signed and
notarized disk image:

| Secret | Purpose |
|---|---|
| `MACOS_CERTIFICATE` | Base64-encoded Developer ID Application `.p12` certificate |
| `MACOS_CERTIFICATE_PASSWORD` | Password for the `.p12` file |
| `MACOS_SIGNING_IDENTITY` | Full Developer ID Application identity name |
| `KEYCHAIN_PASSWORD` | Temporary CI keychain password |
| `APPLE_ID` | Apple developer account email |
| `APPLE_APP_PASSWORD` | App-specific password for `notarytool` |
| `APPLE_TEAM_ID` | Apple Developer team identifier |

The workflow imports the certificate into a temporary keychain. PyInstaller
signs the application bundle with the hardened runtime, and the build script
signs, submits, and staples the disk image. The temporary keychain is deleted
even if the build fails.

Validate a downloaded release on macOS with:

```zsh
codesign --verify --deep --strict --verbose=2 RamPo.app
spctl --assess --type execute --verbose=2 RamPo.app
xcrun stapler validate RamPo-<version>-macOS-<architecture>.dmg
```

## Windows code signing

Configure these secrets to sign both `RamPo.exe` and the Setup executable:

| Secret | Purpose |
|---|---|
| `WINDOWS_CERTIFICATE` | Base64-encoded code-signing `.pfx` certificate |
| `WINDOWS_CERTIFICATE_PASSWORD` | Password for the `.pfx` file |
| `WINDOWS_TIMESTAMP_URL` | Optional RFC 3161 timestamp URL |

If `WINDOWS_TIMESTAMP_URL` is omitted, the build uses DigiCert's public
timestamp service.

## Packaging files

- `RamPo.spec`: shared PyInstaller definition for both operating systems
- `rampo_launcher.py`: frozen-application entry point
- `build_macos.sh`: macOS application, archive, DMG, and notarization workflow
- `build_windows.ps1`: Windows application, archive, installer, and signing workflow
- `windows/RamPo.iss`: Inno Setup installer definition
- `macos/entitlements.plist`: minimal hardened-runtime entitlements
