#!/usr/bin/env python3
import sys
import numpy as np
from scipy.special import erfinv

N = int(sys.argv[1])               
prob = 1.0 / N                     # one-sided tail probability
sigma = np.sqrt(2) * erfinv(1 - 2*prob)

print(f"Trials N = {N}")
print(f"Noise floor (sigma threshold) = {sigma:.4f}")