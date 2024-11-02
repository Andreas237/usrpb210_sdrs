import argparse
import ctypes
import cupy as cp
import cupyx.scipy.fft as cufft
import cupyx.scipy.signal as cpsp
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
import uhd


def parse_args():
    parser = argparse.ArgumentParser(
        prog = 'sample_capture_and_plot',
        usage = '''frequency range: 70MHz - 6GHz
        maximum sample rate: 61.44Msps
        maximum bandwidth: 56MHz
        '''
    )
    parser.add_argument("-a", "--args", default="", type=str)
    parser.add_argument("-o", "--output-file", type=str, required=True)
    parser.add_argument("-f", "--freq", type=float, required=True)
    parser.add_argument("-r", "--rate", default=1e6, type=float)
    parser.add_argument("-d", "--duration", default=5.0, type=float)
    parser.add_argument("-c", "--channels", default=0, nargs="+", type=int)
    parser.add_argument("-g", "--gain", type=int, default=10)
    return parser.parse_args()


def plotter(samples):
    samples_gpu = cp.asarray(samples)
    sp_gpu = cufft.fft(samples_gpu)
    print(f'took the fft')

    fft_shift_gpu = cufft.fftshift(sp_gpu)
    abs_fft_shift_gpu = cp.absolute(fft_shift_gpu)
    print(f'shifted it')
    
    freq_gpu = cufft.fftfreq(samples_gpu.shape[-1])
    print(f'found the freqs')

    peaks_gpu, _ = cpsp.find_peaks(sp_gpu[0].real, height=0)
    print(f'found peaks')

    
    sp = cp.asnumpy(sp_gpu)
    fft_shift = cp.asnumpy(fft_shift_gpu)
    abs_fft_shift = cp.asnumpy(abs_fft_shift_gpu)
    freq = cp.asnumpy(freq_gpu)
    peaks = cp.asnumpy(peaks_gpu)
    print(f'transferred from device to host memory')

    # sp = sp[::4]
    # fft_shift = fft_shift[::4]
    # freq = freq[::4]
    # peaks = peaks[::4]
    # print(f'downsampling by a factor of 4')
 
    print(f'sp.shape = {sp.shape}')
    print(f'sp.real.shape = {sp.real.shape}')
    print(f'sp.imag.shape = {sp.imag.shape}')
    print(f'samples.shape = {samples.shape}')
    print(f'fft_shift.shape = {fft_shift.shape}')
    print(f'freq.shape = {freq.shape}')
    print(f'peaks.shape = {peaks.shape}')

    print(samples[:5])

    # Plot the FFT magnitude spectrum
    fig, axs = plt.subplots(2,2, sharey=True)
    fig.suptitle('Compare FFT Plots of the Samples')
    # axs[0, 0].plot(freq, sp[0].real, freq, sp[0].imag)
    axs[0, 1].plot(abs_fft_shift)
    axs[1,0].plot(peaks, sp[0][peaks], 'x')
    # fig.show()
    # plt.show()



    # plt.plot(np.abs(fft_result))
    # plt.xlabel('Frequency Bin')
    # plt.ylabel('Magnitude')
    # plt.title('FFT Spectrum')
    # plt.show()

def main():
    args = parse_args()
    usrp = uhd.usrp.MultiUSRP(args.args)
    num_samps = int(np.ceil(args.duration*args.rate))
    if not isinstance(args.channels, list):
        args.channels = [args.channels]
    samps = usrp.recv_num_samps(num_samps, args.freq, args.rate, args.channels, args.gain)
    print(f'Sampling complete')
    with open(args.output_file, 'wb') as f:
        np.save(f, samps, allow_pickle=False, fix_imports=False)
        print(f'Saved')
    plotter(samps)

if __name__ == "__main__":
    main()