from __future__ import division
import math 
import sys
import numpy as np
import pylab as plt
import csv

#Data taken March 6-8. Measure how ion signal depends on various parameters such as G2,G4 voltage and electron beam signal duration. 

eV = 1.602
#data_dir = '/home/pvq65952/accelerators/ibex/Data'
data_dir = '/Users/pvq65952/accelerators/ibex/Data'


def read_csv_file(filename, index_st):
	"""filename includes full path. index_st is row index where data starts"""
	file = open(filename)
	reader = csv.reader(file)
	data_all = list(reader)	
	data = np.array(data_all[index_st:])
	return data

def linfit_create(x,y,i1,i2):
	"""given x and y data, find slope "a" and offset "b" given points i1 and i2 to return fit  ax + b"""
	a = (y[i2] - y[i1])/(x[i2] - x[i1])
	b = y[i1] - a*x[i1]
	linfit = np.poly1d([a,b])
	return linfit 

#31/1/17 data
#Ion signal versus pressure with 1s ebeam
sub_dir = '/2017/January'
dir0 = data_dir + sub_dir 
data = np.loadtxt(dir0+"/170131/ions_pressure.txt", skiprows = 2)
vgauge = data[:,0]
pressure = 1e7*data[:,1]
sig_peak = data[:,2]
e_fc_uA = 0.1*data[:,3]

#plt.plot(pressure, sig_peak,'ko',label='ion peak signal (mV)')
#plt.xlim(0,8)
#plt.axvline(x=2.2)
#plt.axvline(x=4.4)
#plt.title("31/1/17 data")
#plt.show()


sub_dir = '/2017/March'
dir1 = data_dir + sub_dir 

#6/3/17 data
data_a = read_csv_file(dir1+'/170306/data_170306.csv', 4)
sig_peak_06 = data_a[:,7].astype(np.float)
pres_06 = data_a[:,6].astype(np.float)
G2_V_06 = data_a[:,1].astype(np.float)
G4_V_06 = data_a[:,3].astype(np.float)

#identify various subexperiments by index
i_exp1 = range(4) #Vary pressure, filament current 14.6mA
i_exp2 = range(4,10) #Vary presssure, fil current 15mA
i_exp3 = [9,10,11,12] #Vary G2 voltage
i_exp4 = [12,13,14,15,16,17] #Vary G4 voltage

show_pressure_scan = False
if show_pressure_scan:
	plt.plot(pressure, sig_peak,'b*',label='1m cable') #31/1/17 data
	plt.plot(pres_06[i_exp1], sig_peak_06[i_exp1],'ko',label='I_fil = 14.6mA')
	plt.plot(pres_06[i_exp2], sig_peak_06[i_exp2],'ro',label='I_fil = 15.0mA')
	plt.xlim(0,8)
	plt.ylabel('peak current [nA]')
	plt.xlabel('pressure [x1e-7 mbar]')
	plt.legend(loc = 'lower right')
	plt.savefig('pressure_scan.png')
	plt.show()

show_G2G4_scan = False
if show_G2G4_scan:
	print "G2_V_06[i_exp3] ",G2_V_06[i_exp3]
	
	fit_G2 = np.polyfit(G2_V_06[i_exp3], sig_peak_06[i_exp3],1)
	fitp_G2 = np.poly1d(fit_G2)

	fit_G4 = np.polyfit(G2_V_06[i_exp4], sig_peak_06[i_exp4],1)
	fitp_G4 = np.poly1d(fit_G4)
	
	plt.subplot(211)
	plt.plot(G2_V_06[i_exp3], sig_peak_06[i_exp3],'ko',markersize=8)
	plt.plot(G2_V_06[i_exp3], fitp_G2(G2_V_06[i_exp3]),'k--',markersize=8)
	plt.ylim(5,7.3)
	plt.xlim(-105,-80)
	plt.xlabel('G2 voltage [V]')
	plt.ylabel('peak current [nA]')
	plt.axvline(x = -84,color='r')
	#plt.ylim(ymin=0)
	plt.subplot(212)
	plt.plot(G4_V_06[i_exp4], sig_peak_06[i_exp4],'ko',markersize=8)
	plt.plot(G4_V_06[i_exp4], fitp_G4(G2_V_06[i_exp4]),'k--',markersize=8)
	plt.xlim(450,580)
	plt.ylim(5,7.3)
	plt.xlabel('G4 voltage [V]')
	plt.ylabel('peak current [nA]')
	#plt.ylim(ymin=0)
	plt.savefig('170309_opt_ions/G2G4_scan.png')
	plt.show()
	sys.exit()


