#!/usr/bin/env python3
# Evan gave me this script. 
import scipy.special as s
import numpy as np
import sys

prob = float(sys.argv[1])
x    = 1 - 2.0*prob
sig  = np.sqrt(2)*s.erfinv(x)

print("Probability = ",prob)
print("One in",1.0/prob, "trials")
print("Will have sigma >= ",sig)