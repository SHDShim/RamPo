import os

from qtpy import QtCore

from rampo.rampo.utils.fileutils import get_valid_start_directory
from rampo.rampo.utils.settingsutils import get_rampo_settings


def test_valid_start_directory_keeps_existing_directory(tmp_path):
    expected = tmp_path / "data"
    expected.mkdir()

    assert get_valid_start_directory(expected) == str(expected)


def test_valid_start_directory_uses_parent_for_file(tmp_path):
    selected_file = tmp_path / "sample.spe"
    selected_file.write_text("", encoding="utf-8")

    assert get_valid_start_directory(selected_file) == str(tmp_path)


def test_valid_start_directory_replaces_stale_path(tmp_path):
    fallback = tmp_path / "fallback"
    fallback.mkdir()

    result = get_valid_start_directory(
        tmp_path / "removed-folder", fallback=fallback)

    assert result == str(fallback)
    assert os.path.isdir(result)


def test_settings_use_rampo_namespace(monkeypatch):
    calls = []

    def fake_settings(organization, application):
        calls.append((organization, application))
        return object()

    monkeypatch.setattr(QtCore, "QSettings", fake_settings)

    get_rampo_settings()

    assert calls == [("DS", "RamPo")]
