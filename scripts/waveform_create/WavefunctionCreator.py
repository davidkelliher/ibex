# Code creates txt files containing the desired waveforms for a variety of tunes and saves them to a file
# Code should also include the sweep in tune from the starting tune
# Code should define the starting tune, this waveform then remains the same
# Perhaps naming the sweep files and the second tune files with the same number will make it easier.

from functions import *


# Enter desired parameters:

# Tune at which plasma is accumulated
accumulation_tune = 0.09

# tune that sweep starts at
initial_tune = 0.18

# tune that sweep ends at
final_tune = 0.18

# tune divisions covered
tune_points = 1

# Segment length for the waveforms
seg_len = 100

# how many rods are powered 2 or 4?
rods_powered = 4

# Time taken for tune ramp
ramp_time = 100e-6
# time increment plotted in waveforms
time_increment = 1e-8
# time increment plotted in ramping waveforms
ramp_time_increment = 1e-8

# voltage offset on rods
rod_offset = 8
# voltage offset on endcaps
endcap_offset = 25

# Need to include amplifier calibration

# Amplifier 1 gain
# Amplifier rods 13
A1_gain = 46.78

# Amplifier 2 gain
# FC endcap 13
A4_gain = 50.85

# Amplifier 3 gain
# MCP endcap 24
A3_gain = 50.11

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
print max_bits

####################################################

# option to use Mathematica or approximate equation to convert tune to voltage

use_mathematica = False
if use_mathematica:
    # Use the mathematica to convert the tune to a voltage
    tune_x, tune_y, rf_voltage, offset_voltage = readfiledata('V-DC.txt')
else:
    # Use approximate equation to convert tunes to voltages
    equal_tunes = True
    ntune = tune_points  # number of tune points. If 1, tune_x_start is selected.
    tune_x_start = initial_tune
    tune_x_end = final_tune
    tune_x = np.linspace(tune_x_start, tune_x_end, ntune)
    if equal_tunes:
        tune_y = tune_x
    else:
        print "unequal tunes in x and y not yet supported"
    V0 = 29.413
    # approximate equation from Hiromi's NIM 2002 paper, eqn 13.
    # tunet = (2**0.5)*qm_argon*V0/(((r0*freq)**2)*(math.pi**3))

    tune_coef = (((r0 * freq) ** 2) * (math.pi ** 3)) / ((2 ** 0.5) * qm_argon)
    voltage_array = 1.29 * tune_coef * tune_x  # factor of 1.29 missing?
    accumulation_voltage = 1.29 * tune_coef * accumulation_tune
    # print tune_coef, tune_coef*0.1, tunet


if rods_powered == 2:
    voltage_array = voltage_array * 2
    accumulation_voltage = accumulation_voltage * 2



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


Rods = Waveforms('Rods', seg_len, rod_offset, accumulation_voltage, voltage_array, ramp_time * freq, A1_gain, AWG_gain, max_bits)
FC_endcap = Waveforms('FC', seg_len, endcap_offset, accumulation_voltage, voltage_array, ramp_time* freq, A4_gain, AWG_gain, max_bits)
MCP_endcap = Waveforms('MCP', seg_len, endcap_offset, accumulation_voltage, voltage_array, ramp_time*freq, A3_gain, AWG_gain, max_bits)

Rods.create_all_waveforms(rods_powered)
FC_endcap.create_all_waveforms(rods_powered)
MCP_endcap.create_all_waveforms(rods_powered)


