# Code creates txt files containing the desired waveforms for a variety of tunes and saves them to a file
# Code should also include the sweep in tune from the starting tune
# Code should define the starting tune, this waveform then remains the same
# Perhaps naming the sweep files and the second tune files with the same number will make it easier.

from __future__ import division
from functions import *
import numpy as np
import matplotlib.pyplot as plt
import math
import sys
import csv

# Enter desired parameters:
# At the moment need to specify accumulation voltage
accumulation_amplitude = 62

# Segment length for the waveforms
seg_len = 100

# Time taken for tune ramp
ramp_time =5e-5
# time increment plotted in waveforms
time_increment = 1e-8
# time increment plotted in ramping waveforms
ramp_time_increment = 1e-8

# voltage offset on rods
rod_offset = 9
# voltage offset on endcaps
endcap_offset = 25


# Need to include amplifier calibration
# calibrate w.r.t channel 1?

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
AWG_gain = 5/2



# Mass of argon
argon_mass = 39.948
# rf frequency
freq = 1e6
# time of 1 rf period
time_length = 1/freq
# trap radius
r0 = 5e-3
# correction to trap radius from calibration
calibration = 1
# charge
charge = 1.60217733e-19
# speed of light
speed_of_light = 2.99792458e8
unified_atomic_mass_unit = 1.6605e-27
qm_argon = charge/(argon_mass*unified_atomic_mass_unit)

# Max no. of bits, note that this is amplitude
max_bits = 2**15
# 1E8 samples per second is the limit of the system

####################################################

#option to use Mathematica or approximate equation to convert tune to voltage

use_mathematica = False
if use_mathematica:
    # Use the mathematica to convert the tune to a voltage
    tune_x, tune_y, rf_voltage, offset_voltage = readfiledata('V-DC.txt')
else:
    #Use approximate equation to convert tunes to voltages
    equal_tunes = True
    ntune = 1 #number of tune points. If 1, tune_x_start is selected.
    tune_x_start = 0.15
    tune_x_end = 0.15
    tune_x = np.linspace(tune_x_start, tune_x_end, ntune)
    if equal_tunes:
        tune_y = tune_x
    else:
        print "unequal tunes in x and y not yet supported"
    V0 = 29.413
    #approximate equation from Hiromi's NIM 2002 paper, eqn 13.
    #tunet = (2**0.5)*qm_argon*V0/(((r0*freq)**2)*(math.pi**3))

    tune_coef = (((r0*freq)**2)*(math.pi**3))/((2**0.5)*qm_argon)
    rf_voltage = 1.29*tune_coef*tune_x #factor of 1.29 missing?
    #print tune_coef, tune_coef*0.1, tunet


#print tune_x
#print tune_y
#print rf_voltage
#print offset_voltage
final_amplitude = []
for i in range(len(rf_voltage)):
    final_amplitude.append(rf_voltage[i] * 2)

print "tunes ", tune_x
print len(final_amplitude)


outfile = open('Summary.txt', 'w')
outfile.write("Accumulation voltage: \t")
outfile.write("%f\n" % accumulation_amplitude)
outfile.write("Final voltage and tune\n")
for i in range(len(final_amplitude)):
    outfile.write("%f," % final_amplitude[i])
    outfile.write("%f\n" % tune_x[i])
outfile.close()

# Need to write a seperate file for each amplifier due to the differences between them
# Also need seperate file for rods as offset is different from endcaps


#################################################################
###   Main Rods 13
#################################################################


# Save the waveform to a file
# "accumulation_tune.txt" specifies the waveform that tunes are accumulated at

outfile = open('Rods_13_seg_1.csv', 'w')


accumulation_time = []
accumulation_voltage = []
accumulation_number = []

for i in range(int(time_length/time_increment)):
    accumulation_number.append(i)

for i in range(seg_len):
    accumulation_voltage.append(accumulation_amplitude * np.sin(i * 2 * np.pi/seg_len) + rod_offset )

#convert amplifier voltage to AWG bits
accumulation_voltage = np.array(accumulation_voltage)
accumulation_v_bits = (np.array(accumulation_voltage)/A1_gain)*(max_bits/AWG_gain)


print accumulation_voltage
print "maxbits ",max_bits
print "accumulation_v_bits ",max(accumulation_v_bits) - min(accumulation_v_bits)
#plt.plot(accumulation_v_bits)
#plt.show()
writer = csv.writer(outfile,lineterminator = '\n')
for i, v in zip(range(seg_len), accumulation_v_bits):
    writer.writerow((i,v))
outfile.close()


