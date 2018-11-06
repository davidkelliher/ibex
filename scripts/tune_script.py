from __future__ import division
import math 
import sys
import numpy as np
import pylab as plt
from scipy.optimize import newton
from scipy.optimize import minimize
import time

#git_dir = '/Users/pvq65952/accelerators/ibex/ibex-git/optics_code'
#sys.path.insert(0,git_dir)
import ibex_optics

op = ibex_optics.optics(f_rf=1.0, npts=1000)



opt_method =  'Nelder-Mead' #'L-BFGS-B' also good
#tune to voltage
calc_tune_to_voltage = True

scan_equaltunes = False
ntune = 10
if scan_equaltunes:
	nu_x_goal = np.linspace(0.01,0.45,ntune)
	nu_y_goal = nu_x_goal
else:
	nu_x_goal = np.array([0.215]*ntune)
	nu_y_goal = np.linspace(0.1, 0.3, ntune)
	
v_out_l = []
u_out_l = []
opt_time_l = []
if calc_tune_to_voltage:
	#for a given set of desired cell tunes, find the corresponding voltages

	def volt_root_2D(v_a):

		nux, nuy = op.voltage_to_tune(v_a[0],v_a[1])
		
		try:
			nud = (nux - nugx)**2 + (nuy-nugy)**2
		except:
			nud = 1e6
			
		return nud

	def volt_root_1D(vg):
		nud = op.voltage_to_tune(vg)[0] - nugx
		return nud
				
	check_result = False	
	i1 = 0
	for nugx, nugy in zip(nu_x_goal, nu_y_goal):
	
		if i1 == 0:
			vg = 50
			ug = 0
		else:
			#use previous result as initial guess
			vg = v_out
			ug = u_out
		
		ini_a = np.array([vg,ug])
		#res = newton(volt_root, vg, args=(ug,))
		time0 = time.time()
		
		if nugx == nugy:
			res = newton(volt_root_1D, vg)
			v_out = res
			u_out = 0
		else:
			res = minimize(volt_root_2D, ini_a, method=opt_method)
			v_out, u_out = res['x']
			
		time1 = time.time()
		opt_time_l.append(time1-time0)
		
		v_out_l.append(v_out)
		u_out_l.append(u_out)
		
		#print "goal tunes ",nugx, nugy
		#print "optimisation time ",time1-time0
		#print "result ",res
		
		
		if check_result:
			print "goal tunes ",nugx, nugy
			tune_out = op.voltage_to_tune(v_out,u_out)
			print "tunes at solution voltages ",tune_out
			
			
			resid_tune = ((tune_out[0] - nugx)**2 + (tune_out[1] - nugy)**2)**0.5
			
			print "resid_tune ",resid_tune
			
			

		i1 = i1 + 1


if scan_equaltunes:
	plt.subplot(211)
	plt.plot(nu_x_goal, v_out_l, 'ko-')
	#plt.xlabel('cell tune (x,y)')
	plt.ylabel('V0 [V]')
else:
	
	plt.subplot(311)
	plt.plot(nu_y_goal, v_out_l, 'ko-')
	plt.ylabel('V0 [V]')
	plt.title('nu_x = '+str(nu_x_goal[0]))
	plt.xlim(nu_y_goal[0], nu_y_goal[-1])
	plt.subplot(312)
	plt.plot(nu_y_goal, u_out_l, 'ro-')
	plt.ylabel('U0 [V]')
	
plt.xlim(nu_y_goal[0], nu_y_goal[-1])

if scan_equaltunes:
	plt.subplot(212)
else:
	plt.subplot(313)
	
plt.plot(nu_y_goal, opt_time_l, 'ko-')
plt.ylabel('optimisation time (s)')
plt.xlim(nu_y_goal[0], nu_y_goal[-1])
plt.ylim(ymin=0)
if scan_equaltunes:
	plt.xlabel('cell tune (x,y)')
	plt.savefig('tunescan_equal')
else:
	plt.xlabel('cell tune y')
	plt.savefig('tunescan_unequal')
plt.show()



#tune to voltage
calc_tune_to_frequency = False
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