#7/3/17 data (Pressure 4.4x10^-7 mbar)
#Scan ebeam duration
data_a = read_csv_file(dir1+'/170307/data_170307.csv', 4)
sig_peak_07 = data_a[:,7].astype(np.float)
pres_07 = data_a[:,6].astype(np.float)
eb_d_07 = data_a[:,2].astype(np.float)
fwhm_raw = data_a[:,8] 
fwhm_07= []
fwhm_indices_07 = [] 
for i,f in enumerate(fwhm_raw):
	try:
		fwhm_07.append(float(f))
		fwhm_indices_07.append(i)
	except:
		pass

int_crude_07 = sig_peak_07[fwhm_indices_07]*fwhm_07
ion_num_07 = int_crude_07*1e-2/eV
fwhm_mean_07 = np.mean(fwhm_07)
int_const_FWHM_07 = sig_peak_07*fwhm_mean_07
ion_num_const_FWHM_07 = int_const_FWHM_07*1e-2/eV
plateau_07 = np.mean(ion_num_const_FWHM_07[eb_d_07 >= 0.4])




#8/3/17 data (Pressure 2.2x10^-7 mbar)
data_a = read_csv_file(dir1+'/170308/data_170308.csv', 4)
sig_peak_08 = data_a[:,7].astype(np.float)
pres_08 = data_a[:,6].astype(np.float)
eb_d_08 = data_a[:,2].astype(np.float)
fwhm_raw = data_a[:,8] 
fwhm_08= []
fwhm_indices_08 = [] 
for i,f in enumerate(fwhm_raw):
	try:
		fwhm_08.append(float(f))
		fwhm_indices_08.append(i)
	except:
		pass		
int_crude_08 = sig_peak_08[fwhm_indices_08]*fwhm_08
ion_num_08 = int_crude_08*1e-2/eV
fwhm_mean_08 = np.mean(fwhm_08)
int_const_FWHM_08 = sig_peak_08*fwhm_mean_07
ion_num_const_FWHM_08 = int_const_FWHM_08*1e-2/eV
plateau_08 = np.mean(ion_num_const_FWHM_08[eb_d_08 >= 0.5])

#9/3/17 data  (Pressure 6.6x10^-7 mbar and 1.1x10^-7 mbar)
data_a = read_csv_file(dir1+'/170309/data_170309.csv', 4)
sig_peak_09 = data_a[:,7].astype(np.float)
pres_09 = data_a[:,6].astype(np.float)
eb_d_09 = data_a[:,2].astype(np.float)
fwhm_raw = data_a[:,8] 
fwhm_09= []
fwhm_indices_09 = [] 
for i,f in enumerate(fwhm_raw):
	try:
		fwhm_09.append(float(f))
		fwhm_indices_09.append(i)
	except:
		pass		
fwhm_09 = np.array(fwhm_09)
int_crude_09 = sig_peak_09[fwhm_indices_09]*fwhm_09
ion_num_09 = int_crude_09*1e-2/eV
fwhm_mean_09 = np.mean(fwhm_09)
int_const_FWHM_09 = sig_peak_09*fwhm_mean_07
ion_num_const_FWHM_09 = int_const_FWHM_09*1e-2/eV

#10/3/17 data  (Pressure 4.4x10^-7 mbar)
data_a = read_csv_file(dir1+'/170310/data_170310.csv', 4)
sig_peak_10 = data_a[:,8].astype(np.float)
pres_10 = data_a[:,6].astype(np.float)
eb_d_10 = data_a[:,2].astype(np.float)
eb_ec_d_10 = data_a[:,5].astype(np.float) #delay between ebeam off and dc switch off
fwhm_raw = data_a[:,8] 
fwhm_10= []
fwhm_indices_10 = [] 
for i,f in enumerate(fwhm_raw):
	try:
		fwhm_10.append(float(f))
		fwhm_indices_10.append(i)
	except:
		pass		
int_crude_10 = sig_peak_10[fwhm_indices_10]*fwhm_10
ion_num_10 = int_crude_10*1e-2/eV
fwhm_mean_10 = np.mean(fwhm_10)
int_const_FWHM_10 = sig_peak_10*fwhm_mean_07
ion_num_const_FWHM_10 = int_const_FWHM_10*1e-2/eV

print sig_peak_10





print "sig_peak_09 ",sig_peak_09
print "pres_07 ",pres_07
print "pres_08 ",pres_08
print "pres_09 ",pres_09
print "fwhm_mean 07,08,09 ",fwhm_mean_07, fwhm_mean_08, fwhm_mean_09

sig_peak_09_1 = sig_peak_09[pres_09 == 6.6] #signal peak when P=6.6x10^-7mbar
sig_peak_09_2 = sig_peak_09[pres_09 == 1.1] #signal peak when P=1.1x10^-7mbar
eb_d_09_1 = eb_d_09[pres_09 == 6.6]
eb_d_09_2 = eb_d_09[pres_09 == 1.1]
ion_num_const_FWHM_09_1 = ion_num_const_FWHM_09[pres_09 == 6.6]
ion_num_const_FWHM_09_2 = ion_num_const_FWHM_09[pres_09 == 1.1]
plateau_09_1 = np.mean(ion_num_const_FWHM_09_1[eb_d_09_1 >= 0.4])
plateau_09_2 = np.mean(ion_num_const_FWHM_09_2[eb_d_09_2 >= 1.0])


