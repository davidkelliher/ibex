from __future__ import division
import math 
import sys
import numpy as np
import pylab as plt

#thick lens transfer matrix
transfer_mat_F = lambda kr,t: np.matrix([[np.cos(kr*t),(1/kr)*np.sin(kr*t)],[-kr*np.sin(kr*t),np.cos(kr*t)]])
transfer_mat_D = lambda kr,t: np.matrix([[np.cosh(kr*t),(1/kr)*np.sinh(kr*t)],[kr*np.sinh(kr*t),np.cosh(kr*t)]])

thinlens_mat = lambda k,t: np.matrix([[1,0],[-k*t,1]])
#thinlens_mat_D = lambda k,t: np.matrix([[1,0],[k*t,1]])
thinlens_drift = lambda t: np.matrix([[1,t],[0,1]])

class optics(object):
	"""Setup waveform and calculate optics for IBEX"""
	
	def __init__(self,  npts=1000, lat_type = "sinusoid", f_rf = 1, r0 = 5e-3):
		#self.V0 = V0
		self.npts = npts
		#coef = 2*qm_proton/(A_Ar*(r0*c)**2)
		self.lat_type = lat_type
		self.f_rf = f_rf
		

	def coef_calc(self):
		self.c = 299792458
		charge = 1.602176565e-19
		mass_proton = 1.672621777e-27
		qm_proton = charge/mass_proton
		A_Ar = 39.948
		r0 = 5e-3		
		
		coef = 2*qm_proton/(A_Ar*(r0*self.c)**2)
		return coef

	def transfer_matrix(self, kp_x, kp_y, del_s, thinlens=False, kdc = None):
		"""For waveform kp, calculate transfer matrix of period"""
		index_k = 0
		
		R11_h = []
		R12_h = []
		R21_h = []
		R22_h = []
		R11_v = []
		R12_v = []
		R21_v = []
		R22_v = []
			
		for kx, ky in zip(kp_x, kp_y):
			if isinstance(del_s,list):
				dt = del_s[index_k]
			else:
				dt = del_s
						
			if not thinlens:
				if kx > 0:
					mat_h = transfer_mat_F(abs(kx)**0.5, dt)
					mat_v = transfer_mat_D(abs(ky)**0.5, dt)
				elif kx < 0:
					mat_h = transfer_mat_D(abs(kx)**0.5, dt)
					mat_v = transfer_mat_F(abs(ky)**0.5, dt)
				elif kx == 0:
					mat_h = thinlens_drift(dt)
					mat_v = mat_h
			else:
				if k != 0:
					mat_q_h = thinlens_mat(k, dt)
					mat_q_v = thinlens_mat(-k, dt)
					mat_d = thinlens_drift(0.5*dt)
					
					mat_h1 = np.dot(mat_d, mat_q_h)
					mat_h = np.dot(mat_h1, mat_d)
					
					mat_v1 = np.dot(mat_d, mat_q_v)
					mat_v = np.dot(mat_v1, mat_d)
				else:
					mat_h = thinlens_drift(dt)
					mat_v = mat_h
				
			if index_k == 0:
				
				mat_period_h = mat_h
				mat_period_v = mat_v
					
				R = np.array(mat_period_h)
			else:		
				mat_period_h = np.dot(mat_h, mat_period_h)
				mat_period_v = np.dot(mat_v, mat_period_v)
			
				#print "R ",R, "shape ",R.shape
				#print "mat_period_h ",mat_period_h
			
				R = np.dstack((np.array(mat_period_h),R))
			
				#print "R after stack ",R
				#print "shape ",R.shape
				#sys.exit()
			
			R11_h.append(mat_period_h[0,0])
			R12_h.append(mat_period_h[0,1])
			R21_h.append(mat_period_h[1,0])
			R22_h.append(mat_period_h[1,1])
			R11_v.append(mat_period_v[0,0])
			R12_v.append(mat_period_v[0,1])
			R21_v.append(mat_period_v[1,0])
			R22_v.append(mat_period_v[1,1])
			
			index_k = index_k + 1

		#print "R11_list ",R11
		#print "R ",R
		#sys.exit()
		
		R_matrix_h = [R11_h, R12_h, R21_h, R22_h]
		R_matrix_v = [R11_v, R12_v, R21_v, R22_v]
		
		return mat_period_h, mat_period_v, R_matrix_h, R_matrix_v
		
		
	def tune_calc(self, mat):
		"""Calculate tune from transfer matrix"""
		
		if abs((mat[0,0] +  mat[1,1])/2) <= 1:
			mu1 = np.arccos((mat[0,0] +  mat[1,1])/2)
			tune = mu1/(2*math.pi)
			if np.sin(mu1) * mat[0,1] < 0:
				tune = 1 - tune
		else:
			tune = None
			
		return tune

	
	def construct_waveform(self):
		"""Construct a V(t) waveform """
	
		if self.lat_type == "sinusoid":
			self.ta = np.linspace(0,1,self.npts)
			self.va = self.v0*np.sin(2*math.pi*self.ta)
			
		return self.ta, self.va

	def calc_transfer_matrix(self):
		"""Read waveform from construct_waveform, convert of focusing waveform ka and calculate transfer matrix"""
		
		ta, va = self.construct_waveform() #read time and voltage of waveform

		coef = self.coef_calc()
		
		kx_a = coef*(self.u0 - va) #convert to array of quadrupole strengths, ka
		ky_a = coef*(self.u0 + va)
	
		del_s = (self.c/(self.f_rf*1e6))*(ta[1]-ta[0]) #convert time increment to distance increment c*dt
		self.transferh, self.transferv, self.R_matrix_h, self.R_matrix_v = self.transfer_matrix(kx_a, ky_a, del_s, thinlens=False)
		
		return self.transferh, self.transferv, self.R_matrix_h, self.R_matrix_v
				
		
	def optics_periodic(self, mat, mu):
		"""Calculate initial beta, alpha and gamma from periodic transfer matrix (i.e. at start and end of periodic cell"""
	
		denom = (2 - mat[0,0]**2 - (2*mat[0,1]*mat[1,0]) - mat[1,1]**2)**0.5
		
		alpha = (mat[0,0] - mat[1,1])/denom
		beta = mat[0,1]/math.sin(mu)
		gamma = (1+alpha**2)/beta
		
		return alpha, beta, gamma
		
	def optics_profile(self, RM, alpha, beta, gamma):
		"""Calculate optics throughout lattice using transfer matrix calculated at each point"""
		
		R11 = np.array(RM[0])
		R12 = np.array(RM[1])
		R21 = np.array(RM[2])
		R22 = np.array(RM[3])
	
		beta_p = (R11**2)*beta - 2*R11*R12*alpha + (R12**2)*gamma
		alpha_p = -R11*R21*beta + (R22*R11+R12*R21)*alpha - R12*R22*gamma 
		gamma_p = (1 + alpha_p**2)/beta_p 
		
		return alpha_p, beta_p, gamma_p
	

	def voltage_to_tune(self, v0, u0=0):
		"""Calculate tune for a given RF voltage. The frequency is assumed to be 1 MHz"""
		
		self.v0 = v0
		self.u0 = u0
		
		self.calc_transfer_matrix()
		self.tuneh = self.tune_calc(self.transferh)
		self.tunev = self.tune_calc(self.transferv)
		
	
		return self.tuneh, self.tunev
		
	def frequency_voltage_to_tune(self, f_rf, v0, u0=0):
		"""Calculate tune for a given RF frequency and given tune"""
		
		self.v0 = v0
		self.u0 = u0
		self.f_rf = f_rf
		
		self.calc_transfer_matrix()
		self.tuneh = self.tune_calc(self.transferh)
		self.tunev = self.tune_calc(self.transferv)
	
		return self.tuneh, self.tunev
		
		
	def voltage_to_optics_periodic(self, v0, u0=0):
		"""Calculate periodic optics for a given voltage"""
		
		self.v0 = v0
		self.u0 = u0
		
		self.transferh, self.transferv, _, _ = self.calc_transfer_matrix()
		self.tuneh = self.tune_calc(self.transferh)
		self.tunev = self.tune_calc(self.transferv)
		
		if self.tuneh != None:
			mu_h = 2*math.pi*self.tuneh
			self.alphah, self.betah, self.gammah = self.optics_periodic(self.transferh, mu_h)
		else:
			self.alphah = None
			self.betah = None
			self.gammah = None
		
		if self.tunev != None:
			mu_v = 2*math.pi*self.tunev
			self.alphav, self.betav, self.gammav = self.optics_periodic(self.transferv, mu_v)	
		else:
			self.alphav = None
			self.betav = None
			self.gammav = None
			
		return self.alphah, self.betah, self.gammah, self.alphav, self.betav, self.gammav

		
	def voltage_to_optics_profile(self, v0, u0=0):
		"""First calculate periodic optics. Then calculate the optics throughout the lattice using the periodic optics as the initial condition"""
		
		#calculate periodic optics
		self.voltage_to_optics_periodic(v0, u0)
		
		if self.alphah != None:
			self.alphah_p, self.betah_p, self.gammah_p = self.optics_profile(self.R_matrix_h, self.alphah, self.betah, self.gammah)
			
			#for consistency, replace first point by periodic solution
			if self.ta[0] == 0.0:
				self.alphah_p[0] = self.alphah
				self.betah_p[0] = self.betah
				self.gammah_p[0] = self.gammah
		
		if self.alphav != None:
			self.alphav_p, self.betav_p, self.gammav_p = self.optics_profile(self.R_matrix_v, self.alphav, self.betav, self.gammav)	
			
			#for consistency, replace first point by periodic solution
			if self.ta[0] == 0.0:
				self.alphav_p[0] = self.alphav
				self.betav_p[0] = self.betav
				self.gammav_p[0] = self.gammav
				
		return self.ta, self.alphah_p, self.betah_p, self.gammah_p, self.alphav_p, self.betav_p, self.gammav_p
		