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


    
def tune_to_voltage_ibex_optics(tune_goal, f_rf_MHz):
    """This function assumes a sinusoid waveform and equal tunes in both
planes. It searches for the voltage amplitude that produces tune_goal"""

    op = ibex_optics.optics(f_rf=f_rf_MHz, npts=1000) 

    def volt_root(v):
        tune = op.voltage_to_tune(v)[0] - tune_goal
        return tune

    vg = 60 #initial guess
    vsol = newton(volt_root, vg)
    
    return vsol



class Waveforms(object):

    def __init__(self, rodtype, seg_len, offset, offset_diff, accumulation_voltage, voltage_array, ramp_periods, amp_gain, awg_connect, awg_gain, max_bits, endcap_offset_drop=0):

        self.Type = rodtype
        self.Seg_len = seg_len
        self.Offset = offset
        self.Offset_diff = offset_diff
        self.Offset_drop = endcap_offset_drop
        self.Accumulation_voltage = accumulation_voltage
        self.Voltage_array = voltage_array
        self.Ramp_periods = ramp_periods
        self.DC_gain =  50
        #self.amp_DC_gain = {'A1': 50, 'A2': 50, 'A3':50.0, 'A4':50.0}

        
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

    def create_accumulation_waveforms(self, seg, rods):
        
        pts_a = np.arange(self.Seg_len)

        if rods == "13":
            voltage = self.Accumulation_voltage * np.sin(pts_a * 2 * np.pi / self.Seg_len)/self.Amp_gain[self.Type+rods] + (self.Offset/self.DC_gain)

        else:
            voltage = -self.Accumulation_voltage * np.sin(pts_a * 2 * np.pi / self.Seg_len)/self.Amp_gain[self.Type+rods] + (self.Offset/self.DC_gain)
           
        # convert amplifier voltage to AWG bits
        accumulation_v_bits = voltage*(self.Max_bits / self.Awg_gain)

        outfile = open(self.Type + str(rods) + '_seg_' + str(seg) +'.csv', 'w')
        writer = csv.writer(outfile, lineterminator='\n')
        for i, v in zip(range(self.Seg_len), accumulation_v_bits):
            writer.writerow((i, v))

        outfile.close()

        return

    def  create_ramping_waveforms(self, seg, rods):

        npts_ramp = self.Ramp_periods * self.Seg_len

        for j in range(len(self.Voltage_array)):

            voltage = []

            for l in range(int(self.Ramp_periods)):
                nl = l*self.Seg_len
                for i in range(self.Seg_len):

                    rf_amp = (self.Voltage_array[j]-self.Accumulation_voltage)*(nl + i)/npts_ramp+ self.Accumulation_voltage

                    dc_part = 0.5*self.Offset_diff*(nl + i)/npts_ramp 

                    if rods == "13":
                        voltage.append(rf_amp*(np.sin(i * 2 * np.pi / self.Seg_len))/self.Amp_gain[self.Type+rods] + (self.Offset + dc_part)/self.DC_gain)
                    else:
                        voltage.append(-rf_amp*(np.sin(i * 2 * np.pi / self.Seg_len))/self.Amp_gain[self.Type+rods] + (self.Offset - dc_part) /self.DC_gain)

            
            # convert amplifier voltage to AWG bits
            voltage = np.array(voltage)
            v_bits = voltage * (self.Max_bits / self.Awg_gain)

            outfile = open(self.Type + str(rods) + '_seg_' + str(seg) +'_'+ str(j) +'.csv', 'w')
            writer = csv.writer(outfile, lineterminator='\n')
            for i, v in zip(range(int(self.Seg_len*self.Ramp_periods)), v_bits):
                writer.writerow((i, v))

            outfile.close()


        return

    def create_final_tune_waveforms(self, seg, rods, dc_offset):

        print "rods, seg, dc_offset ",self.Type, rods, seg, dc_offset

		        
        for j in range(len(self.Voltage_array)):

            outfile = open(self.Type + str(rods)  + '_seg_' + str(seg) + '_'+ str(j) +'.csv', 'w')
            voltage = []
            number = []

            for i in range(self.Seg_len):
                number.append(i)

            if rods == "13":
                for i in range(self.Seg_len):
                    voltage.append(self.Voltage_array[j] * np.sin(i * 2 * np.pi / self.Seg_len)/self.Amp_gain[self.Type+rods] + (dc_offset + 0.5*self.Offset_diff)/self.DC_gain )
            else:
                for i in range(self.Seg_len):
                    voltage.append(-1 * self.Voltage_array[j] * np.sin(i * 2 * np.pi / self.Seg_len)/self.Amp_gain[self.Type+rods] + (dc_offset - 0.5*self.Offset_diff)/self.DC_gain)


            # convert amplifier voltage to AWG bits
            voltage = np.array(voltage)
            v_bits = voltage * (self.Max_bits / self.Awg_gain)

            writer = csv.writer(outfile, lineterminator='\n')
            for i, v in zip(range(self.Seg_len), v_bits):
                writer.writerow((i, v))

            outfile.close()
        return

    def create_all_waveforms(self, powered):
        if powered ==2:
            rods = "13"
            if self.Type == "CROD":
                self.create_accumulation_waveforms(1, rods)
                self.create_ramping_waveforms(2, rods)
                self.create_final_tune_waveforms(3, rods)
                self.create_final_tune_waveforms(4, rods)

            if self.Type == "FC":
                self.create_accumulation_waveforms(1, rods)
                self.create_ramping_waveforms(2, rods)
                self.create_final_tune_waveforms(3, rods)
                self.create_gate_drop_waveforms(4, rods)

            if self.Type == "MCP":
                self.create_accumulation_waveforms(1, rods)
                self.create_ramping_waveforms(2, rods)
                self.create_final_tune_waveforms(3, rods)
                self.create_final_tune_waveforms(4, rods)

        else:
            rods = "13"
            if self.Type == "CROD":
                self.create_accumulation_waveforms(1, rods)
                self.create_ramping_waveforms(2, rods)
                self.create_final_tune_waveforms(3, rods, self.Offset)
                self.create_final_tune_waveforms(4, rods, self.Offset)

            if self.Type == "FC":
                self.create_accumulation_waveforms(1, rods)
                self.create_ramping_waveforms(2, rods)
                self.create_final_tune_waveforms(3, rods, self.Offset)
                self.create_final_tune_waveforms(4, rods, self.Offset_drop)

            if self.Type == "MCP":
                self.create_accumulation_waveforms(1, rods)
                self.create_ramping_waveforms(2, rods)
                self.create_final_tune_waveforms(3, rods, self.Offset)
                self.create_final_tune_waveforms(4, rods, self.Offset_drop)

            rods = "24"
            if self.Type == "CROD":
                self.create_accumulation_waveforms(1, rods)
                self.create_ramping_waveforms(2, rods)
                self.create_final_tune_waveforms(3, rods, self.Offset)
                self.create_final_tune_waveforms(4, rods, self.Offset)

            if self.Type == "FC":
                self.create_accumulation_waveforms(1, rods)
                self.create_ramping_waveforms(2, rods)
                self.create_final_tune_waveforms(3, rods, self.Offset)
                self.create_final_tune_waveforms(4, rods, self.Offset_drop)

            if self.Type == "MCP":
                self.create_accumulation_waveforms(1, rods)
                self.create_ramping_waveforms(2, rods)
                self.create_final_tune_waveforms(3, rods, self.Offset)
                self.create_final_tune_waveforms(4, rods, self.Offset_drop)



