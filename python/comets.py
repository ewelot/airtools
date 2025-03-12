
import math
import re


def cometname (scname):
    # check for numbered periodic comet
    if re.compile('^[0-9]+P$').match(scname):
        return scname
    # convert comet name [ACP]YYYYXX to [ACP]/YYYY XX
    if re.compile('^[ACP][0-9][0-9][0-9][0-9][A-Z]').match(scname):
        return scname[0]+"/"+scname[1:5]+" "+scname[5:]
    # convert comet name YYYYAN to C/YYYY AN
    if re.compile('^[0-9][0-9][0-9][0-9][A-Z]').match(scname):
        return "C/"+scname[0:4]+" "+scname[4:]
    # check for numbered asteroid or asteroid name
    if re.compile('^([0-9]+)$').match(scname) or \
        re.compile('^[0-9]+$').match(scname) or \
        re.compile('^[^0-9]+$').match(scname):
        return ""
    return ""


# convert mag to heliocentric mag
def hmag(mag, d_earth_au):
    if (type(mag) is str):
        mag=float(mag.rstrip(':'))
    val=mag-5*math.log10(d_earth_au)
    return val


# convert coma size from arcmin to linear diameter in km
def lcoma(coma, d_earth_au):
    coma=float(coma)
    if coma < 0: return coma
    au=149597870700 # au in meters 
    val=d_earth_au*au*math.tan(math.pi*coma/60/180)/1000
    return val
