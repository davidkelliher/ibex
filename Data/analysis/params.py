from __future__ import division
import math 
import sys
import numpy as np
import pylab as plt

#constants
c = 299792458
charge = 1.602176565e-19
mass_proton = 1.672621777e-27
mass_electron = 9.10938291e-31
qm_proton = charge/mass_proton
qm_electron = charge/mass_electron
epsilon = 8.85418782e-12
kb = 1.3806488e-23#8.6173324e-5 #Boltzmann constant in eV/K
N_coef = 8*math.pi*epsilon/(charge**2)
ev2K = 11604.505
A_Ar = 39.948
A_Cs = 133
A_Ba = 137.32

#functions
#%%%%%%%%%%

#Classical radius
r_p = lambda A: charge**2/(4*math.pi*epsilon*A*mass_proton*(c**2)) 

#line density in the limit of stationary plasma, [Mions/m]
N = lambda padv,T,lam,a0,A: 1e-6*(2/r_p(A))*(((padv*a0)/lam)**2 - (kb*T)/(A_Ar*mass_proton*(c**2)))

#Approx transverse emittance
emit = lambda a0,T,A: 2*a0*((kb*T)/(A_Ar*mass_proton*(c**2)))**0.5


#Settings
rf_f = 1e6 #RF frequency 
lam_rf = c/1e6 #wavelength
ltrap = 60e-3

r_p_Ar = r_p(A_Ar) #Classical radius for Argon

celltune = 0.11
phaseadv = celltune*2*math.pi
a0 = 1.6e-3
Ti_eV = 0.15
T1 = Ti_eV*ev2K
N1 =  N(phaseadv, T1, lam_rf, a0, A_Ar)
print "line density X10^6 (m^-2) ",N1
N_trap = N1*ltrap
print "stored in trap ",N_trap
print "approx emit ",emit(a0,T1,A_Ar)
R = lam_rf/(2*math.pi)
print "req ",R
beta_sm = R/celltune

print "betasm ",beta_sm
print "envelope ",(beta_sm*emit(a0,T1,A_Ar))**0.5

parr = np.linspace(0,0.11*2*math.pi,10)
Na = ltrap*N(parr, T1, lam_rf, a0, A_Ar)

print "Na ",Na

plt.plot(parr/(2*math.pi), Na, 'ko-')
plt.show()


