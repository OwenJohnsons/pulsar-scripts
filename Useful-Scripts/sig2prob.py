#!/usr/bin/env python3
# Evan gave me this script. 
import scipy.special as s
import numpy as np
import sys

if len(sys.argv) < 2:
    print("Usage: sig2prob.py <sigma>")
    sys.exit(1)

sigma = float(sys.argv[1])  # Expect sigma as input
prob = 0.5 * (1 - s.erf(sigma / np.sqrt(2)))  # Convert sigma to probability

print(f"Probability >= {sigma} sigma: {prob:.12g}")

if prob == 0.0:
    print("One in >1e308 trials (beyond double precision).")
else:
    print(f"One in {1.0/prob:.6f} trials")