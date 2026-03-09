import os


_REQUIRED_QT_API = "pyqt6"


def enforce_pyqt6():
    current = os.environ.get("QT_API")
    if current and current.lower() != _REQUIRED_QT_API:
        raise RuntimeError(
            f"RamPo requires QT_API={_REQUIRED_QT_API}, got {current!r}."
        )
    os.environ["QT_API"] = _REQUIRED_QT_API

