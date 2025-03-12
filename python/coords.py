
# coordinate transformations

import math


def cart2pol(x, y):
    # note: phi is radians
    rho = math.sqrt(x**2 + y**2)
    phi = math.atan2(y, x)
    return(rho, phi)

def pol2cart(rho, phi):
    # note: phi is radians
    x = rho * math.cos(phi)
    y = rho * math.sin(phi)
    return(x, y)

def cart2fits(x, y):
    return(x+0.5, y+0.5)

def fits2cart(x, y):
    return(x-0.5, y-0.5)

def cart2impix(x, y, h):
    return(x-0.5, -y+h-0.5)

def impix2cart(x, y, h):
    return(x+0.5, -y+h-0.5)

def fits2impix(x, y, h):
    return(x-1, -y+h)

def impix2fits(x, y, h):
    return(x+1, -y+h)
