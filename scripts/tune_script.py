from __future__ import division
import math 
import sys

import numpy as np
#import pylab as plt
#from scipy.interpolate import interp1d
from scipy.optimize import newton

git_dir = '/home/pvq65952/accelerators/ibex/simul/ibex/optics_code'
sys.path.insert(0,git_dir)
import ibex_optics

op = ibex_optics.optics(f_rf=1.0, npts=1000)

Vtest_ptp = 66

print "Assuming RF frequency is 1MHz"
print "V, cell tune ", Vtest_ptp,"V ", op.voltage_to_tune(0.5*Vtest_ptp)[0]

#tune to voltage
calc_tune_to_voltage = True
if calc_tune_to_voltage:
	#for a given set of desired cell tunes, find the corresponding voltages
	nu_goal = [0.1 ,0.12, 0.15, 0.21, 0.25, 0.28, 0.33, 0.36]

	#print np.interp(np.array(nu_goal), np.array(nu_va), va)

	def volt_root(vg):
		nud = op.voltage_to_tune(vg)[0] - nug
		return nud

	i1 = 0
	
	print "voltage (ptp) for various tunes with all rods powered "
	print "Voltage (ptp) fixed at ",Vtest_ptp, "V"
	print "tune, v0 [V], Vptp [V] "
	for nug in nu_goal:
		if i1 == 0:
			vg = 0.5*Vtest_ptp
		else:
			vg = res
		res = newton(volt_root, vg)
		print nug, res*2
	
		i1 = i1 + 1


#tune to voltage
calc_tune_to_frequency = True
if calc_tune_to_frequency:
	print "RF frequency for various tunes with all rods powered "
	print "Voltage (ptp) fixed at ",Vtest_ptp, " V"
	#for a given set of desired cell tunes, find the corresponding frequencies
	#assumed voltage is fixed 

	def freq_root(fg):
		nud = op.frequency_voltage_to_tune(fg,0.5*Vtest_ptp)[0] - nug
		return nud

	i1 = 0
	print "tune, RF frequency [MHz] "
	for nug in nu_goal:
		#fg = 1
		if i1 == 0:
			fg = 1
		else:
			fg = res
		res = newton(freq_root, fg)
		print nug, res
	
		i1 = i1 + 1

