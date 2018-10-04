from __future__ import division
import numpy as np
import matplotlib.pyplot as plt
import math
import sys
import csv
from scipy.optimize import newton
import ibex_optics_pert

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

    op = ibex_optics_pert.optics(f_rf=1.0, npts=1000)

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
        self.awg_DC_offset = {'C1':0.0028, 'C2':0.0072, 'C3':0.04, 'C4':0.005} #15/1/18
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

    def create_accumulation_waveforms(self, seg, rods, phase, pert):
        outfile = open(self.Type + str(rods) + '_seg_' + str(seg) +'.csv', 'w')
        voltage = []

        DCawgoff = self.awg_DC_offset[self.awg_connect[self.Type+rods]]

        if self.Type == 'FC':
            accumulation_voltage = self.Accumulation_voltage/2
        else:
            accumulation_voltage = self.Accumulation_voltage
        
        print "outfile ",outfile

        if rods == "13":
            for i in range(self.Seg_len):
                voltage.append(accumulation_voltage * np.sin((i * 2 * np.pi/ self.Seg_len)+ phase)/self.Amp_gain[self.Type+rods] + (self.Offset/self.DC_gain) + DCawgoff)
        else:
            for i in range(self.Seg_len):
                voltage.append(-1*accumulation_voltage * np.sin((i * 2 * np.pi / self.Seg_len)+ phase)/self.Amp_gain[self.Type+rods] + (self.Offset/self.DC_gain) + DCawgoff)


        # convert amplifier voltage to AWG bits
        voltage = np.array(voltage)
        accumulation_v_bits = voltage*(self.Max_bits / self.Awg_gain)

        
        writer = csv.writer(outfile, lineterminator='\n')
        for i, v in zip(range(self.Seg_len), accumulation_v_bits):
            writer.writerow((i, v))

        outfile.close()

        return

    def  create_ramping_waveforms(self, seg, rods, phase, pert):

        DCawgoff = self.awg_DC_offset[self.awg_connect[self.Type+rods]]

        if self.Type == 'FC':
            voltage_array = self.Voltage_array/2
            accumulation_voltage = self.Accumulation_voltage /2
        else:
            voltage_array = self.Voltage_array
            accumulation_voltage = self.Accumulation_voltage
        
        for j in range(len(self.Voltage_array)):

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
                        voltage.append((((((voltage_array[j]-accumulation_voltage)*((l*self.Seg_len) + i))/(self.Ramp_periods * self.Seg_len)) + accumulation_voltage)
                         * np.sin((i * 2 * np.pi / self.Seg_len)+ phase))/self.Amp_gain[self.Type+rods] + self.Offset/self.DC_gain + DCawgoff)
                    else:
                        voltage.append((((((voltage_array[j]-accumulation_voltage)*((l*self.Seg_len) + i))/(self.Ramp_periods * self.Seg_len)) + accumulation_voltage)
                         * -1 * np.sin((i * 2 * np.pi / self.Seg_len)+ phase))/self.Amp_gain[self.Type+rods] + self.Offset/self.DC_gain + DCawgoff)

            voltage = np.array(voltage)
            v_bits = voltage * (self.Max_bits / self.Awg_gain)

            writer = csv.writer(outfile, lineterminator='\n')
            for i, v in zip(number, v_bits):
                writer.writerow((i, v))

            outfile.close()


        return

    def create_final_tune_waveforms(self, seg, rods, phase, dc_offset, pert):

        DCawgoff = self.awg_DC_offset[self.awg_connect[self.Type+rods]]

        if self.Type == 'FC':
            voltage_array = self.Voltage_array/2
        else:
            voltage_array = self.Voltage_array

        print "seg, final dc offset: ",seg, self.Offset
        
        for j in range(len(self.Voltage_array)):

            if pert[1] == 0.0:
                outfile = open(self.Type + str(rods) + '_seg_' + str(seg) + '_' + str(2*j) + '.csv', 'w')
            else:
                outfile = open(self.Type + str(rods) + '_seg_' + str(seg) + '_' + str((2*(j+1)) - 1) + '.csv', 'w')
            voltage = []
            number = []

            for i in range(self.Seg_len):
                number.append(i)

            if rods == "13":
                for i in range(self.Seg_len):
                    voltage.append(voltage_array[j] * np.sin((i *  2 * np.pi / self.Seg_len)+ phase) /self.Amp_gain[self.Type+rods] + (dc_offset/self.DC_gain) + DCawgoff)
            else:
                for i in range(self.Seg_len):
                    voltage.append(-1 * voltage_array[j] * np.sin((i * 2 * np.pi / self.Seg_len)+ phase) /self.Amp_gain[self.Type+rods] + (dc_offset/self.DC_gain) + DCawgoff)


            voltage = np.array(voltage)
            v_bits = voltage * (self.Max_bits / self.Awg_gain)

            writer = csv.writer(outfile, lineterminator='\n')
            for i, v in zip(range(self.Seg_len), v_bits):
                writer.writerow((i, v))

            outfile.close()
        return



    def create_blank_waveform_accumulation(self, seg, rods, phase, pert):

        DCawgoff = self.awg_DC_offset[self.awg_connect[self.Type + rods]]

        for j in range(len(self.Voltage_array)):

            outfile = open(self.Type + str(rods) + '_seg_' + str(seg) + '.csv', 'w')
            voltage = []
            number = []

            for i in range(self.Seg_len):
                number.append(i)

            print "rods in gate drop ", rods
            print "seg, self.Offset_drop ", seg, self.Offset_drop
            if rods == "13":
                for i in range(self.Seg_len):
                    voltage.append((self.Offset/self.DC_gain) + DCawgoff)
            else:
                for i in range(self.Seg_len):
                    voltage.append((self.Offset/self.DC_gain) + DCawgoff)
            # convert amplifier voltage to AWG bits
            voltage = np.array(voltage)
            v_bits = voltage * (self.Max_bits / self.Awg_gain)

            writer = csv.writer(outfile, lineterminator='\n')
            for i, v in zip(range(self.Seg_len), v_bits):
                writer.writerow((i, v))

            outfile.close()
        return

    def create_blank_waveform(self, seg, rods, phase, dc_offset, pert):

        DCawgoff = self.awg_DC_offset[self.awg_connect[self.Type + rods]]

        for j in range(len(self.Voltage_array)):

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
                    voltage.append((dc_offset/self.DC_gain) + DCawgoff)
            else:
                for i in range(self.Seg_len):
                    voltage.append((dc_offset/self.DC_gain) + DCawgoff)
            # convert amplifier voltage to AWG bits
            voltage = np.array(voltage)
            v_bits = voltage * (self.Max_bits / self.Awg_gain)

            writer = csv.writer(outfile, lineterminator='\n')
            for i, v in zip(range(self.Seg_len), v_bits):
                writer.writerow((i, v))

            outfile.close()
        return

    def create_blank_ramp_waveform(self, seg, rods, phase, pert):

        DCawgoff = self.awg_DC_offset[self.awg_connect[self.Type + rods]]

        for j in range(len(self.Voltage_array)):

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
                        voltage.append((self.Offset/self.DC_gain) + DCawgoff)
                    else:
                        voltage.append((self.Offset/self.DC_gain) + DCawgoff)


            # convert amplifier voltage to AWG bits
            voltage = np.array(voltage)
            v_bits = voltage * (self.Max_bits / self.Awg_gain)

            writer = csv.writer(outfile, lineterminator='\n')
            for i, v in zip(number, v_bits):
                writer.writerow((i, v))

            outfile.close()

        return

    def create_perturbing_waveform(self, seg, rods, phase, pert):

        DCawgoff = self.awg_DC_offset[self.awg_connect[self.Type + rods]]
        fraction_moved = int(round((phase / 360.0) * self.Seg_len))

        for j in range(len(self.Voltage_array)):

            if pert[1] == 0.0:
                outfile = open(self.Type + str(rods) + '_seg_' + str(seg) + '_' + str(2*j) + '.csv', 'w')
            else:
                outfile = open(self.Type + str(rods) + '_seg_' + str(seg) + '_' + str((2*(j+1)) - 1) + '.csv', 'w')
            voltage = []
            number = []

            # Add square pertubation which is on for one rf period in however many super-periods
            
            for i in range(int(self.Seg_len *(1e6/pert[0]))):
                number.append(i)

            print "rods in gate drop ", rods
            print "seg, self.Offset_drop ", seg, self.Offset_drop
            if rods == "13":
                arr = np.concatenate((np.linspace(0, 0, (self.Seg_len + fraction_moved)), np.linspace(1, 1, self.Seg_len),
                                      np.linspace(0, 0, (int(self.Seg_len *(1e6/pert[0]) - 2*self.Seg_len) - fraction_moved))))
                voltage = (pert[1] * arr /self.Amp_gain[self.Type+rods]) + (self.Offset/self.DC_gain) + DCawgoff
            else:
                arr = np.concatenate((np.linspace(0, 0, (self.Seg_len + fraction_moved)), np.linspace(1, 1, self.Seg_len),
                                      np.linspace(0, 0, (int(self.Seg_len *(1e6/pert[0]) - 2*self.Seg_len) - fraction_moved))))
                voltage = (-pert[1] * arr /self.Amp_gain[self.Type+rods]) + (self.Offset/self.DC_gain) + DCawgoff


            # convert amplifier voltage to AWG bits
            voltage = np.array(voltage)
            v_bits = voltage * (self.Max_bits / self.Awg_gain)

            writer = csv.writer(outfile, lineterminator='\n')
            for i, v in zip(range(int(self.Seg_len * (1e6/pert[0]))), v_bits):
                writer.writerow((i, v))

            outfile.close()
        return


    def create_all_waveforms(self, powered, pertubation):
        FC_phase_13 = -np.radians(8.0)
        FC_phase_24 = -np.radians(5.5)
        CROD_phase_13 = np.radians(0.0)
        CROD_phase_24 = np.radians(0.0)
        if powered == 2:
            if pertubation == False:
                rods = "13"
                if self.Type == "CROD":
                    self.create_accumulation_waveforms(1, rods, CROD_phase_13, pertubation)
                    self.create_ramping_waveforms(2, rods, CROD_phase_13, pertubation)
                    self.create_final_tune_waveforms(3, rods, CROD_phase_13, self.Offset, pertubation)
                    self.create_final_tune_waveforms(4, rods, CROD_phase_13, self.Offset, pertubation)

                if self.Type == "FC":
                    self.create_accumulation_waveforms(1, rods, FC_phase_13, pertubation)
                    self.create_ramping_waveforms(2, rods, FC_phase_13, pertubation)
                    self.create_final_tune_waveforms(3, rods, FC_phase_13, self.Offset, pertubation)
                    self.create_gate_drop_waveforms(4, rods, FC_phase_13, self.Offset_drop, pertubation)

                if self.Type == "MCP":
                    self.create_accumulation_waveforms(1, rods, 0, pertubation)
                    self.create_ramping_waveforms(2, rods, 0, pertubation)
                    self.create_final_tune_waveforms(3, rods, 0, self.Offset, pertubation)
                    self.create_final_tune_waveforms(4, rods, 0, self.Offset, pertubation)

            else:
                rods = "13"
                if self.Type == "CROD":
                    self.create_accumulation_waveforms(1, rods, CROD_phase_13, pertubation)
                    self.create_ramping_waveforms(2, rods, CROD_phase_13, pertubation)
                    self.create_final_tune_waveforms(3, rods, CROD_phase_13, self.Offset, pertubation)
                    self.create_final_tune_waveforms(4, rods, CROD_phase_13, self.Offset, pertubation)

                if self.Type == "FC":
                    self.create_accumulation_waveforms(1, rods, FC_phase_13, pertubation)
                    self.create_ramping_waveforms(2, rods, FC_phase_13, pertubation)
                    self.create_final_tune_waveforms(3, rods, FC_phase_13, self.Offset, pertubation)
                    self.create_final_tune_waveforms(4, rods, FC_phase_13, self.Offset_drop, pertubation)

                if self.Type == "MCP":
                    self.create_accumulation_waveforms(1, rods, 0, pertubation)
                    self.create_ramping_waveforms(2, rods, 0, pertubation)
                    self.create_final_tune_waveforms(3, rods, 0, self.Offset, pertubation)
                    self.create_final_tune_waveforms(4, rods, 0, self.Offset, pertubation)

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
            rods = "13"
            if self.Type == "CROD":
                self.create_accumulation_waveforms(1, rods, CROD_phase_13, pertubation)
                self.create_ramping_waveforms(2, rods, CROD_phase_13, pertubation)
                self.create_final_tune_waveforms(3, rods, CROD_phase_13, self.Offset, pertubation)
                self.create_final_tune_waveforms(4, rods, CROD_phase_13, self.Offset, pertubation)

            if self.Type == "FC":
                self.create_accumulation_waveforms(1, rods, FC_phase_13, pertubation)
                self.create_ramping_waveforms(2, rods, FC_phase_13, pertubation)
                self.create_final_tune_waveforms(3, rods, FC_phase_13, self.Offset, pertubation)
                self.create_final_tune_waveforms(4, rods,FC_phase_13, self.Offset_drop, pertubation)

            if self.Type == "MCP":
                self.create_accumulation_waveforms(1, rods, 0, pertubation)
                self.create_ramping_waveforms(2, rods, 0, pertubation)
                self.create_final_tune_waveforms(3, rods, 0, self.Offset, pertubation)
                self.create_final_tune_waveforms(4, rods, 0, self.Offset, pertubation)

            rods = "24"
            #self.set_amp_gain(50.11)
            if self.Type == "CROD":
                self.create_accumulation_waveforms(1, rods, CROD_phase_24, pertubation)
                self.create_ramping_waveforms(2, rods, CROD_phase_24, pertubation)
                self.create_final_tune_waveforms(3, rods, CROD_phase_24, self.Offset, pertubation)
                self.create_final_tune_waveforms(4, rods, CROD_phase_24, self.Offset, pertubation)

            if self.Type == "FC":
                self.create_accumulation_waveforms(1, rods, FC_phase_24, pertubation)
                self.create_ramping_waveforms(2, rods, FC_phase_24, pertubation)
                self.create_final_tune_waveforms(3, rods, FC_phase_24, self.Offset, pertubation)
                self.create_final_tune_waveforms(4, rods, FC_phase_24, self.Offset_drop, pertubation)

            if self.Type == "MCP":
                self.create_accumulation_waveforms(1, rods, 0, pertubation)
                self.create_ramping_waveforms(2, rods, 0, pertubation)
                self.create_final_tune_waveforms(3, rods, 0, self.Offset, pertubation)
                self.create_final_tune_waveforms(4, rods, 0, self.Offset, pertubation)



