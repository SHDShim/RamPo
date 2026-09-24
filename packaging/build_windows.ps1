param(
    [string]$PythonCommand = "python"
)

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $ProjectRoot

function Invoke-CodeSigning {
    param([Parameter(Mandatory = $true)][string]$Path)

    if (-not $env:WINDOWS_CERTIFICATE_PATH) {
        return
    }

    $SignToolCommand = Get-Command "signtool.exe" -ErrorAction SilentlyContinue
    if ($null -ne $SignToolCommand) {
        $SignToolPath = $SignToolCommand.Source
    } else {
        $KitsBin = "${env:ProgramFiles(x86)}\Windows Kits\10\bin"
        $SignToolPath = Get-ChildItem $KitsBin -Filter "signtool.exe" -Recurse |
            Where-Object { $_.FullName -match '\\x64\\signtool\.exe$' } |
            Sort-Object FullName -Descending |
            Select-Object -First 1 -ExpandProperty FullName
    }

    if (-not $SignToolPath) {
        throw "signtool.exe was not found."
    }

    $TimestampUrl = if ($env:WINDOWS_TIMESTAMP_URL) {
        $env:WINDOWS_TIMESTAMP_URL
    } else {
        "http://timestamp.digicert.com"
    }
    & $SignToolPath sign /fd SHA256 /f $env:WINDOWS_CERTIFICATE_PATH `
        /p $env:WINDOWS_CERTIFICATE_PASSWORD /tr $TimestampUrl /td SHA256 $Path
    if ($LASTEXITCODE -ne 0) {
        throw "Code signing failed for $Path"
    }
}

& $PythonCommand -m PyInstaller --clean --noconfirm packaging/RamPo.spec
if ($LASTEXITCODE -ne 0) {
    throw "PyInstaller failed with exit code $LASTEXITCODE"
}

$Executable = Join-Path $ProjectRoot "dist\RamPo\RamPo.exe"
if (-not (Test-Path $Executable)) {
    throw "Expected executable not found: $Executable"
}
Invoke-CodeSigning -Path $Executable

$Version = (& $PythonCommand -c "from version import __version__; print(__version__)").Trim()
$ArtifactDir = Join-Path $ProjectRoot "artifacts"
$PortableArchive = Join-Path $ArtifactDir "RamPo-$Version-Windows-x64-portable.zip"
New-Item -ItemType Directory -Force -Path $ArtifactDir | Out-Null
if (Test-Path $PortableArchive) {
    Remove-Item -Force $PortableArchive
}
Compress-Archive -Path (Join-Path $ProjectRoot "dist\RamPo") -DestinationPath $PortableArchive

$IsccCommand = Get-Command "ISCC.exe" -ErrorAction SilentlyContinue
if ($null -eq $IsccCommand) {
    $Candidates = @(
        "${env:ProgramFiles(x86)}\Inno Setup 6\ISCC.exe",
        "${env:ProgramFiles}\Inno Setup 6\ISCC.exe",
        "${env:ProgramFiles}\Inno Setup 7\ISCC.exe"
    )
    $IsccPath = $Candidates | Where-Object { Test-Path $_ } | Select-Object -First 1
} else {
    $IsccPath = $IsccCommand.Source
}

if (-not $IsccPath) {
    throw "ISCC.exe was not found. Install Inno Setup 6 or later."
}

& $IsccPath "/DMyAppVersion=$Version" "packaging\windows\RamPo.iss"
if ($LASTEXITCODE -ne 0) {
    throw "Inno Setup failed with exit code $LASTEXITCODE"
}

$Installer = Join-Path $ArtifactDir "RamPo-$Version-Windows-x64-Setup.exe"
if (-not (Test-Path $Installer)) {
    throw "Expected installer not found: $Installer"
}
Invoke-CodeSigning -Path $Installer

Write-Host "Created $PortableArchive"
Write-Host "Created $Installer"
