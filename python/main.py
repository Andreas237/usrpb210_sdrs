import uhd
import numpy as np
import time
import os

class USRPRadio:
    def __init__(self, device_addr=""):
        self.device_addr = device_addr
        self.usrp = uhd.usrp.MultiUSRP(device_addr)
        self.current_freq = None
        self.current_bw = None
        self.recorded_files = []

    def tune(self, frequency, bandwidth):
        """Tune the radio to a frequency F with bandwidth B."""
        self.usrp.set_rx_freq(frequency)
        self.usrp.set_rx_bandwidth(bandwidth)
        self.current_freq = frequency
        self.current_bw = bandwidth
        print(f"Tuned to frequency: {frequency} Hz, bandwidth: {bandwidth} Hz")

    def record_iq(self, duration, filename):
        """Record the I/Q data coming from the radio for X seconds."""
        # Create a stream
        stream_args = uhd.usrp.StreamArgs("fc32")  # Complex float32
        rx_stream = self.usrp.get_rx_stream(stream_args)

        # Create a buffer for the I/Q data
        num_samples = int(duration * self.usrp.get_rx_rate())
        iq_buffer = np.zeros(num_samples, dtype=np.complex64)

        # Start streaming
        self.usrp.set_time_now(uhd.TimeSpec(0.0))  # Start immediately
        rx_metadata = uhd.RXMetadata()
        num_rx_samps = rx_stream.recv(iq_buffer, num_samples, rx_metadata)

        # Save the I/Q data to a file
        np.save(filename, iq_buffer)
        self.recorded_files.append(filename)
        print(f"Recorded {num_rx_samps} samples to {filename}")

    def get_current_freq_bw(self):
        """Return the current center frequency and bandwidth."""
        return self.current_freq, self.current_bw

    def list_recorded_files(self):
        """List the recorded I/Q files."""
        return self.recorded_files

if __name__ == "__main__":
    radio = USRPRadio()

    # Example usage
    radio.tune(2.4e9, 1e6)  # Tune to 2.4 GHz with 1 MHz bandwidth
    radio.record_iq(5, "recording.npy")  # Record for 5 seconds
    freq, bw = radio.get_current_freq_bw()
    print(f"Current Frequency: {freq} Hz, Bandwidth: {bw} Hz")
    print("Recorded Files:", radio.list_recorded_files())
