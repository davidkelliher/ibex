from __future__ import division
import numpy as np
import matplotlib.pyplot as plt
import math
import sys
import csv
from scipy.optimize import newton
import ibex_optics

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


    
def tune_to_voltage_ibex_optics(tune_goal):
    """This function assumes a 1MHz sinusoid waveform and equal tunes in both
planes. It searches for the voltage amplitude that produces tune_goal"""

    op = ibex_optics.optics(f_rf=1.0, npts=1000)

    def volt_root(v):
        tune = op.voltage_to_tune(v)[0] - tune_goal
        return tune

    vg = 80 #initial guess
    vsol = newton(volt_root, vg)
    
    return vsol



class Waveforms(object):

    def __init__(self, rodtype, seg_len, offset, accumulation_voltage, voltage_array, ramp_periods, amp_gain, awg_connect, awg_gain, max_bits, endcap_offset_drop=0):

        self.Type = rodtype
        self.Seg_len = seg_len
        self.Offset = offset
        self.Offset_drop = endcap_offset_drop
        self.Accumulation_voltage = accumulation_voltage
        self.Voltage_array = voltage_array
        self.Ramp_periods = ramp_periods
        self.DC_gain =  50#48.2#47.5
        #self.awg_DC_offset = {'C1':0.0025, 'C2':0.0025, 'C3':0.01, 'C4':-0.002} #account for offset in AWG DC output which varies with channel?
        #self.awg_DC_offset = {'C1':0.0025, 'C2':0.0035, 'C3':0.012, 'C4':-0.002} #15/1/18
        self.awg_DC_offset = {'C1':0.0028, 'C2':0.0072, 'C3':0.02, 'C4':0.006} #14/03/18
        #self.amp_rf_gain  = {'A1': 46.71, 'A2': 50.9139, 'A3':48.8888, 'A4':50.85}
        #self_amp_DC_gain = {'A1': 47.5, 'A2': 48.2, 'A3':47.5, 'A4':50.0}

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

    def get_accumulation_voltage(self):
        return self.Accumulation_voltage

    def get_voltage_array(self):
        return self.Voltage_array

    def get_ramp_periods(self):
        return self.Ramp_periods

    def get_amp_gain(self):
        return self.Amp_gain

    def set_amp_gain(self, gain):
        self.Amp_gain = gain
        return self.Amp_gain

    def create_accumulation_waveforms(self, seg, rods, phase):
        outfile = open(self.Type + str(rods) + '_seg_' + str(seg) +'.csv', 'w')
        voltage = []

        DCawgoff = self.awg_DC_offset[self.awg_connect[self.Type+rods]]
        
        print "outfile ",outfile

        if rods == "13":
            for i in range(self.Seg_len):
                voltage.append(self.Accumulation_voltage * np.sin((i * 2 * np.pi/ self.Seg_len)+ phase)/self.Amp_gain[self.Type+rods] + (self.Offset/self.DC_gain) + DCawgoff)
        else:
            for i in range(self.Seg_len):
                voltage.append(-1*self.Accumulation_voltage * np.sin((i * 2 * np.pi / self.Seg_len)+ phase)/self.Amp_gain[self.Type+rods] + (self.Offset/self.DC_gain) + DCawgoff)
                

        # convert amplifier voltage to AWG bits
        voltage = np.array(voltage)
        accumulation_v_bits = voltage*(self.Max_bits / self.Awg_gain)

        
        writer = csv.writer(outfile, lineterminator='\n')
        for i, v in zip(range(self.Seg_len), accumulation_v_bits):
            writer.writerow((i, v))

        outfile.close()

        return

    def create_ramping_waveforms(self, seg, rods, phase):

        DCawgoff = self.awg_DC_offset[self.awg_connect[self.Type+rods]]
        
        for j in range(len(self.Voltage_array)):

            outfile = open(self.Type + str(rods) + '_seg_' + str(seg) +'_'+ str(j) +'.csv', 'w')
            voltage = []
            number = []

            for i in range(int(self.Seg_len * self.Ramp_periods)):
                number.append(i)


            for l in range(int(self.Ramp_periods)):
                for i in range(self.Seg_len):
                    if rods == "13":
                        voltage.append((((((self.Voltage_array[j]-self.Accumulation_voltage)*((l*self.Seg_len) + i))/(self.Ramp_periods * self.Seg_len)) + self.Accumulation_voltage)
                         * np.sin((i * 2 * np.pi / self.Seg_len)+ phase))/self.Amp_gain[self.Type+rods] + self.Offset/self.DC_gain + DCawgoff)
                    else:
                        voltage.append((((((self.Voltage_array[j]-self.Accumulation_voltage)*((l*self.Seg_len) + i))/(self.Ramp_periods * self.Seg_len)) + self.Accumulation_voltage)
                         * -1 * np.sin((i * 2 * np.pi / self.Seg_len)+ phase))/self.Amp_gain[self.Type+rods] + self.Offset/self.DC_gain + DCawgoff)

            
            # convert amplifier voltage to AWG bits
            voltage = np.array(voltage)
            v_bits = voltage * (self.Max_bits / self.Awg_gain)

            writer = csv.writer(outfile, lineterminator='\n')
            for i, v in zip(number, v_bits):
                writer.writerow((i, v))

            outfile.close()


        return

    def create_final_tune_waveforms(self, seg, rods, phase):

        DCawgoff = self.awg_DC_offset[self.awg_connect[self.Type+rods]]

        print "seg, final tune dc ",seg, self.Offset
        print "Voltage_array[j] ",self.Voltage_array
        
        for j in range(len(self.Voltage_array)):

            outfile = open(self.Type + str(rods)  + '_seg_' + str(seg) + '_'+ str(j) +'.csv', 'w')
            voltage = []
            number = []

            for i in range(self.Seg_len):
                number.append(i)

            if rods == "13":
                for i in range(self.Seg_len):
                    voltage.append(self.Voltage_array[j] * np.sin((i *  2 * np.pi / self.Seg_len)+ phase) /self.Amp_gain[self.Type+rods] + (self.Offset/self.DC_gain) + DCawgoff)
            else:
                for i in range(self.Seg_len):
                    voltage.append(-1 * self.Voltage_array[j] * np.sin((i * 2 * np.pi / self.Seg_len)+ phase) /self.Amp_gain[self.Type+rods] + (self.Offset/self.DC_gain) + DCawgoff)


            # convert amplifier voltage to AWG bits
            voltage = np.array(voltage)
            v_bits = voltage * (self.Max_bits / self.Awg_gain)

            writer = csv.writer(outfile, lineterminator='\n')
            for i, v in zip(range(self.Seg_len), v_bits):
                writer.writerow((i, v))

            outfile.close()
        return

    def create_gate_drop_waveforms(self, seg, rods, phase):

        DCawgoff = self.awg_DC_offset[self.awg_connect[self.Type+rods]]
        
        for j in range(len(self.Voltage_array)):

            outfile = open(self.Type +str(rods)  + '_seg_' + str(seg) + '_'+ str(j) +'.csv', 'w')
            voltage = []
            number = []
            
            for i in range(self.Seg_len):
                number.append(i)

            print "rods in gate drop ",rods
            print "seg, self.Offset_drop ",seg, self.Offset_drop
            if rods == "13":
                for i in range(self.Seg_len):
                    voltage.append(self.Voltage_array[j] * np.sin((i * 2 * np.pi / self.Seg_len)+ phase)/self.Amp_gain[self.Type+rods] + (self.Offset_drop/self.DC_gain) + DCawgoff)
            else:
                for i in range(self.Seg_len):
                    voltage.append(-1 * self.Voltage_array[j] * np.sin((i * 2 * np.pi / self.Seg_len)+ phase) /self.Amp_gain[self.Type+rods] + (self.Offset_drop/self.DC_gain) + DCawgoff)

            # convert amplifier voltage to AWG bits
            voltage = np.array(voltage)
            v_bits = voltage*(self.Max_bits / self.Awg_gain)


            writer = csv.writer(outfile, lineterminator='\n')
            for i, v in zip(range(self.Seg_len), v_bits):
                writer.writerow((i, v))

            outfile.close()
        return

    def create_all_waveforms(self, powered):
        FC_phase_13 = -np.radians(8.0)
        FC_phase_24 = -np.radians(5.5)
        if powered ==2:
            rods = "13"
            if self.Type == "CROD":
                self.create_accumulation_waveforms(1, rods, 0)
                self.create_ramping_waveforms(2, rods, 0)
                self.create_final_tune_waveforms(3, rods, 0)
                self.create_final_tune_waveforms(4, rods, 0)

            if self.Type == "FC":
                self.create_accumulation_waveforms(1, rods, FC_phase_13)
                self.create_ramping_waveforms(2, rods, FC_phase_13)
                self.create_final_tune_waveforms(3, rods, FC_phase_13)
                self.create_gate_drop_waveforms(4, rods, FC_phase_13)

            if self.Type == "MCP":
                self.create_accumulation_waveforms(1, rods, 0)
                self.create_ramping_waveforms(2, rods, 0)
                self.create_final_tune_waveforms(3, rods, 0)
                self.create_final_tune_waveforms(4, rods, 0)

        else:
            rods = "13"
            if self.Type == "CROD":
                self.create_accumulation_waveforms(1, rods, 0)
                self.create_ramping_waveforms(2, rods, 0)
                self.create_final_tune_waveforms(3, rods, 0)
                self.create_final_tune_waveforms(4, rods, 0)

            if self.Type == "FC":
                self.create_accumulation_waveforms(1, rods, FC_phase_13)
                self.create_ramping_waveforms(2, rods, FC_phase_13)
                self.create_final_tune_waveforms(3, rods, FC_phase_13)
                self.create_gate_drop_waveforms(4, rods,FC_phase_13)

            if self.Type == "MCP":
                self.create_accumulation_waveforms(1, rods, 0)
                self.create_ramping_waveforms(2, rods, 0)
                self.create_final_tune_waveforms(3, rods, 0)
                self.create_final_tune_waveforms(4, rods, 0)

            rods = "24"
            #self.set_amp_gain(50.11)
            if self.Type == "CROD":
                self.create_accumulation_waveforms(1, rods, 0)
                self.create_ramping_waveforms(2, rods, 0)
                self.create_final_tune_waveforms(3, rods, 0)
                self.create_final_tune_waveforms(4, rods, 0)

            if self.Type == "FC":
                self.create_accumulation_waveforms(1, rods, FC_phase_24)
                self.create_ramping_waveforms(2, rods, FC_phase_24)
                self.create_final_tune_waveforms(3, rods, FC_phase_24)
                self.create_gate_drop_waveforms(4, rods, FC_phase_24)

            if self.Type == "MCP":
                self.create_accumulation_waveforms(1, rods, 0)
                self.create_ramping_waveforms(2, rods, 0)
                self.create_final_tune_waveforms(3, rods, 0)
                self.create_final_tune_waveforms(4, rods, 0)



