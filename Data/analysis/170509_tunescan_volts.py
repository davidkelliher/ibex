from __future__ import division
import math 
import sys
import numpy as np
import pylab as plt
import csv
import os

#fix to add ibex_optics
sys.path.append(os.path.abspath("/home/pvq65952/accelerators/ibex/simul/ibex/optics_code"))
import ibex_optics

#Data taken March 6-8. Measure how ion signal depends on various parameters such as G2,G4 voltage and electron beam signal duration. 

eV = 1.602177 #10^-19
data_dir = '/home/pvq65952/accelerators/ibex/Data'


def read_csv_file(filename, index_st):
	"""filename includes full path. index_st is row index where data starts"""
	file = open(filename)
	reader = csv.reader(file)
	data_all = list(reader)	
	data = np.array(data_all[index_st:])
	return data

def sift_floats(data_in):
	"""Pick out floats from list of data"""
	data_out = []
	for d in data_in:
		try:
			data_out.append(d.astype(np.float))
		except:
			data_out.append(None)
	return data_out

sub_dir = '/2017/May'
dir1 = data_dir + sub_dir 

#8/5/17 data
data_a = read_csv_file(dir1+'/170508/tunescan_voltage.csv', 3)
sig_peak_a = data_a[:,6].astype(np.float) #mV
v_ch1_a = data_a[:,4].astype(np.float)
v_ch2_a = data_a[:,5].astype(np.float)
sig_int_a = data_a[:,8].astype(np.float)
v_av_a = [0.5*(v1+v2) for v1,v2 in zip(v_ch1_a, v_ch2_a)]

#9/5/17 data
data_a = read_csv_file(dir1+'/170509/170509_tunescan_voltage.csv', 3)
sig_peak_b = data_a[:,6].astype(np.float) #mV
v_ch1_b =  sift_floats(data_a[:,4]) 
v_ch2_b =  sift_floats(data_a[:,5]) 
sig_int_b = np.array(sift_floats(data_a[:,8]))

v_av_b = []
for v1,v2 in zip(v_ch1_b, v_ch2_b):
	if v1 != None:
		v_av_b.append(0.5*(v1+v2))
	else:
		v_av_b.append(None)
v_av_b = np.array(v_av_b)


i_exp_b = range(6,19) 

#charge
q_fC_a = 0.2*sig_int_a
q_fC_b = 0.2*sig_int_b[i_exp_b]
#number of ions
N_Mi_a = 10*q_fC_a/eV
N_Mi_b = 10*q_fC_b/eV

#tune
op = ibex_optics.optics(f_rf=1.0, npts=1000)
tune_a = [op.voltage_to_tune(0.5*v)[0] for v in v_av_a]
tune_b = [op.voltage_to_tune(0.5*v)[0] for v in v_av_b[i_exp_b]]
print tune_a
print tune_b


plt.subplot(211)
plt.plot(v_av_a, sig_int_a,'ko',label='8/5/17')
plt.plot(v_av_b[i_exp_b], sig_int_b[i_exp_b],'ro',label='9/5/17')
plt.ylabel('Integrated signal [uVs]')
plt.legend()
plt.subplot(212)
plt.plot(v_av_a, sig_peak_a,'ko',label='8/5/17')
plt.plot(v_av_b[i_exp_b], sig_peak_b[i_exp_b],'ro',label='9/5/17')
plt.legend()
plt.xlabel('RF voltage ptp [V]')
plt.ylabel('Peak signal [mV]')
plt.savefig('intsig_170509')
plt.show()


plt.plot(tune_a, q_fC_a,'ko',label='8/5/17')
plt.plot(tune_b, q_fC_b,'ro',label='9/5/17')
plt.axvline(x=0.125, linestyle='--')
plt.axvline(x=0.167, linestyle='--')
plt.legend()
plt.xlabel('cell tune')
plt.ylabel('Charge [fC]')
plt.savefig('charge_170509')
plt.show()

plt.plot(tune_a, N_Mi_a,'ko',label='8/5/17')
plt.plot(tune_b, N_Mi_b,'ko',label='9/5/17')
#plt.legend()
plt.axvline(x=0.125, linestyle='--',color='grey')
plt.axvline(x=0.167, linestyle='--',color='grey')
plt.xlabel('tune')
plt.ylabel('Ion number [Mions]')
plt.savefig('numions_170509_3')
plt.show()