# Include loop for many final tunes
# At the moment loop is over voltage as tune conversion doesnt work
for j in range(len(final_amplitude)):


    # Create equation describing each segment


    # Save the wavforms to file
    # "voltageWaveform001.txt" ect specifies the final tune
    # "voltageramp001.txt" ect specifies the waveform ramp


    outfile = open('voltageWaveformRods13_' + str(j) + '.csv', 'w')
    # outfile.write("Time,")
    # outfile.write("Voltage amplitude\n")

    experiment_time = []
    experiment_voltage = []
    experiment_number = []

    for i in range(int(time_length / time_increment)):
        experiment_number.append(i)

    for i in frange(0, time_length, time_increment):
        experiment_time.append(i)
        # Need to relate to bit number here
        experiment_voltage.append((max_bits/(AWG_gain * A1_gain))*((final_amplitude[j] * np.sin(i * freq * 2 * np.pi)) + rod_offset))

    for i in range(len(experiment_time)):
        outfile.write("%i," % experiment_number[i])
        outfile.write("%i\n" % math.floor(experiment_voltage[i]))
    outfile.close()

    outfile = open('voltageWaveformRampRods13_' + str(j) + '.csv', 'w')
    # outfile.write("Time,")
    # outfile.write("Voltage amplitude\n")

    ramping_time = []
    ramping_voltage = []
    ramping_number = []


    for i in range(int(ramp_time / ramp_time_increment)):
        ramping_number.append(i)

    for l in range(int(ramp_time * freq)):
        for i in frange(0, ramp_time/(ramp_time * freq), ramp_time_increment):
            ramping_time.append(i + (l / freq))
            # Need to relate to bit number here
            ramping_voltage.append((max_bits/(AWG_gain * A1_gain))*((((((final_amplitude[j]-accumulation_amplitude)*l)/(ramp_time * freq)) + accumulation_amplitude) * np.sin(i * freq * 2 * np.pi)) + rod_offset))


    for i in range(len(ramping_time)):
        outfile.write("%i," % ramping_number[i])
        outfile.write("%i\n" % math.floor(ramping_voltage[i]))
    outfile.close()


    #if j==0:
    #    plt.figure('accumulation rods 13')
    #    plt.plot(accumulation_number, accumulation_voltage)
    #
    #    plt.figure('ramp rods 13')
    #    plt.plot(ramping_number, ramping_voltage)
    
    #    plt.figure('experiment rods 13')
    #    plt.plot(experiment_number, experiment_voltage)
    #    plt.show()



#################################################################
###  FC endcap 13
#################################################################
#print 'print'
#print (accumulation_amplitude + endcap_offset)/(AWG_gain * A2_gain)

# Save the waveform to a file
# "accumulation_tune.txt" specifies the waveform that tunes are accumulated at

outfile = open('accumulationVoltageFCendcap13.csv', 'w')
# outfile.write("Time,")
# outfile.write("Voltage amplitude\n")

accumulation_time = []
accumulation_voltage = []
accumulation_number = []

for i in range(int(time_length/time_increment)):
    accumulation_number.append(i)

for i in frange(0, time_length, time_increment):
    accumulation_time.append(i)
    # Need to relate to bit number here
    accumulation_voltage.append((max_bits/(AWG_gain * A4_gain))*((accumulation_amplitude * np.sin(i * freq * 2 * np.pi)) + endcap_offset))

for i in range(len(accumulation_time)):
    outfile.write("%i," % accumulation_number[i])
    outfile.write("%.i\n" % math.floor(accumulation_voltage[i]))
outfile.close()


# Include loop for many final tunes
# At the moment loop is over voltage as tune conversion doesnt work
for j in range(len(final_amplitude)):


    # Create equation describing each segment


    # Save the wavforms to file
    # "voltageWaveform001.txt" ect specifies the final tune
    # "voltageramp001.txt" ect specifies the waveform ramp


    outfile = open('voltageWaveformFCendcap13_' + str(j) + '.csv', 'w')
    # outfile.write("Time,")
    # outfile.write("Voltage amplitude\n")

    experiment_time = []
    experiment_voltage = []
    experiment_number = []

    for i in range(int(time_length / time_increment)):
        experiment_number.append(i)

    for i in frange(0, time_length, time_increment):
        experiment_time.append(i)
        # Need to relate to bit number here
        experiment_voltage.append((max_bits/(AWG_gain * A4_gain))*((final_amplitude[j] * np.sin(i * freq * 2 * np.pi)) + endcap_offset))

    for i in range(len(experiment_time)):
        outfile.write("%i," % experiment_number[i])
        outfile.write("%i\n" % math.floor(experiment_voltage[i]))
    outfile.close()

    outfile = open('voltageWaveformFCendcap13drop_' + str(j) + '.csv', 'w')
    # outfile.write("Time,")
    # outfile.write("Voltage amplitude\n")

    experiment_time = []
    experiment_voltage = []
    experiment_number = []

    for i in range(int(time_length / time_increment)):
        experiment_number.append(i)

    for i in frange(0, time_length, time_increment):
        experiment_time.append(i)
        # Need to relate to bit number here
        experiment_voltage.append((max_bits/(AWG_gain * A4_gain))*((final_amplitude[j] * np.sin(i * freq * 2 * np.pi))))

    for i in range(len(experiment_time)):
        outfile.write("%i," % experiment_number[i])
        outfile.write("%i\n" % math.floor(experiment_voltage[i]))
    outfile.close()



    outfile = open('voltageWaveformFCendcapRamp13_' + str(j) + '.csv', 'w')
    # outfile.write("Time,")
    # outfile.write("Voltage amplitude\n")

    ramping_time = []
    ramping_voltage = []
    ramping_number = []


    for i in range(int(ramp_time / ramp_time_increment)):
        ramping_number.append(i)

    for l in range(int(ramp_time * freq)):
        for i in frange(0, ramp_time/(ramp_time * freq), ramp_time_increment):
            ramping_time.append(i + (l / freq))
            # Need to relate to bit number here
            ramping_voltage.append((max_bits/(AWG_gain * A4_gain))*((((((final_amplitude[j]-accumulation_amplitude)*l)/(ramp_time * freq)) + accumulation_amplitude) * np.sin(i * freq * 2 * np.pi)) + endcap_offset))


    for i in range(len(ramping_time)):
        outfile.write("%i," % ramping_number[i])
        outfile.write("%i\n" % math.floor(ramping_voltage[i]))
    outfile.close()


    #if j==0:
    #    plt.figure('accumulation FC endcap 13')
    #    plt.plot(accumulation_number, accumulation_voltage)
    
    #    plt.figure('ramp FC endcap 13')
    #    plt.plot(ramping_number, ramping_voltage)
    
    #    plt.figure('experiment FC endcap 13')
    #    plt.plot(experiment_number, experiment_voltage)
    #    plt.show()




#################################################################
###  MCP endcap 13
#################################################################
#print 'print'
#print (accumulation_amplitude + endcap_offset)/(AWG_gain * A2_gain)

# Save the waveform to a file
# "accumulation_tune.txt" specifies the waveform that tunes are accumulated at

outfile = open('accumulationVoltageMCOendcap13.csv', 'w')
# outfile.write("Time,")
# outfile.write("Voltage amplitude\n")

accumulation_time = []
accumulation_voltage = []
accumulation_number = []

for i in range(int(time_length/time_increment)):
    accumulation_number.append(i)

for i in frange(0, time_length, time_increment):
    accumulation_time.append(i)
    # Need to relate to bit number here
    accumulation_voltage.append((max_bits/(AWG_gain * A3_gain))*((accumulation_amplitude * np.sin(i * freq * 2 * np.pi)) + endcap_offset))

for i in range(len(accumulation_time)):
    outfile.write("%i," % accumulation_number[i])
    outfile.write("%.i\n" % math.floor(accumulation_voltage[i]))
outfile.close()


# Include loop for many final tunes
# At the moment loop is over voltage as tune conversion doesnt work
for j in range(len(final_amplitude)):


    # Create equation describing each segment


    # Save the wavforms to file
    # "voltageWaveform001.txt" ect specifies the final tune
    # "voltageramp001.txt" ect specifies the waveform ramp


    outfile = open('voltageWaveformMCPendcap13_' + str(j) + '.csv', 'w')
    # outfile.write("Time,")
    # outfile.write("Voltage amplitude\n")

    experiment_time = []
    experiment_voltage = []
    experiment_number = []

    for i in range(int(time_length / time_increment)):
        experiment_number.append(i)

    for i in frange(0, time_length, time_increment):
        experiment_time.append(i)
        # Need to relate to bit number here
        experiment_voltage.append((max_bits/(AWG_gain * A3_gain))*((final_amplitude[j] * np.sin(i * freq * 2 * np.pi)) + endcap_offset))

    for i in range(len(experiment_time)):
        outfile.write("%i," % experiment_number[i])
        outfile.write("%i\n" % math.floor(experiment_voltage[i]))
    outfile.close()

    outfile = open('voltageWaveformMCPendcapRamp13_' + str(j) + '.csv', 'w')
    # outfile.write("Time,")
    # outfile.write("Voltage amplitude\n")

    ramping_time = []
    ramping_voltage = []
    ramping_number = []


    for i in range(int(ramp_time / ramp_time_increment)):
        ramping_number.append(i)

    for l in range(int(ramp_time * freq)):
        for i in frange(0, ramp_time/(ramp_time * freq), ramp_time_increment):
            ramping_time.append(i + (l / freq))
            # Need to relate to bit number here
            ramping_voltage.append((max_bits/(AWG_gain * A3_gain))*((((((final_amplitude[j]-accumulation_amplitude)*l)/(ramp_time * freq)) + accumulation_amplitude) * np.sin(i * freq * 2 * np.pi)) + endcap_offset))


    for i in range(len(ramping_time)):
        outfile.write("%i," % ramping_number[i])
        outfile.write("%i\n" % math.floor(ramping_voltage[i]))
    outfile.close()

    
    #if j==0:
    #    plt.figure('accumulation FC endcap 13')
    #    plt.plot(accumulation_number, accumulation_voltage)

    #    plt.figure('ramp FC endcap 13')
    #    plt.plot(ramping_number, ramping_voltage)
    
    #    plt.figure('experiment FC endcap 13')
    #    plt.plot(experiment_number, experiment_voltage)
    #    plt.show()

