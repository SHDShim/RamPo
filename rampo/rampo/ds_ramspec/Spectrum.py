import numpy as np
import os
import time
import datetime
from ..utils import writechi, readchi, make_filename
from ..model.SpeFile import SpeFile
from .background import fit_bg_cheb_auto


class Spectrum(object):
    """
    This modified from the same object in ds_* modules
    """

    def __init__(self, filename=None):
        if filename is None:
            self.x_raw = None
            self.y_raw = None
            self.raw_image = None
            self.row_roi = None
        else:
            self.fname = filename
            self.read_file(filename)
        self.x_bgsub = None
        self.y_bgsub = None
        self.x_bg = None
        self.y_bg = None
        self.params_chbg = [20, 10, 20]

    def read_file(self, fname):
        """
        read a Raman/XRD pattern and get raw xy
        """
        ext = os.path.splitext(fname)[1].lower()
        self.raw_image = None
        if ext == '.chi':
            data = np.loadtxt(fname, skiprows=4)
            twotheta, intensity = data.T
        elif ext == '.spe':
            spe = SpeFile(fname)
            raw_image = spe.img[0] if isinstance(spe.img, list) else spe.img
            raw_image = np.asarray(raw_image, dtype=float)
            if raw_image.ndim == 1:
                intensity = raw_image
            elif raw_image.shape[0] == 1:
                intensity = raw_image[0]
            else:
                raw_image = raw_image[::-1]
                intensity = np.nansum(raw_image, axis=0)
            twotheta = np.asarray(spe.x_calibration, dtype=float)
            self.raw_image = raw_image
            if raw_image is None or np.ndim(raw_image) < 2:
                self.row_roi = None
            else:
                self.row_roi = (0, int(raw_image.shape[0] - 1))
        else:
            raise ValueError('Only support CHI and SPE formats')
        # set file name information
        self.fname = fname

        self.x_raw = twotheta
        self.y_raw = intensity

    def set_spe_row_roi(self, row_min=None, row_max=None):
        if self.raw_image is None or np.ndim(self.raw_image) < 2:
            return False
        n_rows = int(self.raw_image.shape[0])
        if n_rows <= 0:
            return False
        if row_min is None:
            row_min = 0
        if row_max is None:
            row_max = n_rows - 1
        row_min = max(0, min(int(row_min), n_rows - 1))
        row_max = max(0, min(int(row_max), n_rows - 1))
        if row_max < row_min:
            row_min, row_max = row_max, row_min
        self.row_roi = (row_min, row_max)
        self.y_raw = np.nansum(self.raw_image[row_min:row_max + 1, :], axis=0)
        return True

    def _get_section(self, x, y, roi):
        if roi[0] >= x.min() and roi[1] <= x.max():
            i_roimin = np.abs(x - roi[0]).argmin()
            i_roimax = np.abs(x - roi[1]).argmin()
            x_roi = x[i_roimin:i_roimax]
            y_roi = y[i_roimin:i_roimax]
            return x_roi, y_roi
        else:
            print(str(datetime.datetime.now())[:-7], 
                ": Error: ROI should be smaller than the data range")
            return x, y

    def get_section(self, roi, bgsub=True):
        """
        return a section for viewing and processing
        """
        if bgsub:
            return self._get_section(self.x_bgsub, self.y_bgsub, roi)
        else:
            return self._get_section(self.x_raw, self.y_raw, roi)

    def _get_bg(self, roi, params=None, yshift=0.):
        if params is not None:
            self.params_chbg = params
        x, y = self._get_section(self.x_raw, self.y_raw, roi)
        t_start = time.time()
        y_bg = fit_bg_cheb_auto(x, y, self.params_chbg[0],
                                self.params_chbg[1], self.params_chbg[2])
        print(str(datetime.datetime.now())[:-7], 
            ": Bgsub takes {0:.2f}s".format(time.time() - t_start))
        self.x_bg = x
        self.x_bgsub = x
        y_bgsub = y - y_bg
        """
        if y_bgsub.min() <= 0:
            y_bgsub = y_bgsub - y_bgsub.min() + yshift
        """
        self.y_bgsub = y_bgsub
        self.y_bg = y_bg
        self.roi = roi

    def subtract_bg(self, roi, params=None, yshift=10.):
        print(str(datetime.datetime.now())[:-7], ": Receive BG subtraction")
        self._get_bg(roi, params=params, yshift=yshift)

    def get_raw(self):
        return self.x_raw, self.y_raw

    def get_background(self):
        return self.x_bg, self.y_bg

    def get_bgsub(self):
        return self.x_bgsub, self.y_bgsub

    def get_bg(self):
        return self.x_bg, self.y_bg

    def set_bg(self, x_bg, y_bg, x_bgsub, y_bgsub, roi, bg_params):
        self.x_bg = x_bg
        self.y_bg = y_bg
        self.x_bgsub = x_bgsub
        self.y_bgsub = y_bgsub
        self.roi = roi
        self.params_chbg = bg_params

    def get_chbg(self, roi, params=None, chiout=False, yshift=10.):
        """
        subtract background from raw data for a roi and then store in
        chbg xy
        """
        self._get_bg(roi, params=params, yshift=yshift)

        if chiout:
            # write background file
            f_bg = os.path.splitext(self.fname)[0] + '.bg.chi'
            text = "Background\n" + "2-theta, CHEB BG:" + \
                ' '.join(map(str, self.params_chbg)) + "\n\n"
            writechi(f_bg, self.x_bgsub, self.y_bg, preheader=text)
            # write background subtracted file
            f_bgsub = os.path.splitext(self.fname)[0] + '.bgsub.chi'
            text = "Background subtracted diffraction pattern\n" + \
                "2-theta, CHEB BG:" + ' '.join(map(str, self.params_chbg)) + "\n\n"
            writechi(f_bgsub, self.x_bgsub, self.y_bgsub, preheader=text)

    def read_bg_from_tempfile(self, temp_dir=None):
        bgsub_filen, bg_filen = self.make_temp_filenames(temp_dir=temp_dir)
        if os.path.exists(bgsub_filen) and os.path.exists(bg_filen):
            roi, bg_params, x_bgsub, y_bgsub = readchi(bgsub_filen)
            __, __, x_bg, y_bg = readchi(bg_filen)
            self.set_bg(x_bg, y_bg, x_bgsub, y_bgsub, roi, bg_params)
            return True
        else:
            return False

    def make_temp_filenames(self, temp_dir=None):
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)
        bgsub_filen = make_filename(self.fname, 'bgsub.chi',
                                    temp_dir=temp_dir)
        bg_filen = make_filename(self.fname, 'bg.chi',
                                 temp_dir=temp_dir)
        return bgsub_filen, bg_filen

    def temp_files_exist(self, temp_dir=None):
        bgsub_filen, bg_filen = self.make_temp_filenames(temp_dir=temp_dir)
        if os.path.exists(bgsub_filen) and os.path.exists(bg_filen):
            return True
        else:
            return False

    def write_temporary_bgfiles(self, temp_dir):
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)
        bgsub_filen, bg_filen = self.make_temp_filenames(temp_dir=temp_dir)
        x_bgsub, y_bgsub = self.get_bgsub()
        x_bg, y_bg = self.get_bg()
        preheader_line0 = \
            '# BG ROI: {0: .5f}, {1: .5f} \n'.format(self.roi[0], self.roi[1])
        preheader_line1 = \
            '# BG Params: {0: d}, {1: d}, {2: d} \n'.format(
                self.params_chbg[0], self.params_chbg[1], self.params_chbg[2])
        preheader_line2 = '\n'
        writechi(bgsub_filen, x_bgsub, y_bgsub, preheader=preheader_line0 +
                 preheader_line1 + preheader_line2)
        writechi(bg_filen, x_bg, y_bg, preheader=preheader_line0 +
                 preheader_line1 + preheader_line2)


class SpectrumPattern(Spectrum):
    '''
    Do not update this.
    Exist only for reading old PPSS files.
    Do not delete this, if so old PPSS cannot be read.
    This is used only for old PPSS file.
    '''

    def __init__(self):
        self.color = 'white'
        self.display = False
        self.wavelength = 0.3344

    def get_invDsp(self):
        self.invDsp_raw = np.sin(np.radians(self.x_raw / 2.)) \
            * 2. / self.wavelength
        self.invDsp_bgsub = np.sin(np.radians(self.x_bgsub / 2.)) \
            * 2. / self.wavelength


class AziSpectrumPattern(SpectrumPattern):
    def __init__(self):
        self.azi_ranges = []


Pattern = Spectrum
PatternPeakPo = SpectrumPattern
AziPatternPeakPo = AziSpectrumPattern
