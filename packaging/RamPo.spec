"""Build a native RamPo application bundle with PyInstaller."""

import os
import re
import sys
from pathlib import Path

from PyInstaller.utils.hooks import collect_data_files


PROJECT_ROOT = Path(SPECPATH).parent
APP_NAME = "RamPo"
BUNDLE_ID = "org.shdshim.rampo"

version_namespace = {}
exec(
    compile(
        (PROJECT_ROOT / "version.py").read_text(encoding="utf-8"),
        str(PROJECT_ROOT / "version.py"),
        "exec",
    ),
    version_namespace,
)
APP_VERSION = version_namespace["__version__"]

is_macos = sys.platform == "darwin"
is_windows = sys.platform == "win32"
icon_path = PROJECT_ROOT / "rampo" / "rampo" / "assets"
icon_path /= "RamPo.icns" if is_macos else "RamPo.ico"

datas = collect_data_files(
    "rampo.rampo",
    includes=["assets/*", "mplstyle/*.mplstyle"],
)
binaries = []
hiddenimports = [
    "PyQt6.QtPrintSupport",
    "matplotlib.backends.backend_qtagg",
]

codesign_identity = os.environ.get("MACOS_SIGNING_IDENTITY") or None
entitlements_file = None
if is_macos and codesign_identity:
    entitlements_file = str(
        PROJECT_ROOT / "packaging" / "macos" / "entitlements.plist"
    )

version_file = None
if is_windows:
    numeric_version = [int(value) for value in re.findall(r"\d+", APP_VERSION)[:3]]
    numeric_version = (numeric_version + [0, 0, 0, 0])[:4]
    version_tuple = tuple(numeric_version)
    version_text = ".".join(str(value) for value in version_tuple)
    generated_dir = PROJECT_ROOT / "build" / "pyinstaller"
    generated_dir.mkdir(parents=True, exist_ok=True)
    version_file = generated_dir / "rampo-version-info.txt"
    version_file.write_text(
        f"""VSVersionInfo(
  ffi=FixedFileInfo(
    filevers={version_tuple},
    prodvers={version_tuple},
    mask=0x3f,
    flags=0x0,
    OS=0x40004,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
  ),
  kids=[
    StringFileInfo([
      StringTable(
        '040904B0',
        [StringStruct('CompanyName', 'S.-H. Dan Shim'),
         StringStruct('FileDescription', 'RamPo Raman spectroscopy analysis'),
         StringStruct('FileVersion', '{version_text}'),
         StringStruct('InternalName', 'RamPo'),
         StringStruct('LegalCopyright', 'GPL-3.0-only'),
         StringStruct('OriginalFilename', 'RamPo.exe'),
         StringStruct('ProductName', 'RamPo'),
         StringStruct('ProductVersion', '{APP_VERSION}')])
    ]),
    VarFileInfo([VarStruct('Translation', [1033, 1200])])
  ]
)\n""",
        encoding="utf-8",
    )

a = Analysis(
    [str(PROJECT_ROOT / "packaging" / "rampo_launcher.py")],
    pathex=[str(PROJECT_ROOT)],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["PySide6", "PyQt5", "tkinter"],
    noarchive=False,
    optimize=1,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name=APP_NAME,
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=codesign_identity,
    entitlements_file=entitlements_file,
    icon=str(icon_path),
    version=str(version_file) if version_file else None,
)

collection = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    name=APP_NAME,
)

if is_macos:
    app = BUNDLE(
        collection,
        name=f"{APP_NAME}.app",
        icon=str(icon_path),
        bundle_identifier=BUNDLE_ID,
        version=APP_VERSION,
        codesign_identity=codesign_identity,
        entitlements_file=entitlements_file,
        info_plist={
            "CFBundleDisplayName": APP_NAME,
            "CFBundleName": APP_NAME,
            "CFBundleShortVersionString": APP_VERSION,
            "CFBundleVersion": APP_VERSION,
            "LSMinimumSystemVersion": "12.0",
            "NSHighResolutionCapable": True,
            "NSPrincipalClass": "NSApplication",
        },
    )
