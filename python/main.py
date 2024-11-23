import uhd
import numpy as np
import time
import os

class USRPRadio:
    channels = [1]
    gain = 0

    def __init__(self, device_addr=""):
        self.device_addr = device_addr
        self.usrp = uhd.usrp.MultiUSRP(device_addr)
        self.current_freq = None
        self.current_bw = None
        self.current_sample_rate = None
        self.recorded_files = []

    def tune(self, frequency, bandwidth):
        """Tune the radio to a frequency F with bandwidth B."""
        self.usrp.set_rx_freq(frequency)
        self.usrp.set_rx_bandwidth(bandwidth)
        # self.current_freq = frequency
        self.current_freq = self.usrp.get_rx_freq()
        # self.current_bw = bandwidth
        self.current_bw = self.usrp.get_rx_bandwidth()
        self.current_sample_rate = self.usrp.get_rx_rate()
        print(f"Tuned to frequency: {frequency} Hz, bandwidth: {bandwidth} Hz")

    def record_iq(self, duration, filename):
        """Record the I/Q data coming from the radio for X seconds."""
        # Create a stream
        stream_args = uhd.usrp.StreamArgs("fc32", "sc16")  # Complex float32
        rx_stream = self.usrp.get_rx_stream(stream_args)

        # Create a buffer for the I/Q data
        num_samples = int(duration * self.usrp.get_rx_rate())
        iq_buffer = np.zeros(num_samples, dtype=np.complex64)

        # Start streaming
        self.usrp.set_time_now(uhd.types.TimeSpec(0.0))  # Start immediately
        rx_metadata = uhd.types.RXMetadata()
        # num_rx_samps = rx_stream.recv(iq_buffer, num_samples, rx_metadata)
        iq_buffer = self.usrp.recv_num_samps(num_samples, self.current_freq, self.current_sample_rate, self.channels, self.gain)

        # Save the I/Q data to a file
        np.save(filename, iq_buffer)
        self.recorded_files.append(filename)
        print(f"Recorded {num_samples:,} samples to {filename}")

    def get_current_tune(self):
        """Return the current center frequency and bandwidth."""
        return self.current_freq, self.current_bw, self.current_sample_rate

    def list_recorded_files(self):
        """List the recorded I/Q files."""
        return self.recorded_files

if __name__ == "__main__":
    radio = USRPRadio()

    # Example usage
    radio.tune(2.4e9, 1e6)  # Tune to 2.4 GHz with 1 MHz bandwidth
    radio.record_iq(5, "recording.npy")  # Record for 5 seconds
    freq, bw, sr = radio.get_current_tune()
    print(f"Current Frequency: {freq:,} Hz, Bandwidth: {bw:,} Hz, Sample Rate: {sr:,}")
    print("Recorded Files:", radio.list_recorded_files())
