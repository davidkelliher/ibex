
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
