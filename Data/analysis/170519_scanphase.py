from __future__ import division
import math 
import sys
import numpy as np
import pylab as plt
import csv
import os

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
			pass
			#data_out.append(None)
	return data_out	

sub_dir = '/2017/May'
dir1 = data_dir + sub_dir 

#8/5/17 data
data_a = read_csv_file(dir1+'/170519/170519_awg_settings.csv', 3)
rf_phase = sift_floats(data_a[:,5])
sig_peak = sift_floats(data_a[:,9]) #mV
sig_int = np.array(sift_floats(data_a[:,10])) #uVs
#charge
q_fC = 0.2*sig_int
#number of ions
N_Mi = 10*q_fC/eV

#plt.subplot(211)
plt.plot(rf_phase, N_Mi,'ko')
plt.ylabel('Ion number [Mions]')
#plt.subplot(212)
#plt.plot(rf_phase, sig_peak,'ko')
plt.ylim(ymin=0)
plt.show()


