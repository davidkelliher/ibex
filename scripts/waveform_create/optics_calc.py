import math 
import os, sys
import ibex_optics
import numpy as np
from scipy.optimize import newton
import pylab as plt
import csv

op = ibex_optics.optics(f_rf=1.0, npts=1000)


#tune to voltage
calc_tune_to_voltage = True
if calc_tune_to_voltage:
        #for a given set of desired cell tunes, find the corresponding voltages
        #nu_goal = [0.114, 0.15]
        nu_goal = [0.1163, 0.1524]

        #print np.interp(np.array(nu_goal), np.array(nu_va), va)

        def volt_root(vg):
                nud = op.voltage_to_tune(vg)[0] - nug
                return nud

        i1 = 0
        print "tune, v amplitude, betx, bety, alfx, alfy"
        for nug in nu_goal:
                if i1 == 0:
                        vg = 10 #initial guess
                else:
                        vg = res
                res = newton(volt_root, vg)
                
        
                i1 = i1 + 1

                opt_out= op.voltage_to_optics_periodic(res)
                beta_x = opt_out[1]
                beta_y = opt_out[4]
                alpha_x = opt_out[0]
                alpha_y = opt_out[3]

                print nug, 2*res, beta_x, beta_y, alpha_x, alpha_y

vscope = [66.2, 85.4]
for vg in vscope:
        print op.voltage_to_tune(0.5*vg)[0]


read_madx_seq = True
if read_madx_seq:
	
        k1_name = []
        k1_l = []
        lq_l = []
        
        f1 = open('beamline_final.txt')
        for line in f1:
                lspl = line.split()
                #print lspl
                if 'k1' in lspl[0]:
                        k1_l.append(float(lspl[2][:-1])) #strip trailing semicolon
        
                if len(lspl) > 1:
                        if 'quadrupole' in lspl[1]:
                                lspl2 = lspl[2].split(",")
                                lq_l.append(float(lspl2[0]))
                                
        print "k1_l ",k1_l
        print "lq_l ",lq_l
        k1_a = np.array(k1_l)
        #plt.plot(k1_l,'ko')
        #plt.show()
        
        coef = op.coef_calc()
        
        dc_offset = 10
        
        v_a_13 = dc_offset + k1_a/coef
        v_a_24 = dc_offset - k1_a/coef
        A1_gain = 46.78
        A3_gain = 48.8888
        A4_gain = 50.85
        v_awg_a_13 = v_a_13/A1_gain
        v_awg_a_24 = v_a_24/A3_gain
        np = len(k1_a)
        
        
        #dc_awg = dc_offset/A1_gain
        
        bits = 2**15
        vbits_a_13 = bits*v_awg_a_13/2.5
        vbits_a_24 = bits*v_awg_a_24/2.5
        
        print "write csv files"
        
        csv_file = open('match_fast_13.csv','w')
        #assume waveform in which half a 1us period is spent at each amplitude.
        writer = csv.writer(csv_file, lineterminator='\n')
        
        i=0
        for vb in vbits_a_13:
                for j in range(50):
                        writer.writerow((i, vb))
                        i = i + 1
                
        csv_file.close()
        

        csv_file = open('match_fast_24.csv','w')
        #assume waveform in which half a 1us period is spent at each amplitude.
        writer = csv.writer(csv_file, lineterminator='\n')
        
        i=0
        for vb in vbits_a_24:
                for j in range(50):
                        writer.writerow((i, vb))
                        i = i + 1
                
        csv_file.close()	
			
