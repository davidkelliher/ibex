from __future__ import division
import math 
import sys
import numpy as np
import pylab as plt
import ibex_optics

#Voltage on rods is U + V*Sin(omega*t
#scan first stability region in terms of U,V (translated to a,q)

qfn = lambda qm, r0, omega0, Vrf: 4*qm*Vrf/(r0*omega0)**2
afn = lambda qm, r0, omega0, U: 8*qm*U/(r0*omega0)**2

plt.rcParams.update({'axes.labelsize':20})
plt.rcParams.update({'xtick.labelsize':14})
plt.rcParams.update({'ytick.labelsize':14})


charge = 1.602176565e-19
mass_proton = 1.672621777e-27
qm_proton = charge/mass_proton
A_Ar = 39.948
f_rf_MHz = 1
omega_rf = 2*math.pi*f_rf_MHz*1e6
r0 = 5e-3
	
op = ibex_optics.optics(f_rf=f_rf_MHz, npts=1000)


nv = 40
nu = nv

v_a = np.linspace(0,95,nv)
u_a = np.linspace(0,50,nu)

#convert to a-q parameters
q_a = qfn(qm_proton/A_Ar, r0, omega_rf, v_a)
a_a = afn(qm_proton/A_Ar, r0, omega_rf, u_a)

show_aq = True

um, vm  = np.meshgrid(u_a, v_a)

stability_a = []
index_row = 0
for u0 in u_a:

	a = afn(qm_proton/A_Ar, r0, omega_rf, u0)
	
	tr = []
	for v, q in zip(v_a, q_a):
	
		res_h, res_v = op.voltage_to_tune(v0=v, u0 = u0)
		
		#print "u0, res_h, res_v ",u0, res_h, res_v
		if res_h != None and res_v != None:
			if show_aq:
				plt.plot([q],[a],'ko')
			else:
				plt.plot([v],[u0],'ko')

if show_aq:		
	plt.xlabel('q')		
	plt.ylabel('a')
	plt.savefig('aq_stability')	
else:
	plt.xlabel(r'$V_0 [V]$')
	plt.ylabel(r'$U_0 [V]$')
	plt.savefig('UV_stability')		
plt.show()
	


