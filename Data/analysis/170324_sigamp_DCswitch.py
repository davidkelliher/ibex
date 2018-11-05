from __future__ import division
import math 
import sys
import numpy as np
import pylab as plt
import csv

#import matplotlib as mpl
#mpl.rcParams['text.usetex'] = True

#Data taken March 6-8. Measure how ion signal depends on various parameters such as G2,G4 voltage and electron beam signal duration. 

eV = 1.602
data_dir = '/home/pvq65952/accelerators/ibex/Data'
sub_dir_mar = '/2017/March'
sub_dir_apr = '/2017/April'

def read_csv_file(filename, index_st):
	"""filename includes full path. index_st is row index where data starts"""
	file = open(filename)
	reader = csv.reader(file)
	data_all = list(reader)	
	data = np.array(data_all[index_st:])
	return data

#21/3/17 + 3/4/17 data, Adam's fast switch off
fall_time_fastsw = np.array([0.005])
sig_peak_fastsw = np.array([62])
sig_integ_fastsw  = [1.656] #crude measurement 
sig_peak_fastsw_noamp = np.array([-2.4])
sig_integ_fastsw_noamp  = np.array([0.394])

#21/3/17 WW1074 TTL switch off sinusoid DC part 
fall_time_sine = [0.4]
sig_peak_sine = [58]



#24/3/17 data with Shinj's signal amplifier.
dir0 = data_dir + sub_dir_mar
data_a = read_csv_file(dir0+'/170324/170324_data.csv', 1)
fall_time_24 = data_a[:,3].astype(np.float)
sig_peak_24 = data_a[:,4].astype(np.float)
sig_integ_24 =  data_a[:,5].astype(np.float)


#10/4/17 data no signal amplifier. 1m BNC cable.
dir0 = data_dir + sub_dir_apr 
data_a = read_csv_file(dir0+'/170410/170410_data.csv', 1)
fall_time_noamp1 = data_a[:,2].astype(np.float)
sig_peak_noamp1 = data_a[:,3].astype(np.float)
sig_integ_noamp1 =  data_a[:,4].astype(np.float)

#11/4/17 data no signal amplifier. 1m BNC cable.
dir0 = data_dir + sub_dir_apr 
data_a = read_csv_file(dir0+'/170411/170411_data.csv', 1)
fall_time_noamp2 = data_a[:,2].astype(np.float)
sig_peak_noamp2 = data_a[:,3].astype(np.float)
sig_integ_noamp2 =  data_a[:,4].astype(np.float)

print fall_time_noamp1
print sig_peak_noamp1
print fall_time_noamp2
print sig_peak_noamp2

fall_time_noamp_r = np.append(fall_time_noamp1, fall_time_noamp2)
sig_peak_noamp_r = np.append(sig_peak_noamp1, sig_peak_noamp2)
sig_integ_noamp_r = np.append(sig_integ_noamp1, sig_integ_noamp2)
print fall_time_noamp_r
sort_ind =  np.argsort(fall_time_noamp_r)

fall_time_noamp = fall_time_noamp_r[sort_ind]
sig_peak_noamp = sig_peak_noamp_r[sort_ind]
sig_integ_noamp = sig_integ_noamp_r[sort_ind]



#no amplifier result
plt.subplot(211)
plt.plot(fall_time_noamp, sig_peak_noamp,'ko-')
plt.plot(fall_time_fastsw, sig_peak_fastsw_noamp,'ro',label = 'Fast sw')
plt.ylabel(r'FC peak signal [mV]')
plt.subplot(212)
plt.plot(fall_time_noamp, sig_integ_noamp,'ko-')
plt.plot(fall_time_fastsw, 1e3*sig_integ_fastsw_noamp,'ro')
plt.xlabel('fall time [us]')
plt.ylabel(r'FC signal integral [nVs]')
plt.ylim(0,400)
#plt.ylim(ymax = 0)
plt.savefig('pulse_noamp_results.png')
plt.show()



print "sig_peak_24 ",sig_peak_24
#identify various subexperiments by index
i_exp1 = range(7) #Vary pressure, filament current 14.6mA

index_sort_24 = np.argsort(fall_time_24[i_exp1])
fall_time_pulse_exp1 = fall_time_24[i_exp1][index_sort_24][:4]
sig_peak_pulse_exp1 = sig_peak_24[i_exp1][index_sort_24][:4]
fit_pulse_coef1 = np.polyfit(fall_time_pulse_exp1, sig_peak_pulse_exp1, 1)
fit_pulse_poly1 = np.poly1d(fit_pulse_coef1)
print fit_pulse_poly1
ta1 = np.linspace(0, 50,100)

plt.subplot(211)
plt.plot(fall_time_24[i_exp1], sig_peak_24[i_exp1],'ko',label='pulse')
#plt.plot(ta1, fit_pulse_poly1(ta1),'k-')
plt.plot(fall_time_fastsw, sig_peak_fastsw,'ro',label = 'Fast sw')
plt.plot(fall_time_sine, sig_peak_sine,'bo')
#plt.legend(loc = 'lower right')
plt.ylabel(r'Signal positive peak [mV]')
#plt.xscale('log')
plt.subplot(212)

plt.plot(fall_time_24[i_exp1], sig_integ_24[i_exp1],'ko')
plt.plot(fall_time_fastsw, sig_integ_fastsw,'ro')
plt.ylabel(r'integral [uVs]')
plt.xlabel('fall time [us]')
plt.ylim(ymin=0)
#plt.ylim(ymin=0)
#plt.xscale('log')
plt.savefig('pulse_amp_results.png')
plt.show()



