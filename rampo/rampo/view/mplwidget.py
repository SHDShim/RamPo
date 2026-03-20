from qtpy import QtCore, QtWidgets
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from matplotlib.gridspec import GridSpec
import matplotlib.style as mplstyle


class MplCanvas(FigureCanvasQTAgg):
    """Matplotlib canvas used by PeakPo."""

    def __init__(self):
        self.fig = Figure()
        bbox = self.fig.get_window_extent().transformed(
            self.fig.dpi_scale_trans.inverted()
        )
        width, height = bbox.width * self.fig.dpi, bbox.height * self.fig.dpi

        self.fig.subplots_adjust(
            left=50 / width,
            bottom=30 / height,
            right=1 - 20 / width,
            top=1 - 30 / height,
            hspace=0.05,
        )

        self.bgColor = "#1e1f22"
        self.objColor = "#f0f0f0"
        self.gridColor = "#43464d"
        self.spineColor = "#c9c9c9"
        self.figureColor = "#2b2d31"
        self._define_axes(1)

        try:
            mplstyle.use("dark_background")
        except Exception:
            pass
        self._style_axes()

        super().__init__(self.fig)
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.updateGeometry()
        self.show_empty_state(draw=False)

    def _define_axes(self, h_ccd):
        self.gs = GridSpec(100, 1)
        self.ax_pattern = self.fig.add_subplot(self.gs[h_ccd + 1 : 99, 0])
        self.ax_ccd = self.fig.add_subplot(self.gs[0:h_ccd, 0], sharex=self.ax_pattern)
        self.ax_pattern.set_ylabel("Intensity (arbitrary unit)")
        self.ax_pattern.ticklabel_format(axis="y", style="sci", scilimits=(-2, 2))
        self.ax_pattern.get_yaxis().get_offset_text().set_position((-0.04, -0.14))
        self._style_axes()

    def _style_axis(self, axis):
        axis.set_facecolor(self.bgColor)
        axis.grid(False)
        axis.tick_params(colors=self.objColor)
        axis.xaxis.label.set_color(self.objColor)
        axis.yaxis.label.set_color(self.objColor)
        axis.title.set_color(self.objColor)
        axis.yaxis.get_offset_text().set_color(self.objColor)
        for spine in axis.spines.values():
            spine.set_color(self.spineColor)

    def _style_axes(self):
        self.fig.set_facecolor(self.figureColor)
        self.fig.set_edgecolor(self.figureColor)
        for axis in (self.ax_pattern, self.ax_ccd):
            self._style_axis(axis)

    def resize_axes(self, h_ccd):
        self.fig.clf()
        self._define_axes(h_ccd)
        if h_ccd == 1:
            self.ax_ccd.tick_params(axis="y", colors=self.objColor, labelleft=False)
            self.ax_ccd.spines["right"].set_visible(False)
            self.ax_ccd.spines["left"].set_visible(False)
            self.ax_ccd.spines["top"].set_visible(False)
            self.ax_ccd.spines["bottom"].set_visible(False)
        elif h_ccd >= 10:
            self.ax_ccd.set_ylabel("Azimuth (degrees)")
        self._style_axes()

    def set_toNight(self, NightView=True):
        if NightView:
            try:
                mplstyle.use("dark_background")
            except Exception:
                pass
            self.bgColor = "#1e1f22"
            self.objColor = "#f0f0f0"
            self.gridColor = "#43464d"
            self.spineColor = "#c9c9c9"
            self.figureColor = "#2b2d31"
        else:
            try:
                mplstyle.use("classic")
            except Exception:
                pass
            self.bgColor = "white"
            self.objColor = "black"
            self.gridColor = "#a8adb8"
            self.spineColor = "#606060"
            self.figureColor = "white"

        self._style_axes()
        self.ax_ccd.tick_params(
            which="both",
            axis="x",
            colors=self.objColor,
            direction="in",
            labelbottom=False,
            labeltop=False,
        )
        self.ax_ccd.tick_params(axis="x", which="both", length=0)
        self.ax_pattern.xaxis.set_label_position("bottom")

        try:
            self.draw_idle()
        except Exception:
            pass

    def show_empty_state(self, draw=True):
        self.fig.clf()
        self._define_axes(1)
        self.fig.set_facecolor(self.figureColor)
        self.fig.set_edgecolor(self.figureColor)
        for ax in (self.ax_pattern, self.ax_ccd):
            ax.clear()
            ax.set_facecolor(self.bgColor)
            ax.set_axis_off()
        if draw:
            try:
                self.draw_idle()
            except Exception:
                pass


class MplWidget(QtWidgets.QWidget):
    """Widget defined in Qt Designer."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.canvas = MplCanvas()
        self.canvas.setParent(self)
        self.canvas.setFocusPolicy(QtCore.Qt.ClickFocus)
        self.canvas.setFocus()

        self.vbl = QtWidgets.QVBoxLayout()
        self.vbl.setContentsMargins(0, 0, 0, 0)
        self.vbl.setSpacing(0)
        self.ntb = NavigationToolbar(self.canvas, self)
        self.control_bar = QtWidgets.QFrame(self)
        self.control_bar.setObjectName("plotMouseControlBar")
        self.control_bar.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.control_layout = QtWidgets.QHBoxLayout(self.control_bar)
        self.control_layout.setContentsMargins(8, 6, 8, 6)
        self.control_layout.setSpacing(8)
        self.control_bar.hide()
        self.setStyleSheet("MplWidget, QWidget { border: 0px; }")
        self.canvas.setStyleSheet("border: 0px;")
        self.ntb.setStyleSheet("border: 0px;")
        self.vbl.addWidget(self.ntb)
        self.vbl.addWidget(self.control_bar)
        self.vbl.addWidget(self.canvas)
        self.setLayout(self.vbl)
        self.ntb.hide()
        self._shutdown_done = False

    def add_control_widget(self, widget, stretch=0):
        if widget is None:
            return
        self.control_layout.addWidget(widget, stretch)
        self.control_bar.show()

    def add_control_stretch(self, stretch=1):
        self.control_layout.addStretch(stretch)
        self.control_bar.show()

    def insert_control_widget(self, index, widget, stretch=0):
        if widget is None:
            return
        self.control_layout.insertWidget(index, widget, stretch)
        self.control_bar.show()

    def shutdown(self):
        if self._shutdown_done:
            return
        self._shutdown_done = True

        try:
            if self.ntb is not None:
                self.ntb.hide()
                self.vbl.removeWidget(self.ntb)
                self.ntb.deleteLater()
                self.ntb = None
        except Exception:
            pass

        try:
            if self.canvas is not None and hasattr(self.canvas, "fig"):
                self.canvas.fig.clf()
        except Exception:
            pass

        try:
            if self.canvas is not None:
                self.canvas.hide()
                self.vbl.removeWidget(self.canvas)
                self.canvas.deleteLater()
                self.canvas = None
        except Exception:
            pass
