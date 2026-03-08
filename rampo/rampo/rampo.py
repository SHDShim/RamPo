import os
import sys
import faulthandler

if sys.platform == 'darwin':
    os.environ['MPLBACKEND'] = 'QtAgg'
    os.environ.setdefault('QT_OPENGL', 'software')
    os.environ.setdefault('QT_QUICK_BACKEND', 'software')

faulthandler.enable()

from qtpy.QtCore import Qt, QCoreApplication

if sys.platform == 'darwin':
    app_attr = getattr(Qt, "ApplicationAttribute", None)

    use_sw_gl = getattr(Qt, "AA_UseSoftwareOpenGL", None)
    if use_sw_gl is None and app_attr is not None:
        use_sw_gl = getattr(app_attr, "AA_UseSoftwareOpenGL", None)
    if use_sw_gl is not None:
        QCoreApplication.setAttribute(use_sw_gl, True)

    disable_hidpi = getattr(Qt, "AA_EnableHighDpiScaling", None)
    if disable_hidpi is None and app_attr is not None:
        disable_hidpi = getattr(app_attr, "AA_EnableHighDpiScaling", None)
    if disable_hidpi is not None:
        QCoreApplication.setAttribute(disable_hidpi, False)

import matplotlib
matplotlib.use('QtAgg')

from qtpy import QtWidgets
from qtpy.QtGui import QPalette, QColor

from io import StringIO
import traceback
import time
from sys import platform as _platform

app = QtWidgets.QApplication(sys.argv)
app.setStyle('Fusion')

if __package__ in (None, ""):
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    __package__ = "rampo"

from .utils import ErrorMessageBox
from .control import MainController


def excepthook(exc_type, exc_value, traceback_obj):
    try:
        error_msg = str(exc_value)
    except Exception:
        error_msg = repr(exc_value)

    painting_keywords = [
        'QPainter', 'QBackingStore', 'paint device',
        'drawRect', 'paintEvent', 'Painter not active',
        'TypeError: arguments did not match',
    ]

    if any(keyword in error_msg for keyword in painting_keywords):
        print("\nQt/Matplotlib painting error (suppressed GUI dialog):")
        print(f"  {error_msg}")
        traceback.print_exception(exc_type, exc_value, traceback_obj)
        return

    separator = '-' * 80
    log_file = "error.log"
    time_string = time.strftime("%Y-%m-%d, %H:%M:%S")
    tb_info_file = StringIO()
    traceback.print_tb(traceback_obj, None, tb_info_file)
    tb_info_file.seek(0)
    tb_info = tb_info_file.read()
    errmsg = '%s: \n%s' % (str(exc_type), str(exc_value))
    sections = [separator, time_string, separator, errmsg, separator, tb_info]
    msg = '\n'.join(sections)

    try:
        with open(log_file, "w") as f:
            f.write(msg)
    except IOError:
        pass

    errorbox = ErrorMessageBox()
    errorbox.setText(str(msg))
    errorbox.exec()


sys.excepthook = excepthook

def build_dark_palette():
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(40, 42, 46))
    palette.setColor(QPalette.WindowText, Qt.white)
    palette.setColor(QPalette.Base, QColor(26, 28, 31))
    palette.setColor(QPalette.AlternateBase, QColor(45, 48, 53))
    palette.setColor(QPalette.ToolTipBase, QColor(26, 28, 31))
    palette.setColor(QPalette.ToolTipText, Qt.white)
    palette.setColor(QPalette.Text, Qt.white)
    palette.setColor(QPalette.Button, QColor(52, 55, 61))
    palette.setColor(QPalette.ButtonText, Qt.white)
    palette.setColor(QPalette.BrightText, Qt.red)
    palette.setColor(QPalette.Link, QColor(88, 166, 255))
    palette.setColor(QPalette.Highlight, QColor(88, 166, 255))
    palette.setColor(QPalette.HighlightedText, QColor(20, 20, 20))
    palette.setColor(QPalette.Active, QPalette.Button, QColor(52, 55, 61))
    disabled = QColor(130, 130, 130)
    palette.setColor(QPalette.Disabled, QPalette.ButtonText, disabled)
    palette.setColor(QPalette.Disabled, QPalette.WindowText, disabled)
    palette.setColor(QPalette.Disabled, QPalette.Text, disabled)
    palette.setColor(QPalette.Disabled, QPalette.Light, QColor(52, 55, 61))
    return palette

app.setPalette(build_dark_palette())

controller = MainController()
controller.show_window()

_shutdown_done = {"value": False}


def _safe_shutdown():
    if _shutdown_done["value"]:
        return
    _shutdown_done["value"] = True
    try:
        controller.write_setting()
    except Exception:
        pass


app.aboutToQuit.connect(_safe_shutdown)

ret = app.exec()
if sys.platform == 'darwin':
    os._exit(ret)
else:
    sys.exit(ret)
