from spectrum_sweeper import spectrum_sweeper


from argparse import ArgumentParser
import math

MIN_FREQ=70e6
MAX_FREQ=6000e6
BW=20e6
NUM_ITERS=int((MAX_FREQ-MIN_FREQ)//BW)

def main():
    cf = MIN_FREQ + BW/2
    low_freq = cf - BW/2
    hi_freq = cf + BW/2
    
    if low_freq < MIN_FREQ:
        print(f'ERROR: lower frequency bound passed')
        exit(1)
    
    for i in range(NUM_ITERS):
        
        if hi_freq > MAX_FREQ:
            print(f'ERROR: lower frequency bound passed')
            exit(1)
        print(f'lower freq {low_freq}\t center freq {cf}\thi freq {hi_freq}')
        cf += BW
        low_freq = cf - BW/2
        hi_freq = cf + BW/2


if __name__ == "__main__":
    main()