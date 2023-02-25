#!/usr/bin/python3

# Version 1.0
# Changelog ...

import sys
import os
import math
import re
from tempfile import NamedTemporaryFile
from collections import defaultdict
from csv import DictReader
import ephem
import pyvips
import numpy as np

# csv file parser (column names are in first row)
def parse_csv(filename, fieldnames=None, delimiter=','):
    result = defaultdict(list)
    with open(filename) as infile:
        reader = DictReader(
            infile, fieldnames=fieldnames, delimiter=delimiter
        )
        for row in reader:
            for fieldname, value in row.items():
                result[fieldname].append(value)
    return result

#---------------------------------------------
#   functions for calculation of ephemerides
#---------------------------------------------

# convert UT date string yyyymmdd to JD
def ymd2jd (ymd):
    s=str(ymd)
    datestr=s[0:4] + '/' + s[4:6] + '/' + s[6:]
    return ephem.julian_date(datestr)

# convert JD to UT date string yyyymmdd.dd
def jd2ymd (jd):
    d=ephem.Date(jd - ephem.julian_date(0))
    x=d.triple()
    s='{:04d}{:02d}{:05.2f}'.format(x[0],x[1],x[2])
    return s

# convert mag to heliocentric mag
def hmag(mag, d_earth):
    if (type(mag) is str):
        mag=float(mag.rstrip(':'))
    val=mag-5*math.log10(d_earth)
    return val

# convert coma size from arcmin to linear diameter in km
def lcoma(coma, d_earth):
    coma=float(coma)
    if coma < 0: return coma
    val=d_earth*ephem.meters_per_au*math.tan(math.pi*coma/60/180)/1000
    return val


def addephem (param):
    # param
    #   csvfile   reqired fields: utime, date, source, obsid, mag, coma, method, filter, soft
    #               where utime is unix time in seconds and date is yyyymmdd.dd
    #   cephem    comet ephemeris record from xephem edb file
    #
    # output: text file with following fields:
    #   position 1     2    3      4     5   6    7    8     9      10     11   12         13    14
    #   fields:  utime date source obsid mag hmag coma lcoma method filter soft log(r_sun) r_sun d_earth
    if (len(param) != 2):
        print("usage: addephem csvfile cephem")
        exit(-1)
    else:
        csvfile=param[0]
        cephem=param[1]

    # TODO: parse comet ephem database (xephem edb format)
    k2=ephem.readdb(cephem)

    data=parse_csv(csvfile)
    n=len(data['date'])
    for i in range(n):
        if (data['utime'][i][0]=='#'):
            continue
        str=data['date'][i]
        datestr=str[0:4] + '/' + str[4:6] + '/' + str[6:]
        k2.compute(datestr)
        #ephem.julian_date(datestr),
        print('{} {} {} {}'.format(
            data['utime'][i],
            data['date'][i],
            data['source'][i],
            data['obsid'][i]
            ),
            end='')
        print(' {} {:.2f} {} {:.0f}'.format(
            data['mag'][i],
            hmag(data['mag'][i], k2.earth_distance),
            data['coma'][i],
            lcoma(data['coma'][i], k2.earth_distance)
            ),
            end='')
        print(' {} {} {} {:.4f} {:.4f} {:.4f}'.format(
            data['method'][i],
            data['filter'][i],
            data['soft'][i],
            math.log10(k2.sun_distance),
            k2.sun_distance,
            k2.earth_distance
            ))
    exit()


def mkephem (param):
    # param
    #   cephem    comet ephemeris record from xephem edb file
    #   start     start date (yyyymmdd or jd)
    #   end       end date (yyyymmdd or jd)
    #   g         model parameter
    #   k         model parameter
    # output: text file with following fields:
    #   position 1     2    3   4    5          6     7
    #   fields:  utime date mag hmag log(r_sun) r_sun d_earth
    # reading command line parameters
    dateunit="yyyymmdd"
    if (param[0] == "-s"):
        dateunit="unixseconds"
        del param[0]
    if (len(param) < 3):
        print("usage: mkephem [-s] cephem start end [g] [k] [num]")
        exit(-1)
    else:
        cephem=param[0]
        start=float(param[1])
        end=float(param[2])
    if (len(param) > 3):
        if param[3]: g=float(param[3])
        if param[4]: k=float(param[4])
    if (len(param) > 5):
        num=int(param[5])

    # convert start and end from yyyymmdd or unix time to JD
    if (dateunit == "yyyymmdd"):
        start=ymd2jd(start)
        end=ymd2jd(end)
    else:
        # convert start and end from unix time to JD
        start=2440587.5+start/86400.0
        end=2440587.5+end/86400.0
    
    # TODO: parse comet ephem database
    k2=ephem.readdb(cephem)
    if 'g' in locals(): k2._g=g
    if 'k' in locals(): k2._k=k
    print('# model: m = {:.2f} + 5log(D) + {:.2f}*2.5log(r)'.format(k2._g,k2._k))


    # print header line
    print('# utime        date        mag   hmag  log(r) r      d')

    if not 'num' in locals(): num=100   # number of intervals
    for i in range(num+1):
        jd=start+i*(end-start)/(num)
        unixtime=(jd-2440587.5)*86400.0
        utdate=jd2ymd(jd)
        k2.compute(ephem.Date(jd - ephem.julian_date(0)))
        print('{:.0f} {}'.format(
            unixtime,
            utdate
            ),
            end='')
        print(' {:.3f} {:.3f}'.format(
            k2.mag,
            hmag(k2.mag, k2.earth_distance)
            ),
            end='')
        print(' {:.4f} {:.4f} {:.4f}'.format(
            math.log10(k2.sun_distance),
            k2.sun_distance,
            k2.earth_distance
            ))
    exit()


#---------------------------------------
#   functions for image processing
#---------------------------------------

# convert 3 monochrome FITS images to PPM (16bit)
# syntax: fits3toppm red green blue outppm
def fits3toppm(param):
    red = param[0]
    green = param[1]
    blue = param[2]
    outppm = param[3]
    r = pyvips.Image.new_from_file(red)
    g = pyvips.Image.new_from_file(green)
    b = pyvips.Image.new_from_file(blue)
    rgb = r.bandjoin([g, b]).copy(interpretation="rgb16")
    rgb.ppmsave(outppm, strip=1)
    exit()

# convert FITS cube to PPM (stdout), optionally apply scaling
# syntax: fitscubetoppm [-m mult] [-a add] infits outppm
def fitscubetoppm(param):
    mult=1
    add=0
    if(param[0]=='-m'):
        mult=float(param[1])
        del param[0:2]
    if(param[0]=='-a'):
        add=float(param[1])
        del param[0:2]
    infits = param[0]
    outpnm = param[1]

    # reading input image
    if (infits and infits != '-'):
        inimg = pyvips.Image.new_from_file(infits)
    else:
        source = pyvips.Source.new_from_descriptor(sys.stdin.fileno())
        inimg = pyvips.Image.new_from_source(source, "")

    inimg.linear(mult,add).copy(interpretation="rgb16").ppmsave(outpnm, strip=1)
    exit()

# crop an image
# imcrop [-f] inimg outimg w h xoff yoff
def imcrop(param):
    outfmt='pnm'
    if(param[0]=='-f'):
        outfmt='fits'
        del param[0]
    infile = param[0]
    outfile = param[1]
    width = param[2]
    height = param[3]
    xoff = param[4]
    yoff = param[5]

    # reading input image
    if (infile and infile != '-'):
        inimg = pyvips.Image.new_from_file(infile)
    else:
        source = pyvips.Source.new_from_descriptor(sys.stdin.fileno())
        inimg = pyvips.Image.new_from_source(source, "")

    outimg=inimg.crop(xoff, yoff, width, height)

    # writing output image
    writeimage(["-f", outfmt, outimg, outfile])
    exit()


# image statistics (per channel output: min max mean (stddev))
# imstat [-m] "$fname"
# note: integer statistics assuming input is 8bit or 16bit integer data
def imstat(param):
    medianbox=""
    if(param[0]=='-m'):
        medianbox=3
        del param[0]
    infile = param[0]

    # reading input image
    if (infile and infile != '-'):
        inimg = pyvips.Image.new_from_file(infile)
    else:
        source = pyvips.Source.new_from_descriptor(sys.stdin.fileno())
        inimg = pyvips.Image.new_from_source(source, "")

    if(medianbox):
        statsimg=inimg.median(medianbox).stats()
    else:
        statsimg=inimg.stats()

    # writing output values
    for i in range(1, statsimg.height):
        if (i>1): print(' ', end='')
        print('{:.0f} {:.0f} {:.1f} ({:.1f})'.format(
            statsimg.getpoint(0, i)[0],
            statsimg.getpoint(1, i)[0],
            statsimg.getpoint(4, i)[0],
            statsimg.getpoint(5, i)[0]
            ),
            end='')
    exit()

# get min/max of image data
# datarange "$fname"
def datarange(param):
    infile = param[0]

    # reading input image
    if (infile and infile != '-'):
        inimg = pyvips.Image.new_from_file(infile)
    else:
        source = pyvips.Source.new_from_descriptor(sys.stdin.fileno())
        inimg = pyvips.Image.new_from_source(source, "")

    statsimg=inimg.stats()

    # writing output values
    print('{:f} {:f}'.format(
        statsimg.getpoint(0, 0)[0],
        statsimg.getpoint(1, 0)[0]),
        end='')
    exit()

