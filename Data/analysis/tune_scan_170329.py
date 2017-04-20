from __future__ import division
import math 
import sys
import numpy as np
import pylab as plt
import csv

def read_csv_file(filename, index_st):
	"""filename includes full path. index_st is row index where data starts"""
	file = open(filename)
	reader = csv.reader(file)
	data_all = list(reader)	
	data = np.array(data_all[index_st:])
	return data

data_dir = '/Users/pvq65952/accelerators/ibex/Data'
sub_dir = '/2017/January'
dir0 = data_dir + sub_dir 

#27/1/17 data
data_a = read_csv_file(dir0+'/170127/vary_tune_voltage.csv', 3)
v_ptp = data_a[:,2].astype(np.float)
sig_peak_v = data_a[:,3].astype(np.float)
cell_tune_v = data_a[:,4].astype(np.float)


data = np.loadtxt("frequency_tune.txt", skiprows = 2)

freq_MHz = data[:,0]
cell_tune_f = data[:,1]
sig_peak_f = data[:,2]

i_sort = np.argsort(cell_tune_f)

plt.subplot(211)
plt.plot(v_ptp, sig_peak_v, 'ko-')
plt.ylabel("peak ion signal (mV)")
plt.xlabel('RF voltage ptp [V]')
plt.subplot(212)
plt.plot(freq_MHz[i_sort], sig_peak_f[i_sort], 'ko-')
plt.ylabel("peak ion signal (mV)")
plt.xlabel('RF frequency [MHz]')
plt.savefig('tune_scan_sep.png')
plt.show()



plt.plot(cell_tune_v, sig_peak_v,'ko-',label='Vary RF voltage')
plt.plot(cell_tune_f[i_sort], sig_peak_f[i_sort],'ro-',label='Vary RF frequency')
plt.xlabel('cell tune')
plt.ylabel("ion peak signal (mV)")
plt.legend()
plt.savefig('tune_scan_combined.png')
plt.show()