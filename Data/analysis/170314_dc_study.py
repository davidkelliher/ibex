from __future__ import division
import math 
import sys
import numpy as np
import pylab as plt


f1 = open('../2017/March/170314/IBEXdata140317offsetchange.txt','r')
#25V applied to two of four endcaps on both sides, effectively 12.5 on axis
dc_bias = []
peak_sig1 = []
for l in f1:
	lspl = l.split()
	dc_bias.append(float(lspl[1]))
	peak_sig1.append(float(lspl[2]))
dc_bias = np.array(dc_bias)
pot1 = 12.5 - dc_bias

f2 = open('../2017/March/170314/IBEXdata140317endcapvariation.txt','r')
#offset applied to main rods is 120mV before amplifiction = 6V after
dc_endcap = []
peak_sig2 = []
for l in f2:
	lspl = l.split()
	dc_endcap.append(float(lspl[0]))
	peak_sig2.append(float(lspl[1]))
dc_endcap = np.array(dc_endcap)
pot2 = 0.5*dc_endcap - 6
print dc_endcap

plt.plot(pot1, peak_sig1,'ko-')
plt.plot(pot2, peak_sig2,'ro-')
plt.xlabel('Confining potential (V)')
plt.ylabel('peak in ion signal (mV)')
plt.savefig('170314_data')
plt.show()