# basic CCD image reduction: outpnm = mult * (inpnm-dark)/flat + add
#   note about sequence of operations
#   - add preadd
#   - multiply premult
#   - flip image (top-bottom)
#   - rotate image (180 degrees)
#   - subtract dark image
#   - divide by flat image
#   - clean hot pixel
#   - crop image
#   - post rotate (180 degrees)
#   - multiply by mult (array for different bands)
#   - add offset value add (array for different bands)
#   - optionally convert from rgb to gray
# syntax: pnmccdred [-fmt outfmt|pnm] [-gray] [-preadd val] [-premult val] [-flip] [-prerot]
#   [-bpat bayerpattern] [-cgeom wxh+x+y ] [-rot] inpnm outpnm dark flat bad mult add
def pnmccdred(param):
    outfmt='pnm'
    outgray=False
    preadd=0
    premult=1
    bayerpattern="" # only used if bad is provided
    cgeom=""
    flip=False
    prerot=False
    rot=False
    if(param[0]=='-fmt'):
        outfmt=param[1]
        del param[0:2]
    if(param[0]=='-gray'):
        outgray=True
        del param[0]
    if(param[0]=='-preadd'):
        preadd=float(param[1])
        del param[0:2]
    if(param[0]=='-premult'):
        premult=float(param[1])
        del param[0:2]
    if(param[0]=='-flip'):
        flip=True
        del param[0]
    if(param[0]=='-prerot'):
        prerot=True
        del param[0]
    if(param[0]=='-bpat'):
        bayerpattern=param[1]
        del param[0:2]
    if(param[0]=='-cgeom'):
        cgeom=param[1]
        del param[0:2]
    if(param[0]=='-rot'):
        rot=True
        del param[0]
    infilename = param[0]
    outfilename = param[1]
    np = len(param)
    if (np > 2): dark = param[2]
    if (np > 3): flat = param[3]
    if (np > 4): bad  = param[4]
    if (np > 5): mult = param[5]
    if (np > 6): add = param[6]
    if (mult): mult = tuple(float(val) for val in tuple(mult.split(",")))
    if (add):  add  = tuple(float(val) for val in tuple(add.split(",")))

    # reading input image
    if (infilename and infilename != '-'):
        inimg = pyvips.Image.new_from_file(infilename)
    else:
        source = pyvips.Source.new_from_descriptor(sys.stdin.fileno())
        inimg = pyvips.Image.new_from_source(source, "")

    # create command
    code = """inimg"""
    if (preadd != 0):
        code += """.linear(1, preadd)"""
    if (premult != 1):
        code += """.linear(premult, 0)"""
    if flip:
        code += """.flip('vertical')"""
    if prerot:
        code += """.rot180()"""
    if dark:
        if (dark != '-'):
            darkimg = pyvips.Image.new_from_file(dark)
        else:
            source = pyvips.Source.new_from_descriptor(sys.stdin.fileno())
            darkimg = pyvips.Image.new_from_source(source, "")
        code += """.subtract(darkimg)"""
    if flat:
        if (flat != '-'):
            flatimg = pyvips.Image.new_from_file(flat)
        else:
            source = pyvips.Source.new_from_descriptor(sys.stdin.fileno())
            flatimg = pyvips.Image.new_from_source(source, "")
        code += """.divide(flatimg)"""
    if cgeom:
        x=re.split('x|\\+', cgeom)
        code += """.crop(x[2], x[3], x[0], x[1])"""
    if rot:
        code += """.rot180()"""
    if mult:
        if add:
            code += """.linear(mult, add)"""
        else:
            code += """.linear(mult, 0)"""
    else:
        if add: code += """.linear(1, add)"""
    if outgray and inimg.bands == 3:
        channelmult=(0.26,0.40,0.34)
        code += """.linear(channelmult, 0).bandmean().copy(interpretation='grey16')"""

    code += """.rint().cast('ushort')"""

    if bad:
        tmpimg = eval(code)
        # TODO: parameters cgeom and rot must be applied to bad as well 
        if (bayerpattern):
            cleanhotpixel(["-b", bayerpattern, tmpimg, bad, outfilename])
        else:
            cleanhotpixel([tmpimg, bad, outfilename])
    else:
        outimg = eval(code)
        writeimage(["-f", outfmt, outimg, outfilename])

    exit()

#ppmtogray $ppm $tmp1 $1,$2,$3
# convert from PPM to PGM using user supplied channel multipliers
# syntax: ppmtogray -f inppm outpgm [multR,multG,multB]
def ppmtogray(param):
    outfmt='pnm'
    if(param[0]=='-f'):
        outfmt='fits'
        del param[0]
    infilename = param[0]
    outfilename = param[1]
    if(len(param)>2):
        mult = param[2]
        mult = tuple(float(val) for val in tuple(mult.split(",")))
    else: mult=(0.26,0.40,0.34)

    # reading input image
    if (infilename and infilename != '-'):
        inimg = pyvips.Image.new_from_file(infilename)
    else:
        source = pyvips.Source.new_from_descriptor(sys.stdin.fileno())
        inimg = pyvips.Image.new_from_source(source, "")

    # scale mult to preserve average intensity
    multnorm=tuple(val*3/sum(mult) for val in mult)
    outimg = inimg.linear(multnorm, 0).bandmean().rint().copy(interpretation="grey16")

    # writing output image
    writeimage(["-f", outfmt, outimg, outfilename])
    exit()


# convert from (noisy) RGB image to color image by using LRGB techniques
# syntax: lrgb [-f|-t] [-16] inppm outppm bgR,bgG,bgB rmsg
def lrgb(param):
    outfmt='ppm'
    depth=8
    bg=""
    while (param[0][0:1] == "-"):
        if(param[0]=='-f'):
            outfmt='fits'
            del param[0]
        if(param[0]=='-t'):
            outfmt='tif'
            del param[0]
        if(param[0]=='-16'):
            depth=16
            del param[0]
    infilename = param[0]
    outfilename = param[1]
    if(len(param)>2):
        bg = param[2]
        bg = tuple(float(val) for val in tuple(bg.split(",")))
    if(len(param)>3):
        sd = float(param[3])

    # reading input image
    if (infilename and infilename != '-'):
        inimg = pyvips.Image.new_from_file(infilename)
    else:
        source = pyvips.Source.new_from_descriptor(sys.stdin.fileno())
        inimg = pyvips.Image.new_from_source(source, "")

    # color smoothing in Lab, and some boost
    l,a,b = inimg.colourspace("lab").bandsplit()
    l = l.gaussblur(0.6)
    if bg:
        x,a,b = inimg.subtract(bg).colourspace("lab").bandsplit()
    a = a.gaussblur(3).linear(1.2,0)
    b = b.gaussblur(3).linear(1.2,0)
    if (depth == 16):
        outimg = l.bandjoin([a,b]).colourspace("rgb16")
    else:
        outimg = l.bandjoin([a,b]).colourspace("srgb")
    
    # writing output image
    writeimage(["-f", outfmt, outimg, outfilename])
    exit()

def svgtopbm(param):
    # convert svg areas (circle/polygon/box) to pbm
    # regions are interpreted as good pixel regions (white, pgm value 255, pbm value 0)
    # TODO: currently output is a bi-level PGM image
    outfmt='pbm'
    invert=False
    if(param[0]=='-i'):
        invert=True
        del param[0]
    infilename = param[0]
    outfilename = param[1]

    # reading input image
    if (infilename and infilename != '-'):
        inimg = pyvips.Image.new_from_file(infilename)
    else:
        source = pyvips.Source.new_from_descriptor(sys.stdin.fileno())
        inimg = pyvips.Image.new_from_source(source, "")

    #vips extract_area $in $out $bwidth $bwidth $((w-2*bwidth)) $((h-2*bwidth))
    #vips gravity $in $out "centre" $w $h extend="white"
    w=inimg.width
    h=inimg.height
    if (invert):
        outimg = inimg.Colourspace("b-w").relational_const("lesseq", 255*0.5)
    else:
        outimg = inimg.Colourspace("b-w").relational_const("more", 255*0.5)

    # writing output image
    writeimage(["-f", outfmt, outimg, outfilename])

    exit()


# replace border by white (or black) pixels
# syntax: pnmreplaceborder [-f] [-b] <in> <out> [bwidth|2]
def pnmreplaceborder(param):
    outfmt='pnm'
    bwidth=2
    bcolor="white"
    if(param[0]=='-f'):
        outfmt='fits'
        del param[0]
    if(param[0]=='-b'):
        bcolor="black"
        del param[0]
    infilename = param[0]
    outfilename = param[1]
    np = len(param)
    if (np > 2): bwidth = int(param[2])

    # reading input image
    if (infilename and infilename != '-'):
        inimg = pyvips.Image.new_from_file(infilename)
    else:
        source = pyvips.Source.new_from_descriptor(sys.stdin.fileno())
        inimg = pyvips.Image.new_from_source(source, "")

    #vips extract_area $in $out $bwidth $bwidth $((w-2*bwidth)) $((h-2*bwidth))
    #vips gravity $in $out "centre" $w $h extend="white"
    w=inimg.width
    h=inimg.height
    outimg = inimg.crop(bwidth, bwidth, w-2*bwidth, h-2*bwidth).embed(bwidth, bwidth, w, h, extend=bcolor)

    # writing output image
    writeimage(["-f", outfmt, outimg, outfilename])

    exit()


# get statistics on image region defined by mask (svg image)
# syntax: regstat [-m] image mask badmask
def regstat(param):
    mode=''
    if(param[0]=='-m'):
        mode='minmax'
        del param[0]
    infilename = param[0]
    maskfilename = param[1]
    if(len(param)>2):
        badmaskfilename = param[2]
    else:
        badmaskfilename = ''

    # reading input image
    if (infilename and infilename != '-'):
        inimg = pyvips.Image.new_from_file(infilename)
    else:
        source = pyvips.Source.new_from_descriptor(sys.stdin.fileno())
        inimg = pyvips.Image.new_from_source(source, "")

    # convert alpha channel of masks to bilevel
    thres=114   # matching old regstat
    if (badmaskfilename):
        badmaskimg = pyvips.Image.svgload(badmaskfilename).extract_band(3)
        badmaskimg2 = (badmaskimg > thres).ifthenelse(0, 1)
        tmpimg = pyvips.Image.svgload(maskfilename).extract_band(3)
        tmpimg2 = (tmpimg > thres).ifthenelse(1, 0)
        maskimg = tmpimg2.multiply(badmaskimg2)
    else:
        tmpimg = pyvips.Image.svgload(maskfilename).extract_band(3)
        maskimg = (tmpimg > thres).ifthenelse(1, 0)

    # count inner and outer pixel
    histmask=maskimg.hist_find()
    outcnt=histmask.getpoint(0, 0)[0]
    incnt=histmask.getpoint(1, 0)[0]

    # image histogram
    ncol=inimg.bands
    histimg=inimg.multiply(maskimg).hist_find()
    # remove pixel counts outside mask
    histimg2=histimg.draw_rect([x-outcnt for x in histimg.getpoint(0, 0)], 0, 0, 1, 1)

    ramp = pyvips.Image.new_from_array(list(range(histimg2.width)))
    # mean value for each band: sum(hist*ramp)/area
    statsimg = histimg2.multiply(ramp).stats()
    mean = [statsimg.getpoint(2, i+1)[0]/incnt for i in range(ncol)]
    # determine min value for each band
    statsimg = (histimg2 > 0).ifthenelse(ramp, ramp.width).stats()
    minval = [statsimg.getpoint(0, i+1)[0] for i in range(ncol)]
    # determine max value for each band
    statsimg = (histimg2 > 0).ifthenelse(ramp, 0).stats()
    maxval = [statsimg.getpoint(1, i+1)[0] for i in range(ncol)]
    # TODO: stddev
    # TODO: clipped mean

    if (mode == 'minmax'):
        # min
        for i in range(ncol):
            if (i>0): print(",", end='')
            print("{:.1f}".format(minval[i]), end='')
        print(" ", end='')
        # max
        for i in range(ncol):
            if (i>0): print(",", end='')
            print("{:.1f}".format(maxval[i]), end='')
        print(" ", end='')
        # mean
        for i in range(ncol):
            if (i>0): print(",", end='')
            print("{:.1f}".format(mean[i]), end='')
        print(" ", end='')
        # area
        print('{:.0f}'.format(incnt))
    else:
        # clipped mean
        for i in range(ncol):
            if (i>0): print(",", end='')
            print("{:.1f}".format(mean[i]), end='')
        print(" ", end='')
        # sd
        for i in range(ncol):
            if (i>0): print(",", end='')
            print("x", end='')
        print(" ", end='')
        # area
        print('{:.0f} '.format(incnt), end='')
        # sum
        for i in range(ncol):
            if (i>0): print(",", end='')
            print("{:.1f}".format(mean[i]*incnt), end='')
        print(" ", end='')
        # mean
        for i in range(ncol):
            if (i>0): print(",", end='')
            print("{:.1f}".format(mean[i]), end='')
        print("")
    exit()

def pnmcombine(param):
    mode='mean' # sum, mean, median, stddev
    outfmt='pnm'
    if(param[0]=='-m'):
        mode=param[1]
        del param[0:2]
    # compatibility with using deprecated switches
    if(param[0]=='-d'):
        mode='median'
        del param[0]
    if(param[0]=='-s'):
        mode='stddev'
        del param[0]
    outfilename = param[len(param)-1]

    # reading input images
    inimgarray = [pyvips.Image.new_from_file(param[i], access='sequential') for i in range(len(param)-1)]
    
    if mode=="median":
        # determine median image
        outimg = inimgarray[0].bandrank(inimgarray[1:])
        #outimg = pyvips.Image.bandrank(inimgarray, len(inimgarray))
    elif mode=="mean":
        outimg = inimgarray[0]
        for i in range(1,len(inimgarray)):
            outimg = outimg.add(inimgarray[i]);
        outimg = outimg.linear(1/len(inimgarray), 0).rint()
    elif mode=="sum":
        outimg = inimgarray[0]
        for i in range(1,len(inimgarray)):
            outimg = outimg.add(inimgarray[i]);
        outimg = outimg.rint()
    else:
        meanimg = inimgarray[0]
        for i in range(1,len(inimgarray)):
            meanimg = meanimg.add(inimgarray[i]);
        meanimg = meanimg.linear(1/len(inimgarray), 0).rint()
        outimg = inimgarray[0].subtract(meanimg).multiply(inimgarray[0].subtract(meanimg))
        for i in range(1,len(inimgarray)):
            outimg = outimg.add(inimgarray[i].subtract(meanimg).multiply(inimgarray[i].subtract(meanimg)));
        #outimg = outimg.linear(1/len(inimgarray), 0).pow(inimgarray[0].linear(0, 0.5)).rint()
        outimg = outimg.linear(1/len(inimgarray), 0).math2_const("pow",0.5).rint()

    # writing output image
    writeimage(["-f", outfmt, outimg, outfilename])

    exit()


