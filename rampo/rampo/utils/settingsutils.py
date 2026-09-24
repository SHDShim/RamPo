from qtpy import QtCore


SETTINGS_ORGANIZATION = "DS"
SETTINGS_APPLICATION = "RamPo"


def get_rampo_settings():
    """Return settings stored in RamPo's own application namespace."""
    return QtCore.QSettings(SETTINGS_ORGANIZATION, SETTINGS_APPLICATION)
