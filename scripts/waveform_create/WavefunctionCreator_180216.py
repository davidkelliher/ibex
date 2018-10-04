# Code creates txt files containing the desired waveforms for a variety of tunes and saves them to a file
# Code should also include the sweep in tune from the starting tune
# Code should define the starting tune, this waveform then remains the same
# Perhaps naming the sweep files and the second tune files with the same number will make it easier.

from __future__ import division
from functions_partial_180115 import *


# Enter desired parameters:

# Tune at which plasma is accumulated
accumulation_tune = 0.114

# tune that sweep starts at
initial_tune = 0.26#0.114 #0.114 #0.114

# tune that sweep ends at
final_tune = 0.3

# tune divisions covered
tune_points = 1

# Segment length for the waveforms
seg_len = 100

# how many rods are powered 2 or 4?
rods_powered = 4

# Time taken for tune ramp
ramp_time = 3e-6
# time increment plotted in waveforms
time_increment = 1e-8
# time increment plotted in ramping waveforms
ramp_time_increment = 1e-8

# voltage offset on rods
rod_offset = 10.0
# voltage offset on endcaps
endcap_offset = 13.0
#voltage offset on endcap after gate drop (normally zero)
offset_drop = 0

# Need to include amplifier calibration

# Amplifier 1 gain
A1_gain = 45.072#46.71 #46.64 # #46.78

# Amplifier 2 gain
# 
A2_gain = 51.75#46.71*1.09

# Amplifier 3 gain
A3_gain = 48.41#48.8888 #50.11

# Amplifier 2 gain
A4_gain = 50.911


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
    import ibex_optics
    op = ibex_optics.optics(f_rf=1.0, npts=1000)
    accumulation_voltage = tune_to_voltage_ibex_optics(accumulation_tune)

    tune_x = np.linspace(initial_tune, final_tune, tune_points)    
    voltage_array = []
    for tune in tune_x:
        v = tune_to_voltage_ibex_optics(tune)
        voltage_array.append(v)


if rods_powered == 2:
    voltage_array = voltage_array * 2 
    accumulation_voltage = accumulation_voltage * 2


print "v, 2v ",v, 2*v

amp_connect = {'CROD13':A1_gain, 'CROD24': A3_gain, 'FC13':A2_gain, 'FC24':A4_gain}
awg_connect = {'CROD13':'C1', 'CROD24': 'C2', 'FC13':'C3', 'FC24':'C4'}

outfile = open('Summary.txt', 'w')
outfile.write("Accumulation tune: \t")
outfile.write("%f\n" % accumulation_tune)
outfile.write("Accumulation voltage: \t")
outfile.write("%f\n" % accumulation_voltage)
outfile.write("Final voltage and tune\n")
for i in range(len(voltage_array)):
    outfile.write("%f," % voltage_array[i])
    outfile.write("%f\n" % tune_x[i])
outfile.close()


Rods = Waveforms('CROD', seg_len, rod_offset, accumulation_voltage, voltage_array, ramp_time * freq, amp_connect, awg_connect, AWG_gain, max_bits)
FC_endcap = Waveforms('FC', seg_len, endcap_offset, accumulation_voltage, voltage_array, ramp_time* freq, amp_connect, awg_connect, AWG_gain, max_bits, endcap_offset_drop=offset_drop)
#MCP_endcap = Waveforms('MCP', seg_len, endcap_offset, accumulation_voltage, voltage_array, ramp_time*freq, amp_connect, AWG_gain, max_bits)


Rods.create_all_waveforms(rods_powered)
FC_endcap.create_all_waveforms(rods_powered)
#MCP_endcap.create_all_waveforms(rods_powered)