print "pressures at fwhm ",fwhm_09[pres_09[fwhm_indices_09] == 6.6]


plt.subplot(211)
plt.plot(eb_d_07, sig_peak_07, 'ko',label='P=4.4E-7 mbar')
plt.plot(eb_d_08, sig_peak_08, 'ro',label='P=2.2E-7 mbar')
plt.plot(eb_d_09_1, sig_peak_09_1,'bo',label='P=6.6E-7 mbar')
plt.plot(eb_d_09_2, sig_peak_09_2,'mo',label='P=1.1E-7 mbar')
plt.ylabel('peak current [nA]')
plt.ylim(ymin=0)
plt.legend(loc = 'lower right')
plt.subplot(212)
plt.plot(eb_d_07[fwhm_indices_07], fwhm_07, 'ko')
plt.plot(eb_d_08[fwhm_indices_08], fwhm_08, 'ro')
plt.plot(eb_d_09[fwhm_indices_09][pres_09[fwhm_indices_09] == 6.6], fwhm_09[pres_09[fwhm_indices_09] == 6.6], 'bo')
plt.plot(eb_d_09[fwhm_indices_09][pres_09[fwhm_indices_09] == 1.1], fwhm_09[pres_09[fwhm_indices_09] == 1.1], 'mo')
#plt.plot(eb_d_09[pres_09==6.6], fwhm_09[pres_09[fwhm_indices_09]==6.6], 'ko')
#plt.plot(eb_d_09[pres_09[fwhm_indices_09]==6.6], fwhm_09[pres_09[fwhm_indices_09]==1.1], 'ro')
plt.ylim(ymin=0, ymax =130)
plt.xlabel('ebeam duration (s)')
plt.ylabel('FWHM [us]')
plt.savefig('170309_opt_ions/ebeam_dur1.png')
plt.show()


linfit_07 = linfit_create(eb_d_07,ion_num_const_FWHM_07,9,10)
linfit_08 = linfit_create(eb_d_08,ion_num_const_FWHM_08,3,4)
linfit_09_1 = linfit_create(eb_d_09_1,ion_num_const_FWHM_09_1,2,0)
linfit_09_2 = linfit_create(eb_d_09_2,ion_num_const_FWHM_09_2,3,2)
xa = np.linspace(0,0.5,2)
print "eb_d_09_1,2 ",eb_d_09_1,eb_d_09_2
print "slopes ",linfit_07[1],linfit_08[1], linfit_09_1[1],linfit_09_2[1]


#plt.plot(eb_d_07[fwhm_indices_07], ion_num_07, 'ko',label='use measured FWHM')
plt.plot(eb_d_07, ion_num_const_FWHM_07,'ko',label='P=4.4E-7 mbar')
plt.plot(eb_d_08, ion_num_const_FWHM_08,'ro',label='P=2.2E-7 mbar')
plt.plot(eb_d_09_1, ion_num_const_FWHM_09_1,'bo',label='P=6.6E-7 mbar')
plt.plot(eb_d_09_2, ion_num_const_FWHM_09_2,'mo',label='P=1.1E-7 mbar')
plt.plot(xa, linfit_07(xa),'k-')
plt.plot(xa, linfit_08(xa),'k-')
plt.ylim(0,5)
plt.xlim(xmin=0)
plt.xlabel('ebeam duration (s)')
plt.ylabel(r'ion number (x10^6)')
plt.legend(loc = 'lower right')
plt.savefig('170309_opt_ions/ebeam_dur2.png')
plt.show()

#group overall results by pressure
pres = [1.1, 2.2, 4.4, 6.6]
slopes = [linfit_09_2[1], linfit_08[1], linfit_07[1], linfit_09_1[1]]
plateau = [plateau_09_2, plateau_08, plateau_07,plateau_09_1]

#plt.subplot(211)
plt.plot(pres, slopes,'ko-',markersize=8)
plt.ylabel('stored ion production rate (Mions/s)')	
#plt.subplot(212)
#plt.plot(pres, plateau,'ko-')
plt.xlabel('pressure [x1e-7 mbar]')
#plt.ylabel('ion plateau (Mions/s)')
plt.ylim(ymin=0)
plt.savefig('170309_opt_ions/rates.png')
plt.show()

plt.plot(pressure, e_fc_uA,'ko-') #31/1/17 data
plt.xlim(1.0, 7) #31/1/17 data
plt.show()




plt.plot(eb_ec_d_10, sig_peak_10, 'ko')
plt.xlabel('G2 OFF to EC OFF (ms)')
plt.ylabel('peak current [nA]')
plt.savefig('signal_falloff.png')
plt.show()




