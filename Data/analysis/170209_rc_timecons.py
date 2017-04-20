from __future__ import division
import math 
import sys
import numpy as np
import pylab as plt


#Cable length data from 31/01/17
cable_l = [1.0,2.5, 6]
peak_mV = [1.1, 0.8, 0.4]

#data 9/2/17 vary cable length and resistance 
#In all cases one FC rod pair was grounded.
#second datum in log book with both pairs connected is omitted here.
cable_l_170209 = np.array([1.0, 1.75, 2.5, 6.0, 1.0])
res_170209 = np.array([1, 1, 1, 1, 0.1]) 
decaytime_170209 = np.array([155, 244, 337, 756, 14.5])
peak_mv_170209 = np.array([3.0, 2.2, 1.8, 1.1, 0.5])
peak_namp_170209 = peak_mv_170209/res_170209
fwhm_us = [249, 333, 400, 756, 112]
peak_us = [112, 126, 134, 168, 53]

capac_170209_pF = decaytime_170209/(res_170209)



fit = np.polyfit(cable_l_170209, capac_170209_pF,1)
fitp = np.poly1d(fit)
la = np.linspace(0,cable_l_170209.max()+10,2)
print fitp
plt.plot(cable_l_170209, capac_170209_pF,'ko',label='data')
plt.plot(la, fitp(la),'r-',label='fit '+str(fitp))
#plt.ylim(0,800)
plt.xlim(0,6.5)
plt.ylim(0,800)
plt.ylabel("Capacitance [pF]")
plt.xlabel("Cable length [m]")
plt.legend(loc = 'upper left')
plt.savefig('170209_rc_timecons/capvscabl.png')
plt.show()

plt.plot(decaytime_170209, peak_us, 'ko')
plt.xlabel('RC Decay time [us]')
plt.ylabel('Time to peak in ion signal [us]')
plt.ylim(ymin=0)
plt.show()


ptau0 = decaytime_170209[0]*peak_namp_170209[0]
peak_fit = ptau0/decaytime_170209
print "peak_fit ",peak_fit

x = [0,800]
plt.plot(decaytime_170209, fwhm_us, 'ko')
plt.plot(x,x,'k--')
plt.xlabel('RC Decay time [us]')
plt.ylabel('Ion signal FWHM [us]')
plt.show()

#plt.subplot(211)
plt.plot(decaytime_170209, peak_mv_170209, 'k*',label='peak voltage [mV]')
plt.plot(decaytime_170209, peak_namp_170209, 'ro',label='peak current [nA]')
plt.xlabel('RC Decay time [us]')
#plt.ylabel('Ion signal peak signal [mV]')
plt.ylim(ymin=0)
plt.ylim(ymax=6)
#plt.subplot(212)
#plt.plot(decaytime_170209, peak_namp_170209, 'ko')
#plt.ylabel('Ion signal peak current [nA]')
#plt.xlabel('1/RC Decay time [us^-1]')
#plt.ylim(ymin=0)

plt.legend()
plt.tight_layout()
plt.savefig('170209_rc_timecons/reducedecayt.png')
plt.show()


# plt.subplot(211)
# plt.plot(decaytime_170209, peak_namp_170209, 'ko')
# plt.xlabel('RC Decay time [us]')
# plt.ylabel('Ion signal peak current [nA]')
# plt.ylim(ymin=0)
# plt.subplot(212)
# plt.plot(1/decaytime_170209, peak_namp_170209, 'ko')
# plt.ylabel('Ion signal peak current [nA]')
# plt.xlabel('1/RC Decay time [us^-1]')
# plt.ylim(ymin=0)
# plt.tight_layout()
# plt.show()


product = fwhm_us*peak_namp_170209
plt.plot(decaytime_170209, product, 'ko')
plt.xlabel('RC Decay time [us]')
plt.ylabel('peak current * FWHM [nA us]')
plt.ylim(ymin=0)
plt.show()

sys.exit()





