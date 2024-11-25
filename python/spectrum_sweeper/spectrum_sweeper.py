import sys


import numpy as np
import scipy as sp

try:
    import uhd
except ImportError as e:
    print(e)
    print("Please install uhd")
    sys.exit(1)


class SpectrumSweeper: