#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: Spectrum Sweeper
# Author: Andreas Slovacek
# GNU Radio version: 3.10.9.2

from PyQt5 import Qt
from gnuradio import qtgui
from gnuradio import blocks
from gnuradio import fft
from gnuradio.fft import window
from gnuradio import gr
from gnuradio.filter import firdes
import sys
import signal
from PyQt5 import Qt
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio import eng_notation
from gnuradio import uhd
import time
import numpy as np
import pmt
import sip



class spectrum_sweeper(gr.top_block, Qt.QWidget):

    def __init__(self, dec_fac=16, filename='/home/ace/work/UsrpB210/data/out_dat', max_bandwidth=56e6, max_bound=6000e6, max_sample_rate=61.44e6, min_bound=70e6, nfft=4096, nsegments=116, samp_rate=50e6, start_freq=96e6, stop_freq=5930e6, stream_chan=1):
        gr.top_block.__init__(self, "Spectrum Sweeper", catch_exceptions=True)
        Qt.QWidget.__init__(self)
        self.setWindowTitle("Spectrum Sweeper")
        qtgui.util.check_set_qss()
        try:
            self.setWindowIcon(Qt.QIcon.fromTheme('gnuradio-grc'))
        except BaseException as exc:
            print(f"Qt GUI: Could not set Icon: {str(exc)}", file=sys.stderr)
        self.top_scroll_layout = Qt.QVBoxLayout()
        self.setLayout(self.top_scroll_layout)
        self.top_scroll = Qt.QScrollArea()
        self.top_scroll.setFrameStyle(Qt.QFrame.NoFrame)
        self.top_scroll_layout.addWidget(self.top_scroll)
        self.top_scroll.setWidgetResizable(True)
        self.top_widget = Qt.QWidget()
        self.top_scroll.setWidget(self.top_widget)
        self.top_layout = Qt.QVBoxLayout(self.top_widget)
        self.top_grid_layout = Qt.QGridLayout()
        self.top_layout.addLayout(self.top_grid_layout)

        self.settings = Qt.QSettings("GNU Radio", "spectrum_sweeper")

        try:
            geometry = self.settings.value("geometry")
            if geometry:
                self.restoreGeometry(geometry)
        except BaseException as exc:
            print(f"Qt GUI: Could not restore geometry: {str(exc)}", file=sys.stderr)

        ##################################################
        # Parameters
        ##################################################
        self.dec_fac = dec_fac
        self.filename = filename
        self.max_bandwidth = max_bandwidth
        self.max_bound = max_bound
        self.max_sample_rate = max_sample_rate
        self.min_bound = min_bound
        self.nfft = nfft
        self.nsegments = nsegments
        self.samp_rate = samp_rate
        self.start_freq = start_freq
        self.stop_freq = stop_freq
        self.stream_chan = stream_chan

        ##################################################
        # Blocks
        ##################################################

        self.uhd_usrp_source_0 = uhd.usrp_source(
            ",".join(("", '')),
            uhd.stream_args(
                cpu_format="fc32",
                args='',
                channels=[1],
            ),
        )
        self.uhd_usrp_source_0.set_samp_rate(samp_rate)
        self.uhd_usrp_source_0.set_time_now(uhd.time_spec(time.time()), uhd.ALL_MBOARDS)

        self.uhd_usrp_source_0.set_center_freq(start_freq, 0)
        self.uhd_usrp_source_0.set_antenna("RX2", 0)
        self.uhd_usrp_source_0.set_gain(0, 0)
        self.qtgui_vector_sink_f_0 = qtgui.vector_sink_f(
            nfft,
            0,
            500e4,
            "Frequency MHz",
            "y-Axis",
            "",
            1, # Number of inputs
            None # parent
        )
        self.qtgui_vector_sink_f_0.set_update_time(0.10)
        self.qtgui_vector_sink_f_0.set_y_axis((-140), 10)
        self.qtgui_vector_sink_f_0.enable_autoscale(True)
        self.qtgui_vector_sink_f_0.enable_grid(True)
        self.qtgui_vector_sink_f_0.set_x_axis_units("MHz")
        self.qtgui_vector_sink_f_0.set_y_axis_units("dB")
        self.qtgui_vector_sink_f_0.set_ref_level(0)


        labels = ['', '', '', '', '',
            '', '', '', '', '']
        widths = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        colors = ["blue", "red", "green", "black", "cyan",
            "magenta", "yellow", "dark red", "dark green", "dark blue"]
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
            1.0, 1.0, 1.0, 1.0, 1.0]

        for i in range(1):
            if len(labels[i]) == 0:
                self.qtgui_vector_sink_f_0.set_line_label(i, "Data {0}".format(i))
            else:
                self.qtgui_vector_sink_f_0.set_line_label(i, labels[i])
            self.qtgui_vector_sink_f_0.set_line_width(i, widths[i])
            self.qtgui_vector_sink_f_0.set_line_color(i, colors[i])
            self.qtgui_vector_sink_f_0.set_line_alpha(i, alphas[i])

        self._qtgui_vector_sink_f_0_win = sip.wrapinstance(self.qtgui_vector_sink_f_0.qwidget(), Qt.QWidget)
        self.top_layout.addWidget(self._qtgui_vector_sink_f_0_win)
        self.fft_vxx_0 = fft.fft_vcc(nfft, True, window.blackmanharris(nfft), True, 1)
        self.blocks_stream_to_vector_0 = blocks.stream_to_vector(gr.sizeof_gr_complex*1, nfft)
        self.blocks_keep_one_in_n_0 = blocks.keep_one_in_n(gr.sizeof_gr_complex*nfft, dec_fac)
        self.blocks_complex_to_mag_0 = blocks.complex_to_mag(nfft)


        ##################################################
        # Connections
        ##################################################
        self.connect((self.blocks_complex_to_mag_0, 0), (self.qtgui_vector_sink_f_0, 0))
        self.connect((self.blocks_keep_one_in_n_0, 0), (self.blocks_complex_to_mag_0, 0))
        self.connect((self.blocks_stream_to_vector_0, 0), (self.fft_vxx_0, 0))
        self.connect((self.fft_vxx_0, 0), (self.blocks_keep_one_in_n_0, 0))
        self.connect((self.uhd_usrp_source_0, 0), (self.blocks_stream_to_vector_0, 0))


    def closeEvent(self, event):
        self.settings = Qt.QSettings("GNU Radio", "spectrum_sweeper")
        self.settings.setValue("geometry", self.saveGeometry())
        self.stop()
        self.wait()

        event.accept()

    def get_dec_fac(self):
        return self.dec_fac

    def set_dec_fac(self, dec_fac):
        self.dec_fac = dec_fac
        self.blocks_keep_one_in_n_0.set_n(self.dec_fac)

    def get_filename(self):
        return self.filename

    def set_filename(self, filename):
        self.filename = filename

    def get_max_bandwidth(self):
        return self.max_bandwidth

    def set_max_bandwidth(self, max_bandwidth):
        self.max_bandwidth = max_bandwidth

    def get_max_bound(self):
        return self.max_bound

    def set_max_bound(self, max_bound):
        self.max_bound = max_bound

    def get_max_sample_rate(self):
        return self.max_sample_rate

    def set_max_sample_rate(self, max_sample_rate):
        self.max_sample_rate = max_sample_rate

    def get_min_bound(self):
        return self.min_bound

    def set_min_bound(self, min_bound):
        self.min_bound = min_bound

    def get_nfft(self):
        return self.nfft

    def set_nfft(self, nfft):
        self.nfft = nfft

    def get_nsegments(self):
        return self.nsegments

    def set_nsegments(self, nsegments):
        self.nsegments = nsegments

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.uhd_usrp_source_0.set_samp_rate(self.samp_rate)

    def get_start_freq(self):
        return self.start_freq

    def set_start_freq(self, start_freq):
        self.start_freq = start_freq
        self.uhd_usrp_source_0.set_center_freq(self.start_freq, 0)

    def get_stop_freq(self):
        return self.stop_freq

    def set_stop_freq(self, stop_freq):
        self.stop_freq = stop_freq

    def get_stream_chan(self):
        return self.stream_chan

    def set_stream_chan(self, stream_chan):
        self.stream_chan = stream_chan



