# Code creates txt files containing the desired waveforms for a variety of tunes and saves them to a file
# Code should also include the sweep in tune from the starting tune
# Code should define the starting tune, this waveform then remains the same
# Perhaps naming the sweep files and the second tune files with the same number will make it easier.

from __future__ import division
from functions_pertubation_splittunes import *
import numpy as np

# Enter desired parameters:

# Tune at which plasma is accumulated (equal in both transverse planes)
accumulation_tune = 0.15

# tune that sweep starts at
initial_tune_x = 0.3 #0.114
initial_tune_y = 0.32

# tune that sweep ends at
final_tune_x = 0.4
final_tune_y = 0.2

# tune divisions covered
tune_points = 1

# Segment length for the waveforms
# Note that segment length must be devisable by four.
seg_len = 100

# how many rods are powered 2 or 4?
rods_powered = 4
# pertubation? [freq, amp, rf periods, with or without alternate measurements, with or without wait]
# for with or without alternate measurements, use 0 if you dont also want to run without a perturbation,
# use 1 if you will also run without perturbation
# With or without wait is for the case where you want to leave the plasma for a while
# after the ramp before applying perturbation. No wait = 0, wait = no. or rf periods to wait.
pertubation = [1.0e6, 0.0, 1, 0, 0]

# Time taken for tune ramp
ramp_time = 100e-6
# time increment plotted in waveforms
#time_increment = 1e-8
# time increment plotted in ramping waveforms
#ramp_time_increment = 1e-8

# voltage offset on rods
rod_offset = 10.0
# voltage offset on endcaps
endcap_offset = 25.0
#voltage offset on endcap after gate drop (normally zero)
offset_drop = 0.0



# Need to include amplifier calibration

# Amplifier 1 gain
A1_gain = 50.0

# Amplifier 2 gain
# 
A2_gain = 50.0*1.00297776

# Amplifier 3 gain
A3_gain = 50.0*0.9657399

# Amplifier 2 gain
A4_gain = 50.0*0.97020645


# AWG gain BE CAREFUL - THIS CAN BE ALTERED ON THE LABVIEW!!!!
# not that this gives max amplitude not max peak to peak
AWG_gain = 5 / 2

# Mass of argon
argon_mass = 39.948
# rf frequency
freq = 1e6
# time of 1 rf period
time_length = 1 / freq
# trap radius
r0 = 5e-3
# correction to trap radius from calibration
calibration = 1
# charge
charge = 1.60217733e-19
# speed of light
speed_of_light = 2.99792458e8
unified_atomic_mass_unit = 1.6605e-27
qm_argon = charge / (argon_mass * unified_atomic_mass_unit)

# Max no. of bits, note that this is amplitude
max_bits = 2 ** 15
# 1E8 samples per second is the limit of the system


####################################################

# option to use Mathematica or approximate equation to convert tune to voltage

use_mathematica = False
if use_mathematica:
    # Use the mathematica to convert the tune to a voltage. Read output file
    tune_x, tune_y, rf_voltage, offset_voltage = readfiledata('V-DC.txt')
else:
    # Use ibex_optics script to do conversion
    # assumes equal tunes in both transverse plane
    #import ibex_optics_pert
    #import ibex_optics_181109# (this will allow split tunes - to be tested here)
    #op = ibex_optics_pert.optics(f_rf=1.0, npts=1000)
   
    accumulation_voltage, _, _ = tune_to_voltages(accumulation_tune, accumulation_tune)
    
    tune_x_a = np.linspace(initial_tune_x, final_tune_x, tune_points)
    tune_y_a = np.linspace(initial_tune_y, final_tune_y, tune_points)
    
    print "tune_x array ",tune_x_a
    v0_array = []
    u0_array = []
    tune_x_out = []
    tune_y_out = []
    for tune_x, tune_y in zip(tune_x_a, tune_y_a):
        
        v, u, tune_out = tune_to_voltages(tune_x, tune_y)
        v0_array.append(v)
        u0_array.append(u)
        tune_x_out.append(tune_out[0])
        tune_y_out.append(tune_out[1])
        
    print "RF voltage amplitudes ",v0_array
    print "DC voltages ",u0_array

    v0_array = np.array(v0_array)
    u0_array =  np.array(u0_array)
    
    if tune_points > 1:
        plt.subplot(211)
        plt.plot(tune_x_a, tune_y_a, 'ko-')
        plt.plot(tune_x_out, tune_y_out, 'ro-')
        plt.xlabel('tune x')
        plt.ylabel('tune y')
        plt.subplot(212)
        plt.plot(v0_array, u0_array, 'ko-')
        plt.xlabel('V0')
        plt.ylabel('U0')        
        plt.show()
    


if rods_powered == 2:
    v0_array = v0_array * 2
    accumulation_voltage = accumulation_voltage * 2
    rod_offset = rod_offset
    endcap_offset = endcap_offset
    offset_drop = offset_drop

amp_connect = {'CROD13':A1_gain, 'CROD24': A3_gain, 'FC13':A2_gain, 'FC24':A4_gain}
awg_connect = {'CROD13':'C1', 'CROD24': 'C2', 'FC13':'C3', 'FC24':'C4'}

outfile = open('Summary.txt', 'w')
outfile.write("Accumulation tune: \t")
outfile.write("%f\n" % accumulation_tune)
outfile.write("Accumulation voltage: \t")
outfile.write("%f\n" % accumulation_voltage)
outfile.write("Final voltage (V0, U0) and tunes \n")
for i in range(len(v0_array)):
    outfile.write("%f, " % v0_array[i])
    outfile.write("%f, " % u0_array[i])
    outfile.write("%f, " % tune_x_a[i])
    outfile.write("%f\n" % tune_y_a[i])
outfile.close()


Rods = Waveforms('CROD', seg_len, rod_offset, accumulation_voltage, v0_array, u0_array, ramp_time * freq, amp_connect, awg_connect, AWG_gain, max_bits)
FC_endcap = Waveforms('FC', seg_len, endcap_offset, accumulation_voltage, v0_array, u0_array, ramp_time* freq, amp_connect, awg_connect, AWG_gain, max_bits, endcap_offset_drop=offset_drop)
#MCP_endcap = Waveforms('MCP', seg_len, endcap_offset, accumulation_voltage, voltage_array, ramp_time*freq, amp_connect, AWG_gain, max_bits)


Rods.create_all_waveforms(rods_powered, pertubation)
FC_endcap.create_all_waveforms(rods_powered, pertubation)
#MCP_endcap.create_all_waveforms(rods_powered)

