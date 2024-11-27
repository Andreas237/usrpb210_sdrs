import argparse
import logging
from sys import stdout

logging.basicConfig(level = logging.DEBUG,
                    format = '%(levelname)s | %(asctime)s | %(lineno)d | %(message)s',
                    stream = stdout)


import numpy as np
import scipy as sp
import matplotlib.pyplot as plt
import scipy.fftpack

try:
    import uhd
except ImportError as e:
    print(e)
    print("Please install uhd")
    sys.exit(1)



def parse_args():
    """Parse the command line arguments."""
    parser = argparse.ArgumentParser()
    parser.add_argument("-a", "--args", default="", type=str)
    parser.add_argument("--start-freq", default=70e6, type=float, help="Lower frequency bound for sweep, in Hertz")
    parser.add_argument("--end-freq", default=6000e6, type=float, help="Upper frequency bound for sweep, in Hertz")
    parser.add_argument("-c", "--channels", default=1, type=int)
    parser.add_argument("-g", "--gain", type=int, default=10, nargs='?', help="RF gain  to apply, dB", choices=[0,1,5,10,20,50])
    return parser.parse_args()


def plot_fft(samples: np.ndarray, center_freq: float, bandwidth: float, sample_rate: int = 600, fft_size: int = 1024):
    
    # y = np.fft.fft(samples)
    # freq = np.fft.fftfreq(len(samples.real))
    # plt.figure()
    # plt.plot( freq, np.abs(y) )
    # plt.figure()
    # plt.plot(freq, np.angle(y) )
    # plt.show()

    
    PSD = 10.0*np.log10(np.abs(np.fft.fftshift(np.fft.fft(samples)))**2/fft_size)
    plt.figure()
    plt.psd(PSD, sample_rate // 2)
    plt.show()

def get_samples(usrp, start_freq: float = None, end_freq: float = None, sample_rate: float = None, channel: int = 0, fft_size: int = 1024) -> np.ndarray:
    if start_freq == None or end_freq == None or sample_rate == None: 
        logging.error(f'Parameters missing to get samples')
        exit(1)
    
    usrp.set_rx_rate(sample_rate, channel)
    usrp.set_rx_freq(uhd.libpyuhd.types.tune_request(start_freq + sample_rate / 2), channel)
    usrp.set_rx_antenna("RX2", channel)
    usrp.set_rx_agc(True, channel)
     # Set up the stream and receive buffer
    st_args = uhd.usrp.StreamArgs("fc32", "sc16")
    st_args.channels = [0]
    metadata = uhd.types.RXMetadata()
    streamer = usrp.get_rx_stream(st_args)
    recv_buffer = np.zeros((1, fft_size), dtype=np.complex64)

    # Start Stream
    stream_cmd = uhd.types.StreamCMD(uhd.types.StreamMode.start_cont)
    stream_cmd.stream_now = True
    streamer.issue_stream_cmd(stream_cmd)
    streamer.recv(recv_buffer, metadata)
    return recv_buffer[0]


if __name__ == '__main__':
    args = parse_args()
    # Number of samplepoints
    # N = 600
    # # sample spacing
    # T = 1.0 / 800.0
    # x = np.linspace(0.0, N*T, N)
    # samples = np.sin(50.0 * 2.0*np.pi*x) + 0.5*np.sin(80.0 * 2.0*np.pi*x)
    # plot_fft(samples, 0,0)

    device_addr = ""
    usrp = uhd.usrp.MultiUSRP(device_addr)
    sample_rate = 50e6
    start_freq = 70e6
    end_freq = start_freq + sample_rate
    center_freq = start_freq + sample_rate/2
    samples = get_samples(usrp, 70e6, 70e6+sample_rate, sample_rate,0)
    plot_fft(samples, 0,0)