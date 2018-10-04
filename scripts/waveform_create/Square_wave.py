import scipy
import ibex_optics
import numpy as np
import pylab as pl

#useful
mass = 6.64e-26
idek = 1/(2*(2**(1/2))*np.pi)
radius = 5e-3
rf = 1e6
amp = 50

def square_wave(offset = 0, amplitude = 0): 
    voltage = []
    v = 100
    bits = []
    p2pamp = amplitude
    time = np.linspace(0, 1e-6, 100)

    a = 2e-7
    b = 4e-7
    c = 6e-7
    d = 8e-7
    e = 1e-6
    f = 0
    g = 0
    h = 0
    i = 0
    j = 0

    for i in range(len(time)):
        if time[i]<a:
            v = p2pamp+offset
            voltage.append(v)
            bits.append((v/50)*13107.2)
        elif a<time[i] and time[i]<=b:
            v = offset
            voltage.append(v)
            bits.append((v/50)*13107.2)
        elif b<time[i] and time[i]<=c:
            v = -p2pamp+offset
            voltage.append(v)
            bits.append((v/50)*13107.2)
        elif c<time[i] and time[i]<=d:
            v = offset
            voltage.append(v)
            bits.append((v/50)*13107.2)
        elif d<time[i] and time[i]<=e:
            v = p2pamp+offset
            voltage.append(v)
            bits.append((v/50)*13107.2)
        elif e<time[i] and time[i]<=f:
            v = offset
            voltage.append(v)
            bits.append((v/50)*13107.2)
        elif f<time[i] and time[i]<=g:
            v = -p2pamp+offset
            voltage.append(v)
            bits.append((v/50)*13107.2)
        elif g<time[i] and time[i]<=h:
            v = offset
            voltage.append(v)
            bits.append((v/50)*13107.2)
        elif h<time[i] and time[i]<=i:
            v = p2pamp+offset
            voltage.append(v)
            bits.append((v/50)*13107.2)
        elif i<time[i] and time[i]<=j:
            v = offset
            voltage.append(v)
            bits.append((v/50)*13107.2)

    return time, voltage

