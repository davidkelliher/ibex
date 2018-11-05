from __future__ import division
import math 
import sys
import numpy as np
import pylab as plt
import csv

filename = "../2017/April/170419/dclevel_FCsig.txt"
f1 = open(filename)

i = 0 
volts = []
bothpairs = []
fcrod13 = []
fcrod24 = []
for line in f1:
	if i > 1:
		ls = line.split()
		volts.append(float(ls[0]))
		bothpairs.append(float(ls[1]))
		fcrod13.append(float(ls[2]))
		fcrod24.append(float(ls[3]))
	i = i + 1

plt.plot(volts, bothpairs,'ko-',label='both pairs')
plt.plot(volts, fcrod13,'bo-',label='FC-ROD1/3 only')
plt.plot(volts, fcrod24,'ro-',label='FC-ROD2/4 only')
plt.ylabel('FC peak signal [mV]')
plt.xlabel('DC voltage')
plt.xlim(xmin=0)
plt.legend(loc = 'lower left')
plt.savefig('dclevel_FCsig.png')
plt.show()
