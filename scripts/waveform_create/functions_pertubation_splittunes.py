from __future__ import division
import numpy as np
import matplotlib.pyplot as plt
import math
import sys
import csv
from scipy.optimize import newton
from scipy.optimize import minimize
import ibex_optics_pert
import ibex_optics_181109

def frange(start, stop, step):
    # used to give foat values within a range, at specified intervals.

    i = start
    while i < stop:
        yield i
        i += step

def readfiledata(filein):
    infile = open(filein, 'r')
    line = ' '

    a = []
    b = []
    c = []
    d = []


    i1 = 0

    while not len(line) == 0 and infile:
        line = infile.readline()


        if line == '':
            0
            #print "found end of file"



        elif i1 <3:
            #print line
			0

        else:

            lspl = line.split(",")
            x = lspl[0].strip()
            y = lspl[1].strip()
            z = lspl[2].strip()
            w = lspl[3].strip()
            #print lspl

            if lspl != [] and i1 != 0:
                a.append(float(x))
                b.append(float(y))
                c.append(float(z))
                d.append(float(w))


        i1 = i1 + 1


    return a, b, c, d


    
def tune_to_voltage_ibex_optics(tune_goal, vguess = 80):
    """This function assumes a 1MHz sinusoid waveform and equal tunes in both
planes. It searches for the voltage amplitude that produces tune_goal"""

    op = ibex_optics_pert.optics(f_rf=1.0, npts=1000)

    def volt_root(v):
        tune = op.voltage_to_tune(v)[0] - tune_goal
        return tune

    #vg = 80 #initial guess
    vsol = newton(volt_root, vguess)
    
    return vsol


	
    

def tune_to_voltages(nugx, nugy):
    """Find DC and RF voltages U0,V0 corresponding to desired transvere tunes nugx, nugy"""


    def volt_root_1D(vg):	
            
            nux = op.voltage_to_tune(vg)[0]

            if nux != None:
                    nud = nux - nugx
            else:
                    nud = 1e6

            return nud

    def volt_root_2D(v_a):
            nux, nuy = op.voltage_to_tune(v_a[0],v_a[1])
            try:
                    nud = (nux - nugx)**2 + (nuy-nugy)**2
            except:
                    nud = 1e6
            return nud
    
    #initial guess
    vg = 15
    ug = 0

    print "nugx, nugy ",nugx, nugy
    
    opt_method =  'L-BFGS-B' 
    op = ibex_optics_181109.optics(f_rf=1.0, npts=1000)
    #if requested tunes are equal, first try Newton

    if nugx == nugy:
            try:
                    #print "Equal tunes - try Newton-Raphson algorithm"
                    res = newton(volt_root_1D, vg)
                    v_out = res
                    u_out = 0
            except:
                    #print "no solution found. Try "+opt_method+" algorithm"
                    ini_a = np.array([vg,ug])
                    res = minimize(volt_root_2D, ini_a, method=opt_method)
                    v_out, u_out = res['x']
                    #print "message: ",res['message']
    else:
            #print "Try "+opt_method+" algorithm"
            ini_a = np.array([vg,ug])
            res = minimize(volt_root_2D, ini_a, method=opt_method)
            v_out, u_out = res['x']
            print "message: ",res['message']
        

    tune_out = op.voltage_to_tune(v_out,u_out)

    return v_out, u_out, tune_out



