# Code creates txt files containing the desired waveforms for a variety of tunes and saves them to a file
# Code should also include the sweep in tune from the starting tune
# Code should define the starting tune, this waveform then remains the same
# Perhaps naming the sweep files and the second tune files with the same number will make it easier.

from __future__ import division
from functions_pertubation import *


# Enter desired parameters:

# Tune at which plasma is accumulated
accumulation_tune = 0.114

# tune that sweep starts at
initial_tune = 0.2 #0.114

# tune that sweep ends at
final_tune = 0.2

# tune divisions covered
tune_points = 10

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
pertubation = [1e6, 0.0, 500, 0, 0]

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
    import ibex_optics_pert
    op = ibex_optics_pert.optics(f_rf=1.0, npts=1000)
    accumulation_voltage = tune_to_voltage_ibex_optics(accumulation_tune)

    tune_x = np.linspace(initial_tune, final_tune, tune_points)    
    voltage_array = []
    for tune in tune_x:
        if voltage_array != []:
            vguess = voltage_array[-1]
        else:
            vguess = 80
            
        v = tune_to_voltage_ibex_optics(tune, vguess)
        voltage_array.append(v)

    


if rods_powered == 2:
    voltage_array = np.array(voltage_array) * 2
    accumulation_voltage = accumulation_voltage * 2
    rod_offset = rod_offset
    endcap_offset = endcap_offset
    offset_drop = offset_drop


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


Rods.create_all_waveforms(rods_powered, pertubation)
FC_endcap.create_all_waveforms(rods_powered, pertubation)
#MCP_endcap.create_all_waveforms(rods_powered)