# clean bad pixels in image according to mask (bilinear interpolation)
# usage: cleanhotpixel [-b bayerpattern] <image> <badmask> [outimage]
# default: write result to stdout (pgm format)
# note: bayerpattern is filter pattern at lower left corner
def cleanhotpixel(param):
    bayerpattern=""
    outfilename="-"
    outfmt="pgm"
    method="median"     # if median use median otherwise mean
    neighbors="nearest" # if nearest then l/r/t/b otherwise tl/tr/bl/br
    if(isinstance(param[0],str) and param[0]=='-b'):
        bayerpattern=param[1]
        del param[0:2]

    # parameters
    if isinstance(param[0], pyvips.vimage.Image):
        image = param[0]
    else:
        image = pyvips.Image.new_from_file(param[0])
    badmask = pyvips.Image.new_from_file(param[1])
    if(len(param)>2):
        outfilename = param[2]

    w = image.width
    h = image.height

    # unused old code
    if ("mode" == "median"):
        # take 3x3 median of next but one pixels
        p00 = image.subsample(2, 2).median(3).zoom(2,2)
        p10 = image.embed(-1, 0, w, h).subsample(2, 2).median(3).zoom(2,2)
        p01 = image.embed(0, -1, w, h).subsample(2, 2).median(3).zoom(2,2)
        p11 = image.embed(-1, -1, w, h).subsample(2, 2).median(3).zoom(2,2)

        index = pyvips.Image.new_from_array([[0, 1], [2, 3]]).replicate(w/2, h/2)
        median = index.case([p00, p10, p01, p11])
        outimg = (badmask > 0).ifthenelse(median, image)

    if (bayerpattern == ""):
        # gray image
        if (neighbors == "nearest"):
            pl = image.embed(-1, 0, w, h)
            pr = image.embed(1, 0, w, h)
            pt = image.embed(0, -1, w, h)
            pb = image.embed(0, 1, w, h)
        else:
            pl = image.embed(-1, -1, w, h)
            pr = image.embed(1, -1, w, h)
            pt = image.embed(-1, 1, w, h)
            pb = image.embed(1, 1, w, h)
        if (method == "median"):
            pgray = pl.bandrank([pr, pt, pb])
        else:
            pgray = pl.bandjoin([pr, pt, pb]).bandmean()

        outimg = (badmask > 0).ifthenelse(pgray, image)
    else:
        # bayered image
        if (bayerpattern[1:2] == "G"):
            greenmask = pyvips.Image.new_from_array([[1, 0], [0, 1]]).replicate(w/2, h/2)
        else:
            greenmask = pyvips.Image.new_from_array([[0, 1], [1, 0]]).replicate(w/2, h/2)
        # interpolate green pixels
        ptl = image.embed(-1, -1, w, h)
        ptr = image.embed(1, -1, w, h)
        pbl = image.embed(-1, 1, w, h)
        pbr = image.embed(1, 1, w, h)
        if (method == "median"):
            pgreen = ptl.bandrank([ptr, pbl, pbr])
        else:
            pgreen = ptl.bandjoin([ptr, pbl, pbr]).bandmean()

        # interpolate red and blue pixels
        pl = image.embed(-2, 0, w, h)
        pr = image.embed(2, 0, w, h)
        pt = image.embed(0, -2, w, h)
        pb = image.embed(0, 2, w, h)
        if (method == "median"):
            predblue = pl.bandrank([pr, pt, pb])
        else:
            predblue = pl.bandjoin([pr, pt, pb]).bandmean()

        outimg = (badmask > 0).ifthenelse(
            (greenmask > 0).ifthenelse(pgreen, predblue),
            image)

    # writing output image
    writeimage(["-f", outfmt, outimg, outfilename])
    exit()


# merge 4 monochrome images into bayered image
# syntax: bmerge top-left top-right bottom-left bottom-right
def bmerge(param):
    outfilename="-"
    outfmt="pgm"
    infilename00 = param[0]
    infilename10 = param[1]
    infilename01 = param[2]
    infilename11 = param[3]
    if(len(param)>4):
        outfilename = param[4]

    p00 = pyvips.Image.new_from_file(infilename00).zoom(2,2)
    p10 = pyvips.Image.new_from_file(infilename10).zoom(2,2)
    p01 = pyvips.Image.new_from_file(infilename01).zoom(2,2)
    p11 = pyvips.Image.new_from_file(infilename11).zoom(2,2)
    w = p00.width
    h = p00.height

    index = pyvips.Image.new_from_array([[0, 1], [2, 3]]).replicate(w/2, h/2)
    outimg = index.case([p00, p10, p01, p11])

    # writing output image
    writeimage(["-f", outfmt, outimg, outfilename])
    exit()

# subtract background image (scaled and downsized)
# syntax: imbgsub [-f] [-bgm bgmult] [-m outmult] [-b outbg] inpnm bgimg outpnm
# processing:
#   - divide bgimg by bgmult and resize to fit inpnm
#   - subtract modified bgimg
#   - multiply by outmult and shift bg to match outbg
def imbgsub(param):
    outfmt='pnm'
    bgmult=0
    outmult=1
    outbg=1000
    if(param[0]=='-f'):
        outfmt='fits'
        del param[0]
    if(param[0]=='-bgm'):
        bgmult=float(param[1])
        del param[0:2]
    if(param[0]=='-m'):
        outmult=float(param[1])
        del param[0:2]
    if(param[0]=='-b'):
        outbg=float(param[1])
        del param[0:2]
    infilename = param[0]
    bgfilename = param[1]
    outfilename = param[2]

    # reading input images
    if (infilename and infilename != '-'):
        inimg = pyvips.Image.new_from_file(infilename)
    else:
        source = pyvips.Source.new_from_descriptor(sys.stdin.fileno())
        inimg = pyvips.Image.new_from_source(source, "")
    bgimg = pyvips.Image.new_from_file(bgfilename)

    # divide bgimg by bgmult and resize to fit inimg
    xscale=inimg.width/bgimg.width
    yscale=inimg.height/bgimg.height
    bgimg2=bgimg.linear(1/bgmult, 0).resize(xscale, vscale=yscale, centre=True)

    # subtract bgimg2
    outimg=inimg.subtract(bgimg2).linear(outmult, outbg).rint().cast('ushort')

    # output
    # writing output image
    writeimage(["-f", outfmt, outimg, outfilename])

    exit()


# subtract column- or row-pattern
# syntax: impatsub [-r] [-f] [-a add] infile [outfile]
def impatsub(param):
    pattern='column'
    outfmt='pnm'
    outadd=0
    if(param[0]=='-r'):
        pattern='row'
        del param[0]
    if(param[0]=='-f'):
        outfmt='fits'
        del param[0]
    if(param[0]=='-a'):
        outadd=float(param[1])
        del param[0:2]
    #if(param[0]=='-m'):
    #    outmult=float(param[1])
    #    del param[0:2]
    infilename = param[0]
    outfilename = param[1]

    # reading input image
    if (infilename and infilename != '-'):
        inimg = pyvips.Image.new_from_file(infilename)
    else:
        source = pyvips.Source.new_from_descriptor(sys.stdin.fileno())
        inimg = pyvips.Image.new_from_source(source, "")

    w=inimg.width
    h=inimg.height
    n=inimg.bands
    print("bands=", n, file=sys.stderr)

    # check outfmt
    if ((n==2 or n>3) and outfmt != 'fits'):
        print("ERROR: bands=", n, "is supported only by FITS file output format (use option -f)", file=sys.stderr)
        exit(-1)

    if (n>10):
        n=10
    for i in range(n):
        imslice=inimg.extract_band(i)
        x=inimg.avg()
        print("i=", i, " avg=", imslice.avg(), file=sys.stderr)
        if (pattern == 'column'):
            index=int(w/2)
            rankimg=imslice.rank(w, 1, index).crop(index, 0, 1, h).replicate(w,1)
        else:
            index=int(h/2)
            rankimg=imslice.rank(1, h, index).crop(0, index, w, 1).replicate(1,h)
        if (i==0):
            outimg=imslice.subtract(rankimg).linear(1,outadd)
        else:
            outimg=outimg.bandjoin(imslice.subtract(rankimg).linear(1,outadd))

    # output
    # writing output image
    writeimage(["-f", outfmt, outimg, outfilename])

    exit()


# write image to file or stdout (default: PNM file)
# syntax: writeimage [-16] [-f format] image [outfilename]
# supported output file formats: PBM PGM PPM PNM TIF PNG FITS
def writeimage(param):
    fmt='pnm'
    depth=None
    strip=None
    filename=None
    if(param[0]=='-16'):
        depth=16
        del param[0]
    if(param[0]=='-f'):
        # TODO: lowercase
        fmt=param[1]
        del param[0:2]
    if isinstance(param[0], pyvips.vimage.Image):
        image = param[0]
    else:
        image = pyvips.Image.new_from_file(param[0])
    if(len(param)>1):
        filename = param[1]

    if (fmt == "pnm" or fmt == "ppm" or fmt == "pgm" or fmt == "pbm"):
        strip=True
    if (fmt == "fits" or fmt == "tif" or fmt == "tiff" or fmt == "png"):
        strip=False
    if (strip == None):
        print("ERROR: unsupported output image file format", file=sys.stderr)
        exit(-1)

    if (depth == 16 or image.max() > 255):
        if (image.bands == 1):
            image=image.cast('ushort').copy(interpretation="grey16")
        else:
            image=image.cast('ushort').copy(interpretation="rgb16")

    if (pyvips.base.at_least_libvips(8,14)):
        # target format pnm is recognized and chooses the smallest possible
        # output format
        pass
    else:
        if (image.bands == 1):
            if (fmt == "pnm"): fmt="pgm"
        else:
            if (fmt == "pnm"): fmt="ppm"

    if (filename and filename != '-'):
        if (fmt=='fits'):
            image.fitssave(filename)
        else:
            # workaraound for ppmsave in libvips 8.12.1 (Ubuntu 22.04)
            # were format determines the output image format
            if (False and pyvips.base.at_least_libvips(8,12)):
                print("WARNING: using fallback in writeimage", file=sys.stderr)
                if (image.bands == 1):
                    if (fmt == "pnm" or fmt == "ppm"): fmt="pgm"
                else:
                    if (fmt == "pnm"): fmt="ppm"
                tmpfile=NamedTemporaryFile(delete=False)
                image.ppmsave(tmpfile.name, format=fmt, strip=1)
                #os.rename(tmpfile.name, filename)
                shutil.move(tmpfile.name, filename)
            else:
                # output file format is picked from image.bands
                # format is not used
                # file extension is ignored
                target = pyvips.Target.new_to_file(filename)
                image.write_to_target(target, "." + fmt, strip=strip)
    else:
        #print("INFO: writing to stdout", file=sys.stderr)
        target = pyvips.Target.new_to_descriptor(sys.stdout.fileno())
        image.write_to_target(target, "." + fmt, strip=strip)
    exit()


# convert vips image into numpy array
def v2np(vipsimage):
    # map vips formats to np dtypes
    format_to_dtype = {
        'uchar': np.uint8,
        'char': np.int8,
        'ushort': np.uint16,
        'short': np.int16,
        'uint': np.uint32,
        'int': np.int32,
        'float': np.float32,
        'double': np.float64,
        'complex': np.complex64,
        'dpcomplex': np.complex128,
    }
    return np.ndarray(buffer=vipsimage.write_to_memory(),
        dtype=format_to_dtype[vipsimage.format],
        shape=[vipsimage.height, vipsimage.width, vipsimage.bands])

# convert vips image into numpy pixel array containing x y value(s)
def v2pixarray(vipsimage):
    size = vipsimage.width * vipsimage.height
    #img = vipsimage.copy(width=1, height=size)
    xy = pyvips.Image.xyz(vipsimage.width, vipsimage.height)
    xyarr = v2np(xy)
    #print('xyarr: ', xyarr.shape)
    imgarr = v2np(vipsimage)
    #print('imgarr: ', imgarr.shape)
    pixarr = np.column_stack((xyarr.reshape(size, 2), imgarr.reshape(size, vipsimage.bands)))
    return pixarr

# list pixel values (optionally using thresholds)
# syntax: listpixels [-c] [-0|-1] img x0 y0 w h [low] [high]
# output: x y val1 <val2> <val3>
# note: x0 y0 is left-top pixel (starting at 0 0)
def listpixels(param):
    low=0
    high=2**16-1
    coord=False
    useminval=False
    usemaxval=False
    if(param[0]=='-c'):
        coord=True
        del param[0]
    if(param[0]=='-0'):
        useminval=True
        del param[0]
    if(param[0]=='-1'):
        usemaxval=True
        del param[0]
    infilename = param[0]
    x0 = int(param[1])
    y0 = int(param[2])
    w  = int(param[3])
    h  = int(param[4])
    if(len(param)>5):
        low = int(param[5])
    if(len(param)>6):
        high = int(param[6])

    # reading input images
    if (infilename and infilename != '-'):
        inimg = pyvips.Image.new_from_file(infilename)
    else:
        source = pyvips.Source.new_from_descriptor(sys.stdin.fileno())
        inimg = pyvips.Image.new_from_source(source, "")
    if (w<1): w=inimg.width
    if (h<1): h=inimg.height
    area = inimg.crop(x0, y0, w, h)

    # converting to array
    if (coord):
        arr=v2pixarray(area)
        arr[:, 0] += x0
        arr[:, 1] += y0
    else:
        arr=v2np(area).reshape(area.width*area.height, area.bands)
    #print('arr: ', arr.shape, file=sys.stderr)
    #np.savetxt(sys.stdout, arr, '%d')
    
    # get minval and maxval from image data type
    minval=0
    maxval=-1
    #print('format:', inimg.format, ' interpretation:', inimg.interpretation, file=sys.stderr)
    if (inimg.format == 'uchar' or inimg.format == 'char'):
        maxval=2**8-1
    elif (inimg.format == 'ushort' or inimg.format == 'short'):
        maxval=2**16-1
    if (maxval < 0):
        printf(sys.stderr, 'ERROR: listpixels: unsupported image format ', inimg.format)
        exit(-1)
    
    # set limits
    if (useminval):
        low=minval
        high=minval
    if (usemaxval):
        low=maxval
        high=maxval

    # create mask image
    #print('minval=', minval, ' maxval=', maxval, file=sys.stderr)
    #print('low=', low, ' high=', high, file=sys.stderr)
    if (inimg.bands == 1):
        imgmask = (area[0] >= low) & (area[0] <= high)
    if (inimg.bands == 3):
        imgmask = \
            (area[0] >= low) & (area[0] <= high) & \
            (area[1] >= low) & (area[1] <= high) & \
            (area[2] >= low) & (area[2] <= high)
    
    # convert to boolean mask array
    mask = v2np(imgmask > 0).flatten()

    # apply mask and print results
    np.savetxt(sys.stdout, arr[mask>0, :], '%d')
    exit()




if __name__ == "__main__":
    import sys
    globals()[sys.argv[1]](sys.argv[2:])
