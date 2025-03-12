
import numpy as np
from collections import defaultdict
from csv import DictReader

# csv file parser (column names are in first row, rows starting with # are ignored)
def parse_csv(filename, fieldnames=None, delimiter=','):
    result = defaultdict(list)
    with open(filename) as infile:
        reader = DictReader(
            infile, fieldnames=fieldnames, delimiter=delimiter
        )
        for row in reader:
            if (not list(row.values())[0].startswith('#')):
                for fieldname, value in row.items():
                    result[fieldname].append(value)
    return result


def gaussian1D(x, ybase, ampl, xcenter ,sigma):
    #return ybase+ampl*(1/(sigma*(np.sqrt(2*np.pi)))) * (np.exp((-1.0/2.0)*(((x-xcenter)/sigma)**2)))
    return ybase + ampl * (np.exp((-1.0/2.0)*(((x-xcenter)/sigma)**2)))


def regheader():
    hdr="# Region file format: DS9 version 4.1\n"
    hdr=hdr + "global color=green dashlist=8 3 width=1 font=\"helvetica 10 normal roman\" select=1 highlite=1 dash=0 fixed=0 edit=1 move=1 delete=1 include=1 source=1\n"
    hdr=hdr + "physical\n"
    return hdr