class Waveforms(object):

    def __init__(self, rodtype, seg_len, offset, accum_voltage, v0_array, u0_array, ramp_periods, amp_gain, awg_connect, awg_gain, max_bits, endcap_offset_drop=0):

        self.Type = rodtype
        self.Seg_len = seg_len
        self.Offset = offset
        self.Offset_drop = endcap_offset_drop
        self.accum_voltage = accum_voltage
        self.v0_array = v0_array
        self.u0_array = u0_array
        self.Ramp_periods = ramp_periods
        self.DC_gain =  50
        self.awg_DC_offset = {'C1':0.00, 'C2':0.00, 'C3':0.0, 'C4':0.0} 
        self_amp_DC_gain = {'A1': 50, 'A2': 50, 'A3':50.0, 'A4':50.0}
        
        self.__dict__.update(amp_gain)
        self.__dict__.update(awg_connect)
        
        self.Amp_gain = amp_gain
        self.awg_connect = awg_connect
        self.Awg_gain = awg_gain
        self.Max_bits = max_bits


    def get_type(self):
        return self.Type

    def get_seg_len(self):
        return self.Seg_len

    def get_offset(self):
        return self.Offset

    def get_accum_voltage(self):
        return self.accum_voltage

    def get_v0_array(self):
        return self.v0_array

    def get_u0_array(self):
        return self.u0_array
    
    def get_ramp_periods(self):
        return self.Ramp_periods

    def get_amp_gain(self):
        return self.Amp_gain

    def set_amp_gain(self, gain):
        self.Amp_gain = gain
        return self.Amp_gain

    def create_accumulation_waveforms(self, seg, rods, phase, pert):
        outfile = open(self.Type + str(rods) + '_seg_' + str(seg) +'.csv', 'w')
        voltage = []

        if self.Type == 'FC' and rods == 2:
            accum_voltage = self.accum_voltage/2
        else:
            accum_voltage = self.accum_voltage
        
        print "outfile ",outfile

        if rods == "13":
            for i in range(self.Seg_len):
                voltage.append(accum_voltage * np.sin((i * 2 * np.pi/ self.Seg_len)+ phase)/self.Amp_gain[self.Type+rods] + (self.Offset/self.DC_gain))
        else:
            for i in range(self.Seg_len):
                voltage.append(-1*accum_voltage * np.sin((i * 2 * np.pi / self.Seg_len)+ phase)/self.Amp_gain[self.Type+rods] + (self.Offset/self.DC_gain))


        # convert amplifier voltage to AWG bits
        voltage = np.array(voltage)
        accumulation_v_bits = voltage*(self.Max_bits / self.Awg_gain)

        
        writer = csv.writer(outfile, lineterminator='\n')
        for i, v in zip(range(self.Seg_len), accumulation_v_bits):
            writer.writerow((i, v))

        outfile.close()

        return

    def  create_ramping_waveforms(self, seg, rods, phase, pert):

        if self.Type == 'FC' and rods == 2:
            v0_array = self.v0_array/2
            accum_voltage = self.accum_voltage /2
        else:
            v0_array = self.v0_array
            accum_voltage = self.accum_voltage
        
        for j in range(len(self.v0_array)):

            if pert[3] == 0:

                outfile = open(self.Type + str(rods) + '_seg_' + str(seg) + '_' + str(j) + '.csv', 'w')
            else:

                if pert[1] == 0.0:
                    outfile = open(self.Type + str(rods) + '_seg_' + str(seg) + '_' + str(2*j) + '.csv', 'w')
                else:
                    outfile = open(self.Type + str(rods) + '_seg_' + str(seg) + '_' + str((2*(j+1)) - 1) + '.csv', 'w')
                    
            voltage = []
            number = []

            for i in range(int(self.Seg_len * self.Ramp_periods)):
                number.append(i)


            for l in range(int(self.Ramp_periods)):
                for i in range(self.Seg_len):
                    if rods == "13":
                        voltage.append((((((v0_array[j]-accum_voltage)*((l*self.Seg_len) + i))/(self.Ramp_periods * self.Seg_len)) + accum_voltage)
                         * np.sin((i * 2 * np.pi / self.Seg_len)+ phase))/self.Amp_gain[self.Type+rods] + self.Offset/self.DC_gain)
                    else:
                        voltage.append((((((v0_array[j]-accum_voltage)*((l*self.Seg_len) + i))/(self.Ramp_periods * self.Seg_len)) + accum_voltage)
                         * -1 * np.sin((i * 2 * np.pi / self.Seg_len)+ phase))/self.Amp_gain[self.Type+rods] + self.Offset/self.DC_gain)

            voltage = np.array(voltage)
            v_bits = voltage * (self.Max_bits / self.Awg_gain)

            writer = csv.writer(outfile, lineterminator='\n')
            for i, v in zip(number, v_bits):
                writer.writerow((i, v))

            outfile.close()


        return

    def create_final_tune_waveforms(self, seg, rods, phase, dc_offset, pert):

        if self.Type == 'FC' and rods == 2:
            v0_array = self.v0_array/2
        else:
            v0_array = self.v0_array

        print "seg, final dc offset: ",seg, self.Offset

        for j in range(len(self.v0_array)): 

            if pert[3] == 0:

                outfile = open(self.Type + str(rods) + '_seg_' + str(seg) + '_' + str(j) + '.csv', 'w')


            else:

                if pert[1] == 0.0:
                    outfile = open(self.Type + str(rods) + '_seg_' + str(seg) + '_' + str(2*j) + '.csv', 'w')
                else:
                    outfile = open(self.Type + str(rods) + '_seg_' + str(seg) + '_' + str((2*(j+1)) - 1) + '.csv', 'w')

                        
            voltage = []
            number = []

            if seg == 3 and self.Type == 'CROD' and pert[4]== 0.0:
                #print 'yes!'
    #                for i in range(int(pert[2] * self.Seg_len *(1e6/pert[0]))):
                for i in range(int(pert[2] * self.Seg_len)):
                    number.append(i)
                if rods == "13":
                    for i in range(int(pert[2] * self.Seg_len)):
                        voltage.append((v0_array[j] * np.sin((i *  2 * np.pi / self.Seg_len)+ phase) /self.Amp_gain[self.Type+rods]) +
                                       (pert[1] * np.sin((i * 2 * np.pi / (self.Seg_len / (pert[0]/1e6))) + phase) / self.Amp_gain[
                            self.Type + rods]) + (dc_offset/self.DC_gain))
                else:
                    for i in range(int(pert[2] * self.Seg_len)):
                        voltage.append((-1 * v0_array[j] * np.sin((i * 2 * np.pi / self.Seg_len)+ phase) /self.Amp_gain[self.Type+rods]) -
                                       (pert[1] * np.sin((i * 2 * np.pi / (self.Seg_len / (pert[0]/1e6))) + phase) / self.Amp_gain[
                            self.Type + rods]) + (dc_offset/self.DC_gain))

            elif pert[4] != 0.0 and seg ==4 and self.Type == 'CROD':
                for i in range(int(pert[2] * self.Seg_len)):
                    number.append(i)
                if rods == "13":
                    for i in range(int(pert[2] * self.Seg_len)):
                        voltage.append((v0_array[j] * np.sin((i *  2 * np.pi / self.Seg_len)+ phase) /self.Amp_gain[self.Type+rods]) +
                                       (pert[1] * np.sin((i * 2 * np.pi / (self.Seg_len / (pert[0]/1e6))) + phase) / self.Amp_gain[
                            self.Type + rods]) + (dc_offset/self.DC_gain))
                else:
                    for i in range(int(pert[2] * self.Seg_len)):
                        voltage.append((-1 * v0_array[j] * np.sin((i * 2 * np.pi / self.Seg_len)+ phase) /self.Amp_gain[self.Type+rods]) -
                                       (pert[1] * np.sin((i * 2 * np.pi / (self.Seg_len / (pert[0]/1e6))) + phase) / self.Amp_gain[
                            self.Type + rods]) + (dc_offset/self.DC_gain))


            else:
                for i in range(self.Seg_len):
                    number.append(i)
                if rods == "13":
                    for i in range(self.Seg_len):
                        voltage.append(v0_array[j] * np.sin((i *  2 * np.pi / self.Seg_len)+ phase) /self.Amp_gain[self.Type+rods] + (dc_offset/self.DC_gain))
                else:
                    for i in range(self.Seg_len):
                        voltage.append(-1 * v0_array[j] * np.sin((i * 2 * np.pi / self.Seg_len)+ phase) /self.Amp_gain[self.Type+rods] + (dc_offset/self.DC_gain))


            voltage = np.array(voltage)
            v_bits = voltage * (self.Max_bits / self.Awg_gain)

            writer = csv.writer(outfile, lineterminator='\n')
            for i, v in zip(range(len(voltage)), v_bits):
                writer.writerow((i, v))

            outfile.close()
        return



    def create_blank_waveform_accumulation(self, seg, rods, phase, pert):

        for j in range(len(self.v0_array)):

            outfile = open(self.Type + str(rods) + '_seg_' + str(seg) + '.csv', 'w')
            voltage = []
            number = []

            for i in range(self.Seg_len):
                number.append(i)

            print "rods in gate drop ", rods
            print "seg, self.Offset_drop ", seg, self.Offset_drop
            if rods == "13":
                for i in range(self.Seg_len):
                    voltage.append((self.Offset/self.DC_gain))
            else:
                for i in range(self.Seg_len):
                    voltage.append((self.Offset/self.DC_gain))
            # convert amplifier voltage to AWG bits
            voltage = np.array(voltage)
            v_bits = voltage * (self.Max_bits / self.Awg_gain)

            writer = csv.writer(outfile, lineterminator='\n')
            for i, v in zip(range(self.Seg_len), v_bits):
                writer.writerow((i, v))

            outfile.close()
        return

    def create_blank_waveform(self, seg, rods, phase, dc_offset, pert):

        for j in range(len(self.vo_array)):

            if pert[1] == 0.0:
                outfile = open(self.Type + str(rods) + '_seg_' + str(seg) + '_' + str(2*j) + '.csv', 'w')
            else:
                outfile = open(self.Type + str(rods) + '_seg_' + str(seg) + '_' + str((2*(j+1)) - 1) + '.csv', 'w')
            voltage = []
            number = []

            for i in range(self.Seg_len):
                number.append(i)

            print "rods in gate drop ", rods
            print "seg, self.Offset_drop ", seg, self.Offset_drop
            if rods == "13":
                for i in range(self.Seg_len):
                    voltage.append((dc_offset/self.DC_gain))
            else:
                for i in range(self.Seg_len):
                    voltage.append((dc_offset/self.DC_gain))
            # convert amplifier voltage to AWG bits
            voltage = np.array(voltage)
            v_bits = voltage * (self.Max_bits / self.Awg_gain)

            writer = csv.writer(outfile, lineterminator='\n')
            for i, v in zip(range(self.Seg_len), v_bits):
                writer.writerow((i, v))

            outfile.close()
        return

    def create_blank_ramp_waveform(self, seg, rods, phase, pert):

        for j in range(len(self.v0_array)):

            if pert[3] == 0:

                outfile = open(self.Type + str(rods) + '_seg_' + str(seg) + '_' + str(j) + '.csv', 'w')


            else:

                if pert[1] == 0.0:
                    outfile = open(self.Type + str(rods) + '_seg_' + str(seg) + '_' + str(2*j) + '.csv', 'w')
                else:
                    outfile = open(self.Type + str(rods) + '_seg_' + str(seg) + '_' + str((2*(j+1)) - 1) + '.csv', 'w')


            voltage = []
            number = []

            for i in range(int(self.Seg_len * 100)):
                number.append(i)

            for l in range(int(100)):
                for i in range(self.Seg_len):
                    if rods == "13":
                        voltage.append(0.0)
                        #voltage.append(90 * np.sin((i * 2 * np.pi/ self.Seg_len)+ phase)/self.Amp_gain[self.Type+rods] + (self.Offset/self.DC_gain) + DCawgoff)
                    else:
                        voltage.append(0.0)
                        #voltage.append(-1*90 * np.sin((i * 2 * np.pi/ self.Seg_len)+ phase)/self.Amp_gain[self.Type+rods] + (self.Offset/self.DC_gain) + DCawgoff)


            # convert amplifier voltage to AWG bits
            voltage = np.array(voltage)
            v_bits = voltage * (self.Max_bits / self.Awg_gain)

            writer = csv.writer(outfile, lineterminator='\n')
            for i, v in zip(number, v_bits):
                writer.writerow((i, v))

            outfile.close()

        return

    def create_perturbing_waveform(self, seg, rods, phase, pert):

        for j in range(len(self.v0_array)):

            if pert[1] == 0.0:
                outfile = open(self.Type + str(rods) + '_seg_' + str(seg) + '_' + str(2*j) + '.csv', 'w')
            else:
                outfile = open(self.Type + str(rods) + '_seg_' + str(seg) + '_' + str((2*(j+1)) - 1) + '.csv', 'w')
            voltage = []
            number = []

            
            for i in range(int(self.Seg_len *(1e6/pert[0]))):
                number.append(i)

            print "rods in gate drop ", rods
            print "seg, self.Offset_drop ", seg, self.Offset_drop
            if rods == "13":
                for i in range(int(self.Seg_len * (1e6/pert[0]))):
                    voltage.append(
                        pert[1] * np.sin((i * 2 * np.pi / (self.Seg_len / (pert[0]/1e6))) + phase) / self.Amp_gain[
                            self.Type + rods] + self.Offset/self.DC_gain)
            else:
                for i in range(int(self.Seg_len * (1e6/pert[0]))):
                    voltage.append(
                        -1 * pert[1] * np.sin((i * 2 * np.pi / (self.Seg_len / (pert[0]/1e6))) + phase) / self.Amp_gain[
                            self.Type + rods] + self.Offset/self.DC_gain)


            # convert amplifier voltage to AWG bits
            voltage = np.array(voltage)
            v_bits = voltage * (self.Max_bits / self.Awg_gain)

            writer = csv.writer(outfile, lineterminator='\n')
            for i, v in zip(range(int(self.Seg_len * (1e6/pert[0]))), v_bits):
                writer.writerow((i, v))

            outfile.close()
        return


    def create_all_waveforms(self, powered, pertubation):
        FC_phase_13 = -0.021
        FC_phase_24 = -0.041
        CROD_phase_13 = 0.0
        CROD_phase_24 = -0.014
        if powered == 2:
            if pertubation == False:
                rods = "13"
                if self.Type == "CROD":
                    self.create_accumulation_waveforms(1, rods, CROD_phase_13, pertubation)
                    self.create_ramping_waveforms(2, rods, CROD_phase_13, pertubation)
                    self.create_final_tune_waveforms(3, rods, CROD_phase_13, self.Offset, pertubation)
                    self.create_final_tune_waveforms(4, rods, CROD_phase_13, self.Offset, pertubation)
                    self.create_blank_ramp_waveform(5, rods, CROD_phase_13, pertubation)

                if self.Type == "FC":
                    self.create_accumulation_waveforms(1, rods, FC_phase_13, pertubation)
                    self.create_ramping_waveforms(2, rods, FC_phase_13, pertubation)
                    self.create_final_tune_waveforms(3, rods, FC_phase_13, self.Offset, pertubation)
                    self.create_gate_drop_waveforms(4, rods, FC_phase_13, self.Offset_drop, pertubation)
                    self.create_blank_ramp_waveform(5, rods, FC_phase_13, pertubation)

                if self.Type == "MCP":
                    self.create_accumulation_waveforms(1, rods, 0, pertubation)
                    self.create_ramping_waveforms(2, rods, 0, pertubation)
                    self.create_final_tune_waveforms(3, rods, 0, self.Offset, pertubation)
                    self.create_final_tune_waveforms(4, rods, 0, self.Offset, pertubation)
                    self.create_blank_ramp_waveform(5, rods, 0, pertubation)

            else:
                rods = "13"
                if self.Type == "CROD":
                    self.create_accumulation_waveforms(1, rods, CROD_phase_13, pertubation)
                    self.create_ramping_waveforms(2, rods, CROD_phase_13, pertubation)
                    self.create_final_tune_waveforms(3, rods, CROD_phase_13, self.Offset, pertubation)
                    self.create_final_tune_waveforms(4, rods, CROD_phase_13, self.Offset, pertubation)
                    self.create_blank_ramp_waveform(5, rods, CROD_phase_13, pertubation)

                if self.Type == "FC":
                    self.create_accumulation_waveforms(1, rods, FC_phase_13, pertubation)
                    self.create_ramping_waveforms(2, rods, FC_phase_13, pertubation)
                    self.create_final_tune_waveforms(3, rods, FC_phase_13, self.Offset, pertubation)
                    self.create_final_tune_waveforms(4, rods, FC_phase_13, self.Offset_drop, pertubation)
                    self.create_blank_ramp_waveform(5, rods, FC_phase_13, pertubation)

                if self.Type == "MCP":
                    self.create_accumulation_waveforms(1, rods, 0, pertubation)
                    self.create_ramping_waveforms(2, rods, 0, pertubation)
                    self.create_final_tune_waveforms(3, rods, 0, self.Offset, pertubation)
                    self.create_final_tune_waveforms(4, rods, 0, self.Offset, pertubation)
                    self.create_blank_ramp_waveform(5, rods, 0, pertubation)

                rods = "24"

                # Pertubation currenly only applied to central rods

                if self.Type == "CROD":
                    self.create_blank_waveform_accumulation(1, rods, CROD_phase_24, pertubation)
                    self.create_blank_ramp_waveform(2, rods, CROD_phase_24, pertubation)
                    self.create_perturbing_waveform(3, rods, CROD_phase_24, pertubation)
                    self.create_blank_waveform(4, rods, CROD_phase_24, self.Offset, pertubation)

                if self.Type == "FC":
                    self.create_accumulation_waveforms(1, rods, FC_phase_24, pertubation)
                    self.create_ramping_waveforms(2, rods, FC_phase_24, pertubation)
                    self.create_final_tune_waveforms(3, rods, FC_phase_24, self.Offset, pertubation)
                    self.create_final_tune_waveforms(4, rods, FC_phase_24, self.Offset_drop, pertubation)


        else:
            if pertubation [4] == 0:
                rods = "13"
                if self.Type == "CROD":
                    self.create_accumulation_waveforms(1, rods, CROD_phase_13, pertubation)
                    self.create_ramping_waveforms(2, rods, CROD_phase_13, pertubation)
                    self.create_final_tune_waveforms(3, rods, CROD_phase_13, self.Offset, pertubation)
                    self.create_final_tune_waveforms(4, rods, CROD_phase_13, self.Offset, pertubation)
                    self.create_blank_ramp_waveform(5, rods, CROD_phase_13, pertubation)

                if self.Type == "FC":
                    self.create_accumulation_waveforms(1, rods, FC_phase_13, pertubation)
                    self.create_ramping_waveforms(2, rods, FC_phase_13, pertubation)
                    self.create_final_tune_waveforms(3, rods, FC_phase_13, self.Offset, pertubation)
                    self.create_final_tune_waveforms(4, rods,FC_phase_13, self.Offset_drop, pertubation)
                    self.create_blank_ramp_waveform(5, rods, FC_phase_13, pertubation)

                if self.Type == "MCP":
                    self.create_accumulation_waveforms(1, rods, 0, pertubation)
                    self.create_ramping_waveforms(2, rods, 0, pertubation)
                    self.create_final_tune_waveforms(3, rods, 0, self.Offset, pertubation)
                    self.create_final_tune_waveforms(4, rods, 0, self.Offset, pertubation)
                    self.create_blank_ramp_waveform(5, rods, 0, pertubation)

                rods = "24"
                #self.set_amp_gain(50.11)
                if self.Type == "CROD":
                    self.create_accumulation_waveforms(1, rods, CROD_phase_24, pertubation)
                    self.create_ramping_waveforms(2, rods, CROD_phase_24, pertubation)
                    self.create_final_tune_waveforms(3, rods, CROD_phase_24, self.Offset, pertubation)
                    self.create_final_tune_waveforms(4, rods, CROD_phase_24, self.Offset, pertubation)
                    self.create_blank_ramp_waveform(5, rods, CROD_phase_24, pertubation)

                if self.Type == "FC":
                    self.create_accumulation_waveforms(1, rods, FC_phase_24, pertubation)
                    self.create_ramping_waveforms(2, rods, FC_phase_24, pertubation)
                    self.create_final_tune_waveforms(3, rods, FC_phase_24, self.Offset, pertubation)
                    self.create_final_tune_waveforms(4, rods, FC_phase_24, self.Offset_drop, pertubation)
                    self.create_blank_ramp_waveform(5, rods, FC_phase_24, pertubation)

                if self.Type == "MCP":
                    self.create_accumulation_waveforms(1, rods, 0, pertubation)
                    self.create_ramping_waveforms(2, rods, 0, pertubation)
                    self.create_final_tune_waveforms(3, rods, 0, self.Offset, pertubation)
                    self.create_final_tune_waveforms(4, rods, 0, self.Offset, pertubation)
                    self.create_blank_ramp_waveform(5, rods, FC_phase_24, pertubation)

            else:
                rods = "13"
                if self.Type == "CROD":
                    self.create_accumulation_waveforms(1, rods, CROD_phase_13, pertubation)
                    self.create_ramping_waveforms(2, rods, CROD_phase_13, pertubation)
                    self.create_final_tune_waveforms(3, rods, CROD_phase_13, self.Offset, pertubation)
                    self.create_final_tune_waveforms(4, rods, CROD_phase_13, self.Offset, pertubation)
                    self.create_final_tune_waveforms(5, rods, CROD_phase_13, self.Offset, pertubation)
                    self.create_blank_ramp_waveform(6, rods, CROD_phase_13, pertubation)

                if self.Type == "FC":
                    self.create_accumulation_waveforms(1, rods, FC_phase_13, pertubation)
                    self.create_ramping_waveforms(2, rods, FC_phase_13, pertubation)
                    self.create_final_tune_waveforms(3, rods, FC_phase_13, self.Offset, pertubation)
                    self.create_final_tune_waveforms(4, rods,FC_phase_13, self.Offset, pertubation)
                    self.create_final_tune_waveforms(5, rods,FC_phase_13, self.Offset_drop, pertubation)
                    self.create_blank_ramp_waveform(6, rods, FC_phase_13, pertubation)

                if self.Type == "MCP":
                    self.create_accumulation_waveforms(1, rods, 0, pertubation)
                    self.create_ramping_waveforms(2, rods, 0, pertubation)
                    self.create_final_tune_waveforms(3, rods, 0, self.Offset, pertubation)
                    self.create_final_tune_waveforms(4, rods, 0, self.Offset, pertubation)
                    self.create_final_tune_waveforms(5, rods, 0, self.Offset, pertubation)
                    self.create_blank_ramp_waveform(6, rods, 0, pertubation)

                rods = "24"
                #self.set_amp_gain(50.11)
                if self.Type == "CROD":
                    self.create_accumulation_waveforms(1, rods, CROD_phase_24, pertubation)
                    self.create_ramping_waveforms(2, rods, CROD_phase_24, pertubation)
                    self.create_final_tune_waveforms(3, rods, CROD_phase_24, self.Offset, pertubation)
                    self.create_final_tune_waveforms(4, rods, CROD_phase_24, self.Offset, pertubation)
                    self.create_final_tune_waveforms(5, rods, CROD_phase_24, self.Offset, pertubation)
                    self.create_blank_ramp_waveform(6, rods, CROD_phase_24, pertubation)

                if self.Type == "FC":
                    self.create_accumulation_waveforms(1, rods, FC_phase_24, pertubation)
                    self.create_ramping_waveforms(2, rods, FC_phase_24, pertubation)
                    self.create_final_tune_waveforms(3, rods, FC_phase_24, self.Offset, pertubation)
                    self.create_final_tune_waveforms(4, rods, FC_phase_24, self.Offset, pertubation)
                    self.create_final_tune_waveforms(5, rods, FC_phase_24, self.Offset_drop, pertubation)
                    self.create_blank_ramp_waveform(6, rods, FC_phase_24, pertubation)

                if self.Type == "MCP":
                    self.create_accumulation_waveforms(1, rods, 0, pertubation)
                    self.create_ramping_waveforms(2, rods, 0, pertubation)
                    self.create_final_tune_waveforms(3, rods, 0, self.Offset, pertubation)
                    self.create_final_tune_waveforms(4, rods, 0, self.Offset, pertubation)
                    self.create_final_tune_waveforms(5, rods, 0, self.Offset, pertubation)
                    self.create_blank_ramp_waveform(6, rods, 0, pertubation)

