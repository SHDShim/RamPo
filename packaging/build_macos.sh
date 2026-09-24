#!/usr/bin/env bash

set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
project_root="$(cd "${script_dir}/.." && pwd)"
python_command="${PYTHON_COMMAND:-python}"

cd "${project_root}"

"${python_command}" -m PyInstaller --clean --noconfirm packaging/RamPo.spec

app_path="${project_root}/dist/RamPo.app"
if [[ ! -d "${app_path}" ]]; then
    echo "Expected application bundle not found: ${app_path}" >&2
    exit 1
fi

version="$("${python_command}" -c 'from version import __version__; print(__version__)')"
architecture="$(uname -m)"
artifact_dir="${project_root}/artifacts"
app_archive="${artifact_dir}/RamPo-${version}-macOS-${architecture}.app.zip"
dmg_path="${artifact_dir}/RamPo-${version}-macOS-${architecture}.dmg"
dmg_root="${project_root}/build/dmg-root"
dmg_temp_dir="$(mktemp -d "${TMPDIR:-/tmp}/rampo-dmg.XXXXXX")"
temporary_dmg="${dmg_temp_dir}/$(basename "${dmg_path}")"

cleanup() {
    rm -rf "${dmg_temp_dir}"
}
trap cleanup EXIT

mkdir -p "${artifact_dir}"
rm -rf "${dmg_root}"
mkdir -p "${dmg_root}"
cp -R "${app_path}" "${dmg_root}/RamPo.app"
ln -s /Applications "${dmg_root}/Applications"

codesign --verify --deep --strict --verbose=2 "${app_path}"
ditto -c -k --sequesterRsrc --keepParent "${app_path}" "${app_archive}"
hdiutil create \
    -volname "RamPo ${version}" \
    -srcfolder "${dmg_root}" \
    -ov \
    -format UDZO \
    "${temporary_dmg}"
mv -f "${temporary_dmg}" "${dmg_path}"

if [[ -n "${MACOS_SIGNING_IDENTITY:-}" ]]; then
    codesign --force --timestamp --sign "${MACOS_SIGNING_IDENTITY}" "${dmg_path}"
fi

if [[ -n "${APPLE_ID:-}" && -n "${APPLE_APP_PASSWORD:-}" && -n "${APPLE_TEAM_ID:-}" ]]; then
    xcrun notarytool submit "${dmg_path}" \
        --apple-id "${APPLE_ID}" \
        --password "${APPLE_APP_PASSWORD}" \
        --team-id "${APPLE_TEAM_ID}" \
        --wait
    xcrun stapler staple "${dmg_path}"
    xcrun stapler validate "${dmg_path}"
fi

echo "Created ${app_archive}"
echo "Created ${dmg_path}"