def argument_parser():
    parser = ArgumentParser()
    parser.add_argument(
        "--dec-fac", dest="dec_fac", type=intx, default=16,
        help="Set Decimation Factor [default=%(default)r]")
    parser.add_argument(
        "--filename", dest="filename", type=str, default='/home/ace/work/UsrpB210/data/out_dat',
        help="Set Filename [default=%(default)r]")
    parser.add_argument(
        "--max-bandwidth", dest="max_bandwidth", type=eng_float, default=eng_notation.num_to_str(float(56e6)),
        help="Set USRPB210 Max Bandwidth [default=%(default)r]")
    parser.add_argument(
        "--max-bound", dest="max_bound", type=eng_float, default=eng_notation.num_to_str(float(6000e6)),
        help="Set USRPB210Max Freq [default=%(default)r]")
    parser.add_argument(
        "--max-sample-rate", dest="max_sample_rate", type=eng_float, default=eng_notation.num_to_str(float(61.44e6)),
        help="Set USRPB210 Max Sample Rate [default=%(default)r]")
    parser.add_argument(
        "--min-bound", dest="min_bound", type=eng_float, default=eng_notation.num_to_str(float(70e6)),
        help="Set USRPB210 Min Freq [default=%(default)r]")
    parser.add_argument(
        "--nfft", dest="nfft", type=intx, default=4096,
        help="Set FFT Size [default=%(default)r]")
    parser.add_argument(
        "--nsegments", dest="nsegments", type=intx, default=116,
        help="Set nsegments [default=%(default)r]")
    parser.add_argument(
        "--samp-rate", dest="samp_rate", type=eng_float, default=eng_notation.num_to_str(float(50e6)),
        help="Set Sample Rate [default=%(default)r]")
    parser.add_argument(
        "--start-freq", dest="start_freq", type=eng_float, default=eng_notation.num_to_str(float(96e6)),
        help="Set Starting Frequency [default=%(default)r]")
    parser.add_argument(
        "--stop-freq", dest="stop_freq", type=eng_float, default=eng_notation.num_to_str(float(5930e6)),
        help="Set End Frequency [default=%(default)r]")
    return parser


def main(top_block_cls=spectrum_sweeper, options=None):
    if options is None:
        options = argument_parser().parse_args()

    qapp = Qt.QApplication(sys.argv)

    tb = top_block_cls(dec_fac=options.dec_fac, filename=options.filename, max_bandwidth=options.max_bandwidth, max_bound=options.max_bound, max_sample_rate=options.max_sample_rate, min_bound=options.min_bound, nfft=options.nfft, nsegments=options.nsegments, samp_rate=options.samp_rate, start_freq=options.start_freq, stop_freq=options.stop_freq)

    tb.start()

    tb.show()

    def sig_handler(sig=None, frame=None):
        tb.stop()
        tb.wait()

        Qt.QApplication.quit()

    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)

    timer = Qt.QTimer()
    timer.start(500)
    timer.timeout.connect(lambda: None)

    qapp.exec_()

if __name__ == '__main__':
    main()
