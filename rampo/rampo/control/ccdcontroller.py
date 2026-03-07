import os
import glob
from qtpy import QtWidgets
import numpy as np
from matplotlib.widgets import RectangleSelector
from ..utils import get_temp_dir, extract_extension, InformationBox
from .mplcontroller import MplController
from .ccdprocesscontroller import CCDProcessController
from PIL import Image
import json
import datetime

class CCDController(object):

    def __init__(self, model, widget):
        self.model = model
        self.widget = widget
        self.ccdprocess_ctrl = CCDProcessController(self.model, self.widget)
        self.plot_ctrl = MplController(self.model, self.widget)
        self._row_roi_selector = None
        self.connect_channel()

    def connect_channel(self):
        self.widget.pushButton_Info.clicked.connect(self.show_tif_header)
        self.widget.checkBox_ShowCake.clicked.connect(
            self.addremove_cake)
        self.widget.pushButton_ApplyCakeView.clicked.connect(self.update_cake)
        self.widget.pushButton_ApplyMask.clicked.connect(self.apply_mask)
        self.widget.pushButton_MaskReset.clicked.connect(self.reset_maskrange)
        self.widget.pushButton_ResetCakeScale.clicked.connect(
            self.reset_max_cake_scale)
        if hasattr(self.widget, "spinBox_CCDRowMin"):
            self.widget.spinBox_CCDRowMin.valueChanged.connect(
                self._on_row_roi_spin_changed)
        if hasattr(self.widget, "spinBox_CCDRowMax"):
            self.widget.spinBox_CCDRowMax.valueChanged.connect(
                self._on_row_roi_spin_changed)
        if hasattr(self.widget, "pushButton_CCDSelectRoi"):
            self.widget.pushButton_CCDSelectRoi.clicked.connect(
                self._toggle_row_roi_selector)
        if hasattr(self.widget, "pushButton_CCDFullRoi"):
            self.widget.pushButton_CCDFullRoi.clicked.connect(
                self._reset_row_roi_to_full)
        if hasattr(self.widget, "comboBox_CakeColormap"):
            self.widget.comboBox_CakeColormap.currentIndexChanged.connect(
                self._apply_changes_to_graph)
        if hasattr(self.widget, "cake_hist_widget"):
            self.widget.cake_hist_widget.boundChanged.connect(
                self._set_cake_bound_from_hist)
        """
        self.widget.pushButton_Load_CakeFormatFile.clicked.connect(
            self.load_cake_format_file)
        self.widget.pushButton_Save_CakeFormatFile.clicked.connect(
            self.save_cake_format_file)
        """

    def update_cake(self):
        if not self.model.base_ptn_exist():
            QtWidgets.QMessageBox.warning(
                self.widget, 'Warning', 'Choose a spectrum file first.')
            return
        if (not self._is_spe_source()) and (not self.model.associated_image_exists()):
            self._set_image_file_box_missing()
            QtWidgets.QMessageBox.warning(
                self.widget, 'Warning',
                'CCD image file does not exist in the spectrum folder.\n'
                'Move the image file into the same folder as the spectrum first.')
            return

        success = self.produce_cake()
        if not success:
            return
        temp_dir = get_temp_dir(self.model.get_base_ptn_filename())
        self.model.diff_img.write_temp_cakefiles(temp_dir=temp_dir)
        self._set_image_file_box()
        self._apply_changes_to_graph()

    def _set_row_roi_spin_limits(self):
        if (not hasattr(self.widget, "spinBox_CCDRowMin")) or \
                (not self.model.diff_img_exist()):
            return
        img = getattr(self.model.diff_img, "img", None)
        if img is None or np.ndim(img) < 2 or img.shape[0] <= 0:
            return
        n_rows = int(img.shape[0])
        for box in (self.widget.spinBox_CCDRowMin, self.widget.spinBox_CCDRowMax):
            box.blockSignals(True)
            box.setMaximum(n_rows - 1)
            box.blockSignals(False)
        current = getattr(self.model.base_ptn, "row_roi", None)
        if current is None:
            current = (0, n_rows - 1)
        row_min = max(0, min(int(current[0]), n_rows - 1))
        row_max = max(0, min(int(current[1]), n_rows - 1))
        if row_max < row_min:
            row_min, row_max = row_max, row_min
        self.widget.spinBox_CCDRowMin.blockSignals(True)
        self.widget.spinBox_CCDRowMax.blockSignals(True)
        self.widget.spinBox_CCDRowMin.setValue(row_min)
        self.widget.spinBox_CCDRowMax.setValue(row_max)
        self.widget.spinBox_CCDRowMin.blockSignals(False)
        self.widget.spinBox_CCDRowMax.blockSignals(False)

    def _apply_row_roi_to_spectrum(self):
        if (not self.model.base_ptn_exist()) or \
                (extract_extension(str(self.model.get_base_ptn_filename())).lower() != 'spe'):
            return
        if (not hasattr(self.widget, "spinBox_CCDRowMin")) or \
                (getattr(self.model.base_ptn, "raw_image", None) is None):
            return
        row_min = int(self.widget.spinBox_CCDRowMin.value())
        row_max = int(self.widget.spinBox_CCDRowMax.value())
        if row_max < row_min:
            row_min, row_max = row_max, row_min
            self.widget.spinBox_CCDRowMin.blockSignals(True)
            self.widget.spinBox_CCDRowMax.blockSignals(True)
            self.widget.spinBox_CCDRowMin.setValue(row_min)
            self.widget.spinBox_CCDRowMax.setValue(row_max)
            self.widget.spinBox_CCDRowMin.blockSignals(False)
            self.widget.spinBox_CCDRowMax.blockSignals(False)
        success = self.model.base_ptn.set_spe_row_roi(row_min, row_max)
        if not success:
            return
        self._refresh_bgsub_for_current_spectrum()
        self._apply_changes_to_graph()

    def _refresh_bgsub_for_current_spectrum(self):
        if not self.model.base_ptn_exist():
            return
        x_raw, __ = self.model.base_ptn.get_raw()
        if x_raw is None or len(x_raw) == 0:
            return
        roi_min = float(self.widget.doubleSpinBox_Background_ROI_min.value())
        roi_max = float(self.widget.doubleSpinBox_Background_ROI_max.value())
        if (x_raw.min() >= roi_min) or (x_raw.max() <= roi_min):
            roi_min = float(x_raw.min())
            self.widget.doubleSpinBox_Background_ROI_min.setValue(roi_min)
        if (x_raw.max() <= roi_max) or (x_raw.min() >= roi_max):
            roi_max = float(x_raw.max())
            self.widget.doubleSpinBox_Background_ROI_max.setValue(roi_max)
        params = [
            int(self.widget.spinBox_BGParam0.value()),
            int(self.widget.spinBox_BGParam1.value()),
            int(self.widget.spinBox_BGParam2.value()),
        ]
        self.model.base_ptn.get_chbg([roi_min, roi_max], params, yshift=0)

    def _on_row_roi_spin_changed(self, value):
        del value
        self._apply_row_roi_to_spectrum()

    def _toggle_row_roi_selector(self, checked):
        if checked:
            self._activate_row_roi_selector()
        else:
            self._deactivate_row_roi_selector()

    def _activate_row_roi_selector(self):
        if not self.model.diff_img_exist():
            self.widget.pushButton_CCDSelectRoi.setChecked(False)
            return
        if not hasattr(self.widget.mpl.canvas, "ax_cake"):
            self.widget.pushButton_CCDSelectRoi.setChecked(False)
            return
        self._deactivate_row_roi_selector()
        self._row_roi_selector = RectangleSelector(
            self.widget.mpl.canvas.ax_cake,
            self._on_row_roi_selected,
            useblit=True,
            button=[1],
            interactive=False,
            drag_from_anywhere=False,
        )

    def _deactivate_row_roi_selector(self):
        if self._row_roi_selector is not None:
            try:
                self._row_roi_selector.set_active(False)
            except Exception:
                pass
            self._row_roi_selector = None
        if hasattr(self.widget, "pushButton_CCDSelectRoi"):
            self.widget.pushButton_CCDSelectRoi.blockSignals(True)
            self.widget.pushButton_CCDSelectRoi.setChecked(False)
            self.widget.pushButton_CCDSelectRoi.blockSignals(False)

    def _on_row_roi_selected(self, eclick, erelease):
        if (eclick.ydata is None) or (erelease.ydata is None):
            self._deactivate_row_roi_selector()
            return
        img = getattr(self.model.diff_img, "img", None)
        if img is None or np.ndim(img) < 2:
            self._deactivate_row_roi_selector()
            return
        ymin = int(np.floor(min(float(eclick.ydata), float(erelease.ydata))))
        ymax = int(np.ceil(max(float(eclick.ydata), float(erelease.ydata))))
        ymax = max(ymin, ymax - 1)
        n_rows = int(img.shape[0])
        ymin = max(0, min(ymin, n_rows - 1))
        ymax = max(0, min(ymax, n_rows - 1))
        self.widget.spinBox_CCDRowMin.blockSignals(True)
        self.widget.spinBox_CCDRowMax.blockSignals(True)
        self.widget.spinBox_CCDRowMin.setValue(ymin)
        self.widget.spinBox_CCDRowMax.setValue(ymax)
        self.widget.spinBox_CCDRowMin.blockSignals(False)
        self.widget.spinBox_CCDRowMax.blockSignals(False)
        self._apply_row_roi_to_spectrum()
        self._deactivate_row_roi_selector()

    def _reset_row_roi_to_full(self):
        img = getattr(getattr(self.model, "diff_img", None), "img", None)
        if img is None or np.ndim(img) < 2 or img.shape[0] <= 0:
            return
        self.widget.spinBox_CCDRowMin.blockSignals(True)
        self.widget.spinBox_CCDRowMax.blockSignals(True)
        self.widget.spinBox_CCDRowMin.setValue(0)
        self.widget.spinBox_CCDRowMax.setValue(int(img.shape[0] - 1))
        self.widget.spinBox_CCDRowMin.blockSignals(False)
        self.widget.spinBox_CCDRowMax.blockSignals(False)
        self._apply_row_roi_to_spectrum()

    """
    def load_cake_format_file(self):
        # get filename
        temp_dir = get_temp_dir(self.model.get_base_ptn_filename())
        filen = QtWidgets.QFileDialog.getOpenFileName(
            self.widget, "Open a cake format File", temp_dir,  # self.model.chi_path,
            "Data files (*.cakeformat)")[0]
        if filen == '':
            return
        temp_values = []
        with open(filen, "r") as f:
            for line in f:
                temp_values.append(float(line.split(':')[1]))
        self.widget.spinBox_AziShift.setValue(temp_values[0])
        self.widget.spinBox_MaxCakeScale.setValue(temp_values[1])
        self.widget.horizontalSlider_VMin.setValue(temp_values[2])
        self.widget.horizontalSlider_VMax.setValue(temp_values[3])
        self.widget.horizontalSlider_MaxScaleBars.setValue(temp_values[4])
        self._apply_changes_to_graph()

    def save_cake_format_file(self):
        # make filename
        temp_dir = get_temp_dir(self.model.get_base_ptn_filename())
        ext = "cakeformat"
        #filen_t = self.model.make_filename(ext)
        filen_t = make_filename(self.model.base_ptn.fname, ext,
                                temp_dir=temp_dir)
        filen = dialog_savefile(self.widget, filen_t)
        if str(filen) == '':
            return
        # save cake related Values
        names = ['azi_shift', 'int_max', 'min_bar', 'max_bar', 'scale_bar']
        values = [self.widget.spinBox_AziShift.value(),
                  self.widget.spinBox_MaxCakeScale.value(),
                  self.widget.horizontalSlider_VMin.value(),
                  self.widget.horizontalSlider_VMax.value(),
                  self.widget.horizontalSlider_MaxScaleBars.value()]

        with open(filen, "w") as f:
            for n, v in zip(names, values):
                f.write(n + ' : ' + str(v) + '\n')
    """

    def reset_max_cake_scale(self):
        if hasattr(self.widget, "checkBox_Diff") and self.widget.checkBox_Diff.isChecked():
            return
        intensity_cake, _, _ = self.model.diff_img.get_cake()
        self.widget.spinBox_MaxCakeScale.setValue(int(intensity_cake.max()))
        self._apply_changes_to_graph()

    def _apply_changes_to_graph(self):
        self.plot_ctrl.update()

    def _set_cake_bound_from_hist(self, bound_type, intensity_value):
        prefactor = self.widget.spinBox_MaxCakeScale.value() / \
            (10. ** self.widget.horizontalSlider_MaxScaleBars.value())
        if prefactor <= 0:
            return
        current_min = self.widget.horizontalSlider_VMin.value()
        current_max = self.widget.horizontalSlider_VMax.value()
        slider_value = int(np.clip(round(intensity_value / prefactor * 100.0), 0, 1000))
        if bound_type == "min":
            if slider_value == current_min:
                current_min_intensity = current_min / 100.0 * prefactor
                if intensity_value < current_min_intensity:
                    slider_value = max(0, current_min - 1)
                elif intensity_value > current_min_intensity:
                    slider_value = min(999, current_min + 1)
            if slider_value >= current_max:
                slider_value = max(0, current_max - 1)
            self.widget.horizontalSlider_VMin.setValue(slider_value)
        elif bound_type == "max":
            if slider_value == current_max:
                current_max_intensity = current_max / 100.0 * prefactor
                if intensity_value < current_max_intensity:
                    slider_value = max(1, current_max - 1)
                elif intensity_value > current_max_intensity:
                    slider_value = min(1000, current_max + 1)
            if slider_value <= current_min:
                slider_value = min(1000, current_min + 1)
            self.widget.horizontalSlider_VMax.setValue(slider_value)

    def _ignore_raw_data_missing(self):
        return self.widget.checkBox_IgnoreRawDataExistence.isChecked()

    def _set_image_file_box_missing(self):
        self.widget.textEdit_DiffractionImageFilename.setText(
            'CCD image file is missing. Move the image file into the same folder as the spectrum.')

    def _set_image_file_box(self):
        if self.model.diff_img_exist() and (self.model.diff_img.img_filename is not None):
            self.widget.textEdit_DiffractionImageFilename.setText(
                self.model.diff_img.img_filename)
        else:
            self._set_image_file_box_missing()

    def _warn_cannot_process_cake(self):
        QtWidgets.QMessageBox.warning(
            self.widget, 'Warning',
            'Rampo cannot process the CCD view: no image data and no cached CCD files were found.')

    def _load_cake_from_temp_without_raw_image(self, temp_dir):
        # Temp cake files are named from the base pattern root name.
        if self.model.diff_img is None:
            self.model.reset_diff_img()
        self.model.diff_img.img_filename = self.model.make_filename(
            'tif', original=True)
        return self.model.diff_img.read_cake_from_tempfile(temp_dir=temp_dir)

    def show_tif_header(self):
        if not self.model.base_ptn_exist():
            return
        filen_tif = self.model.make_filename('tif', original=True)
        filen_tiff = self.model.make_filename('tiff', original=True)
        if not (os.path.exists(filen_tif) or
                os.path.exists(filen_tiff)):
            QtWidgets.QMessageBox.warning(
                self.widget, 'Warning',
                'Cannot find image file: %s or %s in the chi folder.' %
                (filen_tif, filen_tiff))
        else:
            textoutput = ''
            if os.path.exists(filen_tif):
                f = filen_tif
            else:
                f = filen_tiff
            metadata = {}
            with Image.open(f) as img:
                for key in img.tag:
                    metadata[key] = img.tag[key]
            infobox = InformationBox()
            infobox.setText(json.dumps(metadata, indent=4))
            print(str(datetime.datetime.now())[:-7], ': TIF metadata\n', 
                json.dumps(metadata, indent=4))
            infobox.exec()
            #self.widget.plainTextEdit_ViewJCPDS.setPlainText(textoutput)


    def addremove_cake(self):
        """
        add / remove cake to the graph
        """
        update = self._addremove_cake()
        if update:
            self._apply_changes_to_graph()
    """
    def image_file_exists(self):
        # if no image file, no cake
        filen_tif = self.model.make_filename('tif', original=True)
        filen_tiff = self.model.make_filename('tiff', original=True)
        filen_mar3450 = self.model.make_filename('mar3450',
            original=True)
        filen_cbf = self.model.make_filename('cbf', original=True)
        filen_h5 = self.model.make_filename('h5', original=True)
        if not (os.path.exists(filen_tif) or
                os.path.exists(filen_tiff) or
                os.path.exists(filen_mar3450) or
                os.path.exists(filen_h5) or
                os.path.exists(filen_cbf)):
            return False
        else:
            return True
    """

    def _addremove_cake(self):
        """
        add / remove cake
        no signal to update_graph
        """
        if not self.widget.checkBox_ShowCake.isChecked():
            return True
        # if no base ptn, no cake
        if not self.model.base_ptn_exist():
            QtWidgets.QMessageBox.warning(
                self.widget, 'Warning', 'Choose a spectrum file first.')
            self.widget.checkBox_ShowCake.setChecked(False)
            return False
        if self._is_spe_source():
            if not self.process_temp_cake():
                self.widget.checkBox_ShowCake.setChecked(False)
                return False
            return True
        if not self.model.associated_image_exists():
            if not self._ignore_raw_data_missing():
                self._set_image_file_box_missing()
                QtWidgets.QMessageBox.warning(
                    self.widget, 'Warning',
                    'Cannot find CCD image file.')
                self.widget.checkBox_ShowCake.setChecked(False)
                return False
            if not self.process_temp_cake():
                self._warn_cannot_process_cake()
                self.widget.checkBox_ShowCake.setChecked(False)
                return False
            return True

        if not self.process_temp_cake():
            self._warn_cannot_process_cake()
            self.widget.checkBox_ShowCake.setChecked(False)
            return False
        return True

    def _load_new_image(self):
        """
        Load new image for cake view.  Cake should be the same as base pattern.
        no signal to update_graph
        """
        self.model.reset_diff_img()
        if not self.model.associated_image_exists():
            self._set_image_file_box_missing()
            return False
        self.model.load_associated_img()
        self._set_image_file_box()
        return True

    def _is_spe_source(self):
        if not self.model.base_ptn_exist():
            return False
        return extract_extension(str(self.model.get_base_ptn_filename())).lower() == 'spe'

    def apply_mask(self):
        # self.produce_cake()
        min_mask = float(self.widget.spinBox_MaskMin.value())
        max_mask = float(self.widget.spinBox_MaskMax.value())
        zrange = self.model.diff_img.get_img_zrange()
        print('img z range', zrange)
        print('mask range', min_mask, max_mask)
        if (zrange[0] < min_mask) or (zrange[1] > max_mask):
            # case for meaningful mask
            if self.widget.pushButton_ApplyMask.isChecked():
                self.ccdprocess_ctrl.cook()
        else:
            self.model.diff_img.set_mask(None)
        self._apply_changes_to_graph()

    def reset_maskrange(self):
        # get min and max of the cake image
        #intensity_cake, _, _ = self.model.diff_img.get_cake()
        zrange = self.model.diff_img.get_img_zrange()
        if zrange != None:
            # push those values to spinboxes
            self.widget.spinBox_MaskMin.setValue(int(zrange[0]))
            self.widget.spinBox_MaskMax.setValue(int(zrange[1]))
            self.model.diff_img.set_mask(None)
            self._apply_changes_to_graph()
        # reprocess the image
        # self.apply_mask()

    def produce_cake(self):
        """
        Reprocess to get cake.  Slower re - processing
        does not signal to update_graph
        """
        success = self._load_new_image()
        if not success:
            return False
        self._set_row_roi_spin_limits()
        self.ccdprocess_ctrl.cook()
        self._apply_row_roi_to_spectrum()
        self._set_image_file_box()
        return True

    def process_temp_cake(self):
        """
        load cake through either temporary file or make a new cake
        """
        temp_dir = get_temp_dir(self.model.get_base_ptn_filename())
        if self._is_spe_source():
            success = self._load_new_image()
            if not success:
                return False
            self._set_row_roi_spin_limits()
            self._apply_row_roi_to_spectrum()
            self.model.diff_img.write_temp_cakefiles(temp_dir=temp_dir)
            return True
        has_raw_image = self.model.associated_image_exists()
        if not has_raw_image:
            self._set_image_file_box_missing()
            if not self._ignore_raw_data_missing():
                QtWidgets.QMessageBox.warning(
                    self.widget, "Warning",
                    "Image file for the base pattern does not exist.")
                return False
            return self._load_cake_from_temp_without_raw_image(temp_dir)
        #temp_dir = os.path.join(self.model.chi_path, 'temporary_pkpo')
        if self.widget.checkBox_UseTempCake.isChecked():
            #if os.path.exists(temp_dir):
            success = self._load_new_image()
            if not success:
                return False
            success = self.model.diff_img.read_cake_from_tempfile(
                temp_dir=temp_dir)
            if success:
                print(str(datetime.datetime.now())[:-7], 
                    ": Load cake image from temporary file.")
                pass
            else:
                print(str(datetime.datetime.now())[:-7], 
                    ": Create new temporary file for cake image.")
                self._update_temp_cake_files(temp_dir)
                return True
            #else:
                #os.makedirs(temp_dir)
                #self._update_temp_cake_files(temp_dir)
            return True
        else:
            self._update_temp_cake_files(temp_dir)
            return True

    def _update_temp_cake_files(self, temp_dir):
        success = self.produce_cake()
        if not success:
            return
        self.model.diff_img.write_temp_cakefiles(temp_dir=temp_dir)

    def temp_cake_exists(self):
        temp_dir = get_temp_dir(self.model.get_base_ptn_filename())
        search_pattern = os.path.join(temp_dir, "*.cake.npy")
        cake_all = glob.glob(search_pattern)
        print(len(cake_all))
        if len(cake_all) < 3:
            return False
        else:
            return True


CakeController = CCDController
