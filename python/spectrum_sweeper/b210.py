from dataclasses import dataclass
import logging
import math
from sys import stdout
from time import time








import numpy as np
import uhd








logging.basicConfig(level = logging.DEBUG,
                    format = '%(levelname)s | %(asctime)s | %(lineno)d | %(message)s',
                    stream = stdout)




@dataclass
class B210Tuner:
    """
        specifications for a USRP B210 tuner
        - minimum frequency in Hz
        - maximum frequency in Hz
        - minimum bandwidth in Hz
        - maximum bandwidth in Hz
        - minimum gain in dB
        - maximum gain in dB
        - sample rate in sps
    """
    min_freq: float = 70e6
    max_freq: float = 6000e6
    default_freq: float = 750e6
    min_bw: float = 2e6
    max_bw: float = 56e6
    default_bw: float = 56e6
    min_gain: float = 0
    max_gain: float = 73
    default_gain: float = 50
    default_sample_rate: float = None
    rx_tuner_count: int = 2
    tx_tuner_count: int = 2
    sample_rates = set([5e6, 15.36e6, 30.72e6, 56e6, 61.44e6])

    def __init__(self,):
        self.default_sample_rate = self.default_bw

    def total_frequency(self) -> float:
        return self.max_freq - self.min_freq
    
    def count_bandwidth_sweeps(self) -> int:
        return math.floor(int(self.total_frequency() / self.min_bw))
    
    def get_next_highest_sample_rate(self, sr) -> float:
        return min(list(sorted(elt for elt in self.sample_rates if elt > sr)))


b210tuner = B210Tuner()



class Sweeper:
    """
    A class for sweeping the frequency and bandwidth of a USRP.
    """

    usrp = None
    device_addr = None
    channel = None
    duration = 0.5 # seconds
    
    
    def __init__(self, **kwargs):
        self.kwargs = kwargs
        self.current_center_freq = b210tuner.min_freq + b210tuner.default_bw // 2
        self.__init_ursp()
    
    def __init_ursp(self):
        self.device_addr = ""
        self.usrp = uhd.usrp.MultiUSRP(self.device_addr)
        self.bandwidth = b210tuner.default_bw
        self.channel = 0
        self.gain = b210tuner.default_gain
        self.sample_rate = b210tuner.default_sample_rate
        self.__tune_requests()
        logging.info("USRP B210 initialized with values: {vars(self)}")
    
    def __tune_requests(self, center_freq: float = None,
                                bandwidth: float = None, 
                                gain: float = None, 
                                sample_rate: float = None) -> bool:
        """Tune the USRP B210 to the center frequency and bandwidth.
        
        Args:
            center_freq (float): The center frequency of the USRP.
            bandwidth (float): The bandwidth of the USRP.
            gain (float): The gain of the USRP.
            sample_rate (float): The sample rate of the USRP.
        
        Returns:
            bool""" 
        if center_freq != None:
            self.current_center_freq = center_freq
        if bandwidth!= None:
            self.bandwidth = bandwidth
            self.sample_rate = b210tuner.get_next_highest_sample_rate(bandwidth)
        if gain!= None:
            self.gain = gain
        if sample_rate!= None:
            self.sample_rate = sample_rate
        try:
            self.usrp.set_rx_rate(self.sample_rate, self.channel)
            self.usrp.set_rx_freq(uhd.libpyuhd.types.tune_request(self.current_center_freq), self.channel)
            self.usrp.set_rx_gain(self.gain, self.channel)
            self.usrp.set_rx_antenna("RX2", self.channel)
            logging.debug(f'USRP: Set RX rate to {self.sample_rate} Hz, center freq to {self.current_center_freq} Hz, and gain to {self.gain}. Frequency window is {self.current_center_freq - self.bandwidth / 2}MHz to {self.current_center_freq + self.bandwidth / 2}MHz.')
        
            return True
        except Exception as e:
            logging.error(f'USRP: Failed to set RX rate to {self.sample_rate} Hz, center freq to {self.current_center_freq} Hz, and gain to {self.gain}.')
            logging.error(e)
            return False
    
    def __get_samples(self) -> np.ndarray:
        """Get the samples from the USRP.
        
        Returns:
            np.ndarray"""
        num_samples = int(np.ceil(self.duration * self.sample_rate))
        if not isinstance(self.channel, list):
            channel = [self.channel]
        else:
            channel = self.channel
        try:
           samps = self.usrp.recv_num_samps(num_samples, self.current_center_freq , self.sample_rate, channel, self.gain)
        except Exception as e:
            logging.error(f'USRP: Failed to get {num_samples} samples from USRP.')
            logging.error(e)
            return np.array([])
        logging.debug(f'USRP: Got {samps.size / 2 } samples.')
        return samps
    

    def sweep(self):
        """Sweep the USRP.
        
        Returns:
            None"""
        sweep_times = []
        while self.current_center_freq < b210tuner.max_freq:
            start_time = time()
            self.__tune_requests(self.current_center_freq, self.bandwidth, self.bandwidth, b210tuner.default_gain)
            self.__get_samples()

            # handle if the bw exceeds the max_freq
            if self.current_center_freq + self.bandwidth > b210tuner.max_freq:
                #   ---l----------l---|
                #      Cn-1       Cn  Max freq
                #     Cn-1 + bw = Cn
                # If the new center freq and the max bandwidth would exceed the max freq
                # then we need to reduce the next bandwidth that will be used.
                # The max freq minus half of the new bandwidth is the center freq
                self.bandwidth = b210tuner.max_freq - (self.current_center_freq + self.bandwidth/2)
                self.current_center_freq = b210tuner.max_freq - self.bandwidth / 2
                
            else:
                self.current_center_freq += self.bandwidth
            end_time = time()
            sweep_times.append(end_time - start_time)
        logging.debug(f"Sweep took {sum(sweep_times)} seconds, with each tune taking an average of {sum(sweep_times)/len(sweep_times)}seconds. {len(sweep_times)} sweeps took place")



if __name__ == '__main__':
    sweeper = Sweeper()
    sweeper.sweep()
