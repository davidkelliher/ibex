from __future__ import division
import math 
import sys
import numpy as np
import pylab as plt

data = np.loadtxt("frequency_tune.txt", skiprows = 2)

freq_MHz = data[:,0]
cell_tune = data[:,1]
sig_peak = data[:,2]

i_sort = np.argsort(cell_tune)

plt.plot(cell_tune[i_sort], sig_peak[i_sort],'ko-')
plt.xlabel('cell tune')
plt.ylabel("ion peak signal (mV)")
plt.savefig('freq_tune.png')
plt.show()