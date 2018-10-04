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

    def create_fixed_waveforms(self, seg, rods, rf_amp, rf_polarity, dc_offset, file_index=None):
        """Single, fixed waveform """

        print "fixed waveform: rods, seg, dc_offset ",self.Type, rods, seg, dc_offset
        
        pts_a = np.arange(self.Seg_len)

        
        if self.Type == 'CROD':
            if rods in '24':
                ampgain = self.Amp_gain['CROD24']
            elif rods in '13':
                ampgain = self.Amp_gain['CROD13']
        if self.Type == 'FC':
            if rods in '24':
                ampgain = self.Amp_gain['FC24']
            elif rods in '13':
                ampgain = self.Amp_gain['FC13']      

        
        voltage = rf_polarity*rf_amp * np.sin(pts_a * 2 * np.pi / self.Seg_len)/ampgain + (dc_offset/self.DC_gain)

           
        # convert amplifier voltage to AWG bits
        accumulation_v_bits = voltage*(self.Max_bits / self.Awg_gain)

        if file_index == None:
            outfile = open(self.Type + str(rods) + '_seg_' + str(seg) +'.csv', 'w')
        else:
            outfile = open(self.Type + str(rods) + '_seg_' + str(seg) +'_'+str(file_index)+'.csv', 'w')
        writer = csv.writer(outfile, lineterminator='\n')
        for i, v in zip(range(self.Seg_len), accumulation_v_bits):
            writer.writerow((i, v))

        outfile.close()

        return

    def  create_ramping_waveforms(self, seg, rods, rf_amp_initial_a, rf_amp_final_a, dc_offset):
        """Ramp from initial to final rf amplitudes given arrays rf_amp_initial_a, rf_amp_final_a"""
        

        npts_ramp = self.Ramp_periods * self.Seg_len

        if self.Type == 'CROD':
            if rods in '24':
                ampgain = self.Amp_gain['CROD24']
            elif rods in '13':
                ampgain = self.Amp_gain['CROD13']
        if self.Type == 'FC':
            if rods in '24':
                ampgain = self.Amp_gain['FC24']
            elif rods in '13':
                ampgain = self.Amp_gain['FC13']

                     
        
        for j in range(len(rf_amp_final_a)):

            voltage = []

            for l in range(int(self.Ramp_periods)):
                nl = l*self.Seg_len
                for i in range(self.Seg_len):

                    rf_amp = (rf_amp_final_a[j]-rf_amp_initial_a[j])*(nl + i)/npts_ramp + rf_amp_initial_a[j]
                        
                    dc_part = 0.5*self.Offset_diff*(nl + i)/npts_ramp 

                    if rods == "13":
                        voltage.append(rf_amp*(np.sin(i * 2 * np.pi / self.Seg_len))/ampgain + (dc_offset + dc_part)/self.DC_gain)
                    else:
                        voltage.append(-rf_amp*(np.sin(i * 2 * np.pi / self.Seg_len))/ampgain + (dc_offset - dc_part) /self.DC_gain)

            
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

        print "final tune waveform: rods, seg, dc_offset ",self.Type, rods, seg, dc_offset

        if self.Type == 'CROD':
            if rods in '24':
                ampgain = self.Amp_gain['CROD24']
            elif rods in '13':
                ampgain = self.Amp_gain['CROD13']
        if self.Type == 'FC':
            if rods in '24':
                ampgain = self.Amp_gain['FC24']
            elif rods in '13':
                ampgain = self.Amp_gain['FC13']
                
            
        for j in range(len(self.Voltage_array)):

            outfile = open(self.Type + str(rods)  + '_seg_' + str(seg) + '_'+ str(j) +'.csv', 'w')
            voltage = []
            number = []

            for i in range(self.Seg_len):
                number.append(i)

            if rods == "13":
                for i in range(self.Seg_len):
                    voltage.append(self.Voltage_array[j] * np.sin(i * 2 * np.pi / self.Seg_len)/ampgain + (dc_offset + 0.5*self.Offset_diff)/self.DC_gain )
            else:
                for i in range(self.Seg_len):
                    voltage.append(-1 * self.Voltage_array[j] * np.sin(i * 2 * np.pi / self.Seg_len)/ampgain + (dc_offset - 0.5*self.Offset_diff)/self.DC_gain)


            # convert amplifier voltage to AWG bits
            voltage = np.array(voltage)
            v_bits = voltage * (self.Max_bits / self.Awg_gain)

            writer = csv.writer(outfile, lineterminator='\n')
            for i, v in zip(range(self.Seg_len), v_bits):
                writer.writerow((i, v))

            outfile.close()
        return

    def create_all_waveforms(self, powered):
        
        rf_amp_initial_a = np.array([self.Accumulation_voltage]*len(self.Voltage_array))
        
        if powered ==2:

            #power "13"
            rods = "13"
            if self.Type == "CROD":
                self.create_fixed_waveforms(1, rods, self.Accumulation_voltage, 1, self.Offset)
                self.create_ramping_waveforms(2, rods, rf_amp_initial_a, self.Voltage_array,  self.Offset)
                self.create_final_tune_waveforms(3, rods, self.Offset)
                self.create_final_tune_waveforms(4, rods, self.Offset)

            if self.Type == "FC":
                self.create_fixed_waveforms(1, rods, self.Accumulation_voltage, 1, self.Offset)
                self.create_ramping_waveforms(2, rods, rf_amp_initial_a, self.Voltage_array, self.Offset)
                self.create_final_tune_waveforms(3, rods, self.Offset)
                self.create_final_tune_waveforms(4, rods, self.Offset_drop)

            if self.Type == "MCP":
                self.create_fixed_waveforms(1, rods, self.Accumulation_voltage, 1, self.Offset)
                self.create_ramping_waveforms(2, rods)
                self.create_final_tune_waveforms(3, rods, self.Offset)
                self.create_final_tune_waveforms(4, rods, self.Offset_drop)

            
            #dipole perturbation and DC to central rods 2 and 4
            rods = "2"
            vp = 2
            rf_amp_vp_a = np.array([vp])
            rf_amp_zero_a = np.array([0])
            if self.Type == "CROD":
                self.create_fixed_waveforms(1, rods, vp, -1, self.Offset)
                self.create_ramping_waveforms(2, rods,  rf_amp_vp_a, rf_amp_vp_a, self.Offset)
                self.create_fixed_waveforms(3, rods, vp, -1, self.Offset, 0)
                self.create_fixed_waveforms(4, rods, vp, -1, self.Offset, 0)

            rods = "4"
            vp = 2
            rf_amp_vp_a = np.array([vp])
            rf_amp_zero_a = np.array([0])
            if self.Type == "CROD":
                self.create_fixed_waveforms(1, rods, vp, 1, self.Offset)
                self.create_ramping_waveforms(2, rods,  rf_amp_vp_a, rf_amp_vp_a, self.Offset)
                self.create_fixed_waveforms(3, rods, vp, 1, self.Offset, 0)
                self.create_fixed_waveforms(4, rods, vp, 1, self.Offset, 0)

                
            if self.Type == "FC":
                self.create_fixed_waveforms(1, rods, 0, -1, self.Offset)
                self.create_ramping_waveforms(2, rods,  rf_amp_zero_a, rf_amp_zero_a, self.Offset)
                self.create_final_tune_waveforms(3, rods, self.Offset)
                self.create_final_tune_waveforms(4, rods, self.Offset_drop)
                
        else:
            rods = "13"
            if self.Type == "CROD":
                self.create_fixed_waveforms(1, rods, self.Accumulation_voltage, 1, self.Offset)
                self.create_ramping_waveforms(2, rods, rf_amp_initial_a, self.Voltage_array, self.Offset)
                self.create_final_tune_waveforms(3, rods, self.Offset)
                self.create_final_tune_waveforms(4, rods, self.Offset)

            if self.Type == "FC":
                self.create_fixed_waveforms(1, rods, self.Accumulation_voltage, 1, self.Offset)
                self.create_ramping_waveforms(2, rods, rf_amp_initial_a, self.Voltage_array,  self.Offset)
                self.create_final_tune_waveforms(3, rods, self.Offset)
                self.create_final_tune_waveforms(4, rods, self.Offset_drop)

            if self.Type == "MCP":
                self.create_fixed_waveforms(1, rods, self.Accumulation_voltage, 1, self.Offset)
                self.create_ramping_waveforms(2, rods, rf_amp_initial_a, self.Voltage_array,  self.Offset)
                self.create_final_tune_waveforms(3, rods, self.Offset)
                self.create_final_tune_waveforms(4, rods, self.Offset_drop)

            rods = "24"
            if self.Type == "CROD":
                self.create_fixed_waveforms(1, rods, self.Accumulation_voltage, -1, self.Offset)
                self.create_ramping_waveforms(2, rods,rf_amp_initial_a, self.Voltage_array, self.Offset)
                self.create_final_tune_waveforms(3, rods, self.Offset)
                self.create_final_tune_waveforms(4, rods, self.Offset)

            if self.Type == "FC":
                self.create_fixed_waveforms(1, rods, self.Accumulation_voltage, -1, self.Offset)
                self.create_ramping_waveforms(2, rods, rf_amp_initial_a, self.Voltage_array,  self.Offset)
                self.create_final_tune_waveforms(3, rods, self.Offset)
                self.create_final_tune_waveforms(4, rods, self.Offset_drop)

            if self.Type == "MCP":
                self.create_fixed_waveforms(1, rods, self.Accumulation_voltage, -1, self.Offset)
                self.create_ramping_waveforms(2, rods, rf_amp_initial_a, self.Voltage_array,  self.Offset)
                self.create_final_tune_waveforms(3, rods, self.Offset)
                self.create_final_tune_waveforms(4, rods, self.Offset_drop)



