#!/usr/bin/python
from __future__ import division
import sys
import numpy as np
import pylab as plt
from scipy.optimize import newton
from scipy.optimize import minimize
import time
import ibex_optics

#for a given set of desired cell tunes, find the corresponding voltages
#usage
#
#To find the voltage required in the case of nu_x=nu_y
#./tune_to_voltage.py <nux> 
#
#To find the voltage required in the case of nu_x!=nu_y
#./tune_to_voltage.py <nux> <nuy> 
#

op = ibex_optics.optics(f_rf=1.0, npts=1000)

if len(sys.argv) == 1:
	print "please supply one or two tunes"
	sys.exit()
if len(sys.argv) == 2:
	nugx = float(sys.argv[1])
	nugy = nugx
	print "requested (qx,qy) = ("+str(nugx)+", "+str(nugx)+")"
elif len(sys.argv) == 3:
	nugx = float(sys.argv[1])
	nugy = float(sys.argv[2])
	print "requested (qx,qy) = ("+str(nugx)+", "+str(nugy)+")"	
	
opt_method =  'L-BFGS-B'#'Nelder-Mead' # also good

def volt_root_1D(vg):	
	
	nux = op.voltage_to_tune(vg)[0]
	
	if nux != None:
		nud = nux - nugx
	else:
		nud = 1e6

	return nud	
	
def volt_root_2D(v_a):
	nux, nuy = op.voltage_to_tune(v_a[0],v_a[1])
	try:
		nud = (nux - nugx)**2 + (nuy-nugy)**2
	except:
		nud = 1e6
	return nud

		
#initial guess
vg = 50
ug = 0

#if requested tunes are equal, first try Newton

time0 = time.time()
if nugx == nugy:
	try:
		print "Equal tunes - try Newton-Raphson algorithm"
		res = newton(volt_root_1D, vg)
		v_out = res
		u_out = 0
	except:
		print "no solution found. Try "+opt_method+" algorithm"
		ini_a = np.array([vg,ug])
		res = minimize(volt_root_2D, ini_a, method=opt_method)
		v_out, u_out = res['x']
		print "message: ",res['message']
else:
	print "Try "+opt_method+" algorithm"
	ini_a = np.array([vg,ug])
	res = minimize(volt_root_2D, ini_a, method=opt_method)
	v_out, u_out = res['x']
	print "message: ",res['message']
	
time1 = time.time()


tune_out = op.voltage_to_tune(v_out,u_out)
		
		
print "obtained voltages ",tune_out
print "optimisation time ",time1-time0
print "RF voltage, V0 = ",v_out
print "DC voltage, U0 = ",u_out
