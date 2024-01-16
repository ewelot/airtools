#!/usr/bin/python3

VERSION="2.3.3"
"""
CHANGELOG
    2.3.3 - 13 Jan 2024
        * cubeslice: complete rewrite
        * new functions: immedian immask debayer_halfsize

    2.3.2 - 08 Dec 2023
        * svgtopbm: bugfix: workaround by setting outfmt=pgm because of
            strange results when using pbm output
        * regstat: changed thres from 114 to 128 to match area of old regstat
            function in airfun.sh

    2.3.1 - 13 Nov 2023
        * new function: mkcluster

    2.3 - 17 May 2023
        * added dependency on rawpy
        * pnmccdred, cleanhotpixel, debayer_malvar, debayer_simple: sanitize
            parameter type checkings
        * impatsub: added option -m <badmask>
        * createmask: added option -margin <width>
        * new functions: rawtogray rawtorgb debayer_bayer2rgb debayer_vng
            debayer_ahd

    2.3a1 - 21 Apr 2023
        * imstat: added options -b (to indicate bayered image) and -s <scale>
            to multiply result by scale
        * pnmccdred: added option -debayer <mode> to include demosaicing
            of CFA images by using either algorithm from Malvar (default,
            mode=malvar) or simple bilinear interpolation
        * writeimage: improve handling of FITS images
        * listpixels: show values at higher precision if image data type is
            float/double
        * new functions: cubeslice imgain imnoise createmask combinemasks
            debayer_simple debayer_malvar asciitoimage

    2.2 - 05 Feb 2023
"""

import sys
import os
import shutil
import math
import re
from tempfile import NamedTemporaryFile
from collections import defaultdict
from csv import DictReader
from subprocess import run, Popen, PIPE
import ephem
import numpy as np
import exifread

import pyvips
import rawpy

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

# extract single image band (2D image) from image cube
# band number starts with 1
# cubeslice [-fmt fmt] imagecube band [outimage]
def cubeslice(param):
    outfmt='pnm'
    outfilename=""
    for i in range(3):
        if (not param or not isinstance(param[0], str)): break
        if(param[0]=='-fmt'):
            outfmt=param[1]
            del param[0:2]

    # parameters
    infilename=param[0]
    band=int(param[1])
    if(len(param)>2):
        outfilename = param[2]

    # reading input image
    if (infilename and infilename != '-'):
        inimg = pyvips.Image.new_from_file(infilename)
    else:
        source = pyvips.Source.new_from_descriptor(sys.stdin.fileno())
        inimg = pyvips.Image.new_from_source(source, "")

    # check number of bands
    if (band > inimg.bands):
        print("ERROR: too few input image bands", file=sys.stderr)
        exit(-1)

    # slicing
    outimg=inimg[band-1]

    # writing output image
    writeimage(["-fmt", outfmt, outimg, outfilename])


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
    writeimage(["-fmt", outfmt, outimg, outfile])


# image statistics (per channel output: min max mean (stddev))
# usage: imstat [-m] [-b] [-s scale] image
def imstat(param):
    medianbox=""
    scale=1
    is_bayered=False
    for i in range(3):
        if(param[0]=='-m'):
            medianbox=3
            del param[0]
        if(param[0]=='-b'):
            is_bayered=True
            del param[0]
        if(param[0]=='-s'):
            scale=float(param[1])
            del param[0:2]
    infile = param[0]

    # reading input image
    if (infile and infile != '-'):
        inimg = pyvips.Image.new_from_file(infile)
    else:
        source = pyvips.Source.new_from_descriptor(sys.stdin.fileno())
        inimg = pyvips.Image.new_from_source(source, "")

    if (not is_bayered):
        if(medianbox):
            statsimg=[inimg.median(medianbox).stats()]
        else:
            statsimg=[inimg.stats()]
    else:
        w=inimg.width
        h=inimg.height
        if(medianbox):
            statsimg  = [inimg.subsample(2, 2).median(medianbox).stats()]
            statsimg += [inimg.embed(-1, 0, w, h).subsample(2, 2).median(medianbox).stats()]
            statsimg += [inimg.embed(0, -1, w, h).subsample(2, 2).median(medianbox).stats()]
            statsimg += [inimg.embed(-1, -1, w, h).subsample(2, 2).median(medianbox).stats()]
        else:
            statsimg  = [inimg.subsample(2, 2).stats()]
            statsimg += [inimg.embed(-1, 0, w, h).subsample(2, 2).stats()]
            statsimg += [inimg.embed(0, -1, w, h).subsample(2, 2).stats()]
            statsimg += [inimg.embed(-1, -1, w, h).subsample(2, 2).stats()]
        
    # writing output values
    for j in range(len(statsimg)):
        if (j>0): print(" ", end='')
        for i in range(1, statsimg[j].height):
            if (i>1): print(' ', end='')
            print('{:.0f} {:.0f} {:.2f} ({:.2f})'.format(
                statsimg[j].getpoint(0, i)[0] * scale,
                statsimg[j].getpoint(1, i)[0] * scale,
                statsimg[j].getpoint(4, i)[0] * scale,
                statsimg[j].getpoint(5, i)[0] * scale
                ), end='')

# determine gain from a pair of light images and pair of dark images (or
#   known value of dark noise)
# note: light images should be monochromatic
# usage: imgain [-c croppercent] light1 light2 dark1 dark2
#    or: imgain [-c croppercent] -n darknoise light1 light2
def imgain(param):
    croppercent=-1
    darknoise=""    # stddev
    if(param[0]=='-c'):
        croppercent=int(param[1])
        del param[0:2]
    if(param[0]=='-n'):
        darknoise=float(param[1])
        del param[0:2]
    light1name = param[0]
    light2name = param[1]
    if (len(param)>2):
        dark1name = param[2]
        dark2name = param[3]
    else:
        if (darknoise == ""):
            print('ERROR: missing parameter', file=sys.stderr)
            exit(-1)
    
    # read images
    light1img = pyvips.Image.new_from_file(light1name)
    light2img = pyvips.Image.new_from_file(light2name)
    if (len(param)>2):
        dark1img = pyvips.Image.new_from_file(dark1name)
        dark2img = pyvips.Image.new_from_file(dark2name)

    # statistics from light images
    w=light1img.width
    h=light1img.height
    if (croppercent < 0):
        croppercent=5
        if(w<1000): croppercent=5000/w
        if(w<50): croppercent=100
    cp=croppercent/100
    mp=(1-cp)/2
    light1img=light1img.crop(int(w*mp), int(h*mp), int(w*cp), int(h*cp))
    light2img=light2img.crop(int(w*mp), int(h*mp), int(w*cp), int(h*cp))
    lmed = np.median(v2np(light1img.add(light2img)))/2
    ldiff = light1img.subtract(light2img)
    lsd = ldiff.deviate()/math.sqrt(2)
    print("lights:  med={:.0f}  diff={:.0f}  sd={:.1f}".format(lmed, ldiff.avg(), lsd))

    # statistics from dark images
    if (len(param)>2):
        dark1img=dark1img.crop(int(w*mp), int(h*mp), int(w*cp), int(h*cp))
        dark2img=dark2img.crop(int(w*mp), int(h*mp), int(w*cp), int(h*cp))
        dmed = np.median(v2np(dark1img.add(dark2img)))/2
        ddiff = dark1img.subtract(dark2img)
        dsd = ddiff.deviate()/math.sqrt(2)
        print("darks:   med={:.0f}  sd={:.1f}".format(dmed, dsd))
        signal=lmed-dmed
        variance=lsd*lsd-dsd*dsd
    else:
        signal=lmed
        variance=lsd*lsd-darknoise*darknoise

    gain=signal/variance
    print("gain={:.3f} e-/ADU".format(gain))
    

# create noise image
# usage: imnoise [-fmt outfmt] inimg outimg gain [darkvalue] [darknoise]
# gain is in e-/ADU, anything else in ADU
def imnoise(param):
    outfmt='pnm'
    darkvalue=0
    darknoise=0
    if(param[0]=='-fmt'):
        outfmt=param[1]
        del param[0:2]
    #if(param[0]=='-m'):
    #    outmult=float(param[1])
    #    del param[0:2]
    infilename = param[0]
    outfilename = param[1]
    gain = float(param[2])
    if (len(param) > 3):
        darkvalue = float(param[3])
    if (len(param) > 4):
        darknoise = float(param[4])

    # reading input image
    if (infilename and infilename != '-'):
        inimg = pyvips.Image.new_from_file(infilename)
    else:
        source = pyvips.Source.new_from_descriptor(sys.stdin.fileno())
        inimg = pyvips.Image.new_from_source(source, "")

    signaladu = inimg.linear(1, -1*darkvalue)
    photnoise2 = signaladu.linear(1/gain, 0)    # in ADU
    noise2 = photnoise2.linear(1, darknoise*darknoise)
    outimg = noise2.math2_const('pow', 0.5)
    writeimage(["-fmt", outfmt, outimg, outfilename])


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


def rawimsize(param):
    rawfilename=param[0]
    raw = rawpy.imread(rawfilename)
    print(raw.sizes.width, raw.sizes.height)


# print basic info about raw image
def rawinfo(param):
    rawfilename=param[0]

    tags = exifread.process_file(open(rawfilename, 'rb'))
    for key, value in tags.items():
        if (key != 'JPEGThumbnail'):
            if (key.startswith('Image')):
                print(f'{key}: {value}')

    try:
        raw = rawpy.imread(rawfilename)
    except:
        print("ERROR: unable to read file by using rawpy", file=sys.stderr)
        exit(-1)

    print("raw type:   ", raw.raw_type)
    print("color desc: ", raw.color_desc)
    print("raw pattern:", raw.raw_pattern.tolist())
    print("black:      ", raw.black_level_per_channel)
    print("white:      ", raw.white_level)
    print("16bit-mult: ", int(2**16 / raw.white_level))
    print("image size: ", raw.sizes.width, raw.sizes.height)
    #print("sizes:      ", raw.sizes)



# linear CFA gray image
# note: implicite scaling to full 16bit range
def rawtogray(param):
    outfmt='pgm'
    rawfilename=param[0]
    outfilename=param[1]

    raw = rawpy.imread(rawfilename)

    cfa = raw.raw_image_visible.copy()

    # convert to vips image   
    height, width = cfa.shape
    bands=1
    nparr = cfa.reshape(width * height)
    outimg = pyvips.Image.new_from_memory(nparr.data, width, height, bands,
        np_dtype_to_vips_format[str(cfa.dtype)])
    #print("data range:", outimg.min(), outimg.max())
    
    # stretch to 16bit
    mult=int(2**16 / raw.white_level)
    if (mult>1):
        outimg = outimg.linear(mult, 0)
    
    # writing output image
    writeimage(["-fmt", outfmt, outimg, outfilename])


# linear 16bit RGB
# note: implicite scaling to full 16bit range
def rawtorgb(param):
    outfmt='ppm'
    develop=False
    for i in range(2):
        if (not param or not isinstance(param[0], str)): break
        if(param[0]=='-d'):
            develop=True
            del param[0]

    rawfilename=param[0]
    outfilename=param[1]
    algorithm=1     # 0-bilinear, 1-VNG, 2-PPG, 3-AHD
    colorspace=0    # 0-raw 1-sRGB 2-Adobe

    raw = rawpy.imread(rawfilename)

    if (develop):
        rgb = raw.postprocess()
    else:
        rgb = raw.postprocess(
            user_flip=0,
            user_wb=(1,1,1,1),
            user_black=0,
            demosaic_algorithm=rawpy.DemosaicAlgorithm(algorithm),
            output_color=rawpy.ColorSpace(colorspace),
            gamma=(1,1),
            no_auto_bright=True,
            output_bps=16)

    # convert to vips image   
    height, width, bands = rgb.shape
    nparr = rgb.reshape(width * height * bands)
    outimg = pyvips.Image.new_from_memory(nparr.data, width, height, bands,
        np_dtype_to_vips_format[str(rgb.dtype)])

    # stretch to 16bit
    mult=int(2**16 / raw.white_level)
    if (mult>1):
        outimg = outimg.linear(mult, 0)

    # writing output image
    writeimage(["-fmt", outfmt, outimg, outfilename])


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
# syntax: pnmccdred [-v] [-fmt outfmt|pnm] [-8|-16] [-gray] [-preadd val] [-premult val] [-flip] [-prerot]
#   [-bpat bayerpattern_up] [-debayer mode] [-cgeom wxh+x+y ] [-resize wxh|mult] [-rot] [-mult mult] [-add add] inpnm outpnm <dark> <flat> <bad>
def pnmccdred(param):
    outfmt='pnm'
    outgray=False
    preadd=0
    premult=1
    bayerpattern="" # only used if bad is provided, row-order is bottom-up
    debayer_mode="" # simple or malvar
    cgeom=""
    size=""   # either wxh or size multiplier
    depth=False
    flip=False
    prerot=False
    rot=False
    mult=False
    add=False
    dark=False
    flat=False
    bad=False
    verbose=False
    for i in range(15):
        if (not param or not isinstance(param[0], str)): break
        if(param[0]=='-h' or param[0]=='--help'):
            print("syntax: pnmccdred [-v] [-fmt outfmt|pnm] [-8|-16] [-gray] [-preadd val] [-premult val] [-flip] [-prerot]",
                "[-bpat bayerpattern] [-debayer algorithm] [-cgeom wxh+x+y ] [-resize wxh|mult] [-rot] [-mult mult] [-add add]",
                "inpnm outpnm [dark] [flat] [bad]", file=sys.stderr)
            return()
        elif(param[0]=='-v'):
            verbose=True
            del param[0]
        elif(param[0]=='-fmt'):
            outfmt=param[1]
            del param[0:2]
        elif(param[0]=='-8'):
            depth=8
            del param[0]
        elif(param[0]=='-16'):
            depth=16
            del param[0]
        elif(param[0]=='-gray'):
            outgray=True
            del param[0]
        elif(param[0]=='-preadd'):
            preadd=float(param[1])
            del param[0:2]
        elif(param[0]=='-premult'):
            premult=float(param[1])
            del param[0:2]
        elif(param[0]=='-flip'):
            flip=True
            del param[0]
        elif(param[0]=='-prerot'):
            prerot=True
            del param[0]
        elif(param[0]=='-bpat'):
            bayerpattern=param[1]
            del param[0:2]
        elif(param[0]=='-debayer'):
            debayer_mode=param[1]
            del param[0:2]
        elif(param[0]=='-cgeom'):
            cgeom=param[1]
            del param[0:2]
        elif(param[0]=='-resize'):
            size=param[1]
            del param[0:2]
        elif(param[0]=='-rot'):
            rot=True
            del param[0]
        elif(param[0]=='-mult'):
            mult = tuple(float(val) for val in tuple(param[1].split(",")))
            del param[0:2]
        elif(param[0]=='-add'):
            add = tuple(float(val) for val in tuple(param[1].split(",")))
            del param[0:2]
    
    if (not param or len(param)<2 or len(param)>5):
        print("ERROR: pnmccdred: wrong number of parameters (try -h).", file=sys.stderr)
        exit(-1)

    infilename = param[0]
    outfilename = param[1]
    np = len(param)
    if (np > 2): dark = param[2]
    if (np > 3): flat = param[3]
    if (np > 4): bad  = param[4]

    # reading input image
    if (infilename and infilename != '-'):
        try:
            inimg = pyvips.Image.new_from_file(infilename)
            if verbose:
                print("# image loaded by libvips", file=sys.stderr)
        except:
            try:
                raw = rawpy.imread(infilename)
                # stretch to 16bit
                premult=premult * int(2**16 / raw.white_level)
                cfa = raw.raw_image_visible.copy()
                if verbose:
                    print("# raw DSLR image loaded by rawpy", file=sys.stderr)
            except:
                print("ERROR: unsupported input image format.", file=sys.stderr)
                exit(-1)
            # convert to vips image   
            height, width = cfa.shape
            bands=1
            nparr = cfa.reshape(width * height)
            inimg = pyvips.Image.new_from_memory(nparr.data, width, height, bands,
                np_dtype_to_vips_format[str(cfa.dtype)])
            # TODO: check for possible scaling to 16bit in which case we must adjust mult
    else:
        source = pyvips.Source.new_from_descriptor(sys.stdin.fileno())
        inimg = pyvips.Image.new_from_source(source, "")

    # store original image size
    width = inimg.width
    height = inimg.height
    
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
        width=int(x[0])
        height=int(x[1])
    if size:
        y=re.split('x', size)
        if (len(y) == 2):
            xscale=int(y[0])/width
            yscale=int(y[1])/height
            code += """.resize(xscale, vscale=yscale, kernel='linear')"""
        else:
            code += """.resize(float(size), kernel='linear')"""
    if rot:
        code += """.rot180()"""
    if mult:
        if add:
            code += """.linear(mult, add)"""
        else:
            code += """.linear(mult, 0)"""
    else:
        if add: code += """.linear(1, add)"""
    if outgray:
        channelmult=[0.26,0.40,0.34]
        for i in range(len(channelmult)):
            channelmult[i] = channelmult[i] * 3
        if (inimg.bands == 2):
            code += """.flatten()"""
        if (inimg.bands == 3):
            code += """.linear(channelmult, 0).bandmean()"""
        if (inimg.bands == 4):
            code += """.flatten().linear(channelmult, 0).bandmean()"""
        if (inimg.bands > 4):
            code += """.flatten().bandmean()"""

    # options passed to writeimage
    wopts = ["-fmt", outfmt]
    if (verbose):
        wopts.append("-v")
    if (depth == 16):
        wopts.append("-16")
    if (depth == 8):
        wopts.append("-8")
    if (verbose):
        print("# wopts =", wopts, file=sys.stderr)


    if bad:
        tmpimg = eval(code)
        # TODO: parameters cgeom and rot must be applied to bad as well 
        if (bayerpattern):
            if (debayer_mode):
                tmpimg2 = cleanhotpixel(["-fmt", outfmt, "-b", bayerpattern, tmpimg, bad, ""])
                debayer([debayer_mode, "-fmt", outfmt, "-b", bayerpattern, tmpimg2, outfilename])
                #debayer_malvar(["-fmt", outfmt, "-b", bayerpattern, tmpimg2, outfilename])
            else:
                cleanhotpixel(["-fmt", outfmt, "-b", bayerpattern, tmpimg, bad, outfilename])
        else:
            cleanhotpixel(["-fmt", outfmt, tmpimg, bad, outfilename])
    else:
        if (bayerpattern and debayer_mode):
            tmpimg = eval(code)
            debayer([debayer_mode, "-fmt", outfmt, "-b", bayerpattern, tmpimg, outfilename])
            #debayer_malvar(["-fmt", outfmt, "-b", bayerpattern, tmpimg, outfilename])
        else:
            outimg = eval(code)
            wopts.append(outimg)
            wopts.append(outfilename)
            writeimage(wopts)


#ppmtogray $ppm $tmp1 $1,$2,$3
# convert from PPM to PGM using user supplied channel multipliers
# syntax: ppmtogray -f inppm outpgm [multR,multG,multB]
def ppmtogray(param):
    outfmt='pgm'
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
    #outimg = inimg.linear(multnorm, 0).bandmean().rint().copy(interpretation="grey16")
    outimg = inimg.linear(multnorm, 0).bandmean()

    # writing output image
    writeimage(["-fmt", outfmt, outimg, outfilename])


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
    writeimage(["-fmt", outfmt, outimg, outfilename])


def svgtopbm(param):
    # convert svg areas (circle/polygon/box) to pbm
    # regions are interpreted as good pixel regions (white, pgm value 255, pbm value 0)
    # TODO: currently output is a bi-level PGM image
    outfmt='pgm'
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
    #outimg = (inimg.Colourspace("b-w") > 128).ifthenelse(1,0)
    # writing output image
    writeimage(["-fmt", outfmt, outimg, outfilename])


# apply badmask to image 
def immask(param):
    outfmt='pnm'
    outfilename=""
    for i in range(1):
        if(param[0]=='-fmt'):
            outfmt=param[1]
            del param[0:2]
    infilename = param[0]
    maskfilename = param[1]
    if (len(param) > 2):
        outfilename = param[2]

    # reading input image
    if (infilename and infilename != '-'):
        inimg = pyvips.Image.new_from_file(infilename)
    else:
        source = pyvips.Source.new_from_descriptor(sys.stdin.fileno())
        inimg = pyvips.Image.new_from_source(source, "")
    maskimg=pyvips.Image.new_from_file(maskfilename)
    
    outimg=(maskimg > 0).ifthenelse(0, inimg)
    # writing output image
    writeimage(["-fmt", outfmt, outimg, outfilename])


# create image mask using simple thresholding
#   valid pixels inside mask if data intensities are within lowlimit and highlimit
# usage: createmask [-fmt outfmt] [-medsub] [-low lowlimit] [-high highlimit] \
#   [-margin width] [-m inmask] <inimg> <outimg>
def createmask(param):
    outfmt='png'
    lowerlimit=''
    upperlimit=''
    margin=''
    maskfilename=''
    medsub=False
    verbose=''
    for i in range(5):
        if(param[0]=='-fmt'):
            outfmt=param[1]
            del param[0:2]
        elif(param[0]=='-medsub'):
            medsub=True
            del param[0]
        elif(param[0]=='-low'):
            lowerlimit=float(param[1])
            del param[0:2]
        elif(param[0]=='-high'):
            upperlimit=float(param[1])
            del param[0:2]
        elif(param[0]=='-margin'):
            margin=int(param[1])
            del param[0:2]
        elif(param[0]=='-m'):
            maskfilename=param[1]
            del param[0:2]
    infilename = param[0]
    outfilename = param[1]

    # reading input image
    if (infilename and infilename != '-'):
        inimg = pyvips.Image.new_from_file(infilename)
    else:
        source = pyvips.Source.new_from_descriptor(sys.stdin.fileno())
        inimg = pyvips.Image.new_from_source(source, "")

    # optionally subtract median background
    if (medsub):
        inimg = inimg.subtract(inimg.median(3))

    # combine conditions
    if (maskfilename):
        inmask = pyvips.Image.new_from_file(maskfilename)
        cond = inmask > 0
    else:
        cond = inimg != 0
    if (verbose):
        print("# cond.min=", cond.min(), file=sys.stderr)
        print("# cond.max=", cond.max(), file=sys.stderr)

    # simple thresholding
    if (lowerlimit):
        cond = cond & (inimg >= lowerlimit)
        if (verbose):
            print("# low=", lowerlimit, file=sys.stderr)
            print("# cond.min=", cond.min(), file=sys.stderr)
            print("# cond.max=", cond.max(), file=sys.stderr)
    if (upperlimit):
        cond = cond & (inimg <= upperlimit)
        if (verbose):
            print("# high=", upperlimit, file=sys.stderr)
            print("# cond.min=", cond.min(), file=sys.stderr)
            print("# cond.max=", cond.max(), file=sys.stderr)

    outimg = cond
    
    # optionally clip border from mask
    if (margin):
        w=inimg.width
        h=inimg.height
        outimg = outimg.crop(margin, margin, w-2*margin, h-2*margin).embed(margin, margin, w, h, extend='black')

    # writing output image
    writeimage(["-fmt", outfmt, outimg, outfilename])


# combine masks using 'or' (default) or 'and' and optionally add border pixels
# usage: combinemasks [-fmt outfmt] [-m mode] [-b borderwidth] [-neg] mask1 mask2 ...
# note: only first image band of any input mask image is used
def combinemasks(param):
    outfmt='png'
    mode='or'   # and == using min, or == using max
    bwidth=0
    negate=False
    for i in range(4):
        if(param[0]=='-fmt'):
            outfmt=param[1]
            del param[0:2]
        if(param[0]=='-m'):
            mode=param[1]
            del param[0:2]
        if(param[0]=='-b'):
            bwidth=int(param[1])
            del param[0:2]
        if(param[0]=='-neg'):
            negate=True
            del param[0]
    outfilename = param[len(param)-1]

    # reading input images
    inimgarray = [pyvips.Image.new_from_file(param[i])[0] for i in range(len(param)-1)]
    
    # index
    index=-2
    if ((mode == 'or') or (mode == 'max')):
        index=len(param)-2
    if ((mode == 'and') or (mode == 'min')):
        index=0
    if (index < -1):
        print("ERROR in combinemasks: unknown mode", file=sys.stderr)
        return
    
    # sort and extract given index
    outimg = inimgarray[0].bandrank(inimgarray[1:], index=index) > 0

    if (bwidth > 0):
        w=outimg.width
        h=outimg.height
        outimg = outimg.crop(bwidth, bwidth, w-2*bwidth, h-2*bwidth).embed(bwidth, bwidth, w, h, extend='white')
    if (negate):
        outimg = outimg == 0

    # writing output image
    writeimage(["-fmt", outfmt, outimg, outfilename])


# replace border by white (or black) pixels
# syntax: pnmreplaceborder [-fmt outfmt] [-b] <in> <out> [bwidth|2]
def pnmreplaceborder(param):
    outfmt='pnm'
    bwidth=2
    bcolor="white"
    if(param[0]=='-fmt'):
        outfmt=param[1]
        del param[0:2]
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
    writeimage(["-fmt", outfmt, outimg, outfilename])


# convolve b/w mask with disk-like mask to find clusters of bad pixels
def mkcluster(param):
    outfmt='pnm'
    if(param[0]=='-fmt'):
        outfmt=param[1]
        del param[0:2]
    infilename = param[0]
    outfilename = param[1]

    # reading input image
    if (infilename and infilename != '-'):
        inimg = pyvips.Image.new_from_file(infilename)
    else:
        source = pyvips.Source.new_from_descriptor(sys.stdin.fileno())
        inimg = pyvips.Image.new_from_source(source, "")

    # convolution kernels
    # TODO: use mask_ideal(7, 7, 1, optical=True, reject=True, uchar=True)
    kernel = pyvips.Image.new_from_array(np.asarray([
        [0,0,1,1,1,0,0],
        [0,1,1,1,1,1,0],
        [1,1,1,1,1,1,1],
        [1,1,1,1,1,1,1],
        [1,1,1,1,1,1,1],
        [0,1,1,1,1,1,0],
        [0,0,1,1,1,0,0]
        ]) / 255)
    dilatemask = pyvips.Image.mask_ideal(11, 11, 1, optical=True, reject=True, uchar=True)

    outimg=((inimg.conv(kernel) > 2).ifthenelse(1,0).conv(dilatemask) > 0).ifthenelse(1,0)

    # writing output image
    writeimage(["-fmt", outfmt, outimg, outfilename])


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
    thres=128   # matching old regstat
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


def tltest1(param):
    infilename = param[0]
    
    inimg = pyvips.Image.new_from_file(infilename)
    outimg = inimg.linear(0.9, 10)
    print("max=", outimg.max(), file=sys.stderr)
    print("bands=", outimg.bands, file=sys.stderr)
    print("format=", outimg.format, file=sys.stderr)
    print("coding=", outimg.coding, file=sys.stderr)
    print("interpretation=", outimg.interpretation, file=sys.stderr)
    outimg.ppmsave('x.nocast.pgm', format='pgm')
    maxval=outimg.max()
    if (maxval > 255):
        outimg.cast('ushort').ppmsave('x.ushort.pgm', format='pgm')
    else:
        outimg.cast('uchar').ppmsave('x.uchar.pgm', format='pgm')
    exit()

def pnmcombine(param):
    mode='mean' # sum, mean, median, stddev
    outfmt='pnm'
    if(param[0]=='-fmt'):
        outfmt=param[1]
        del param[0:2]
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
    if mode=="median":
        inimgarray = [pyvips.Image.new_from_file(param[i]) for i in range(len(param)-1)]
    else:
        inimgarray = [pyvips.Image.new_from_file(param[i], access='sequential') for i in range(len(param)-1)]


    if mode=="median":
        # determine median image
        outimg = inimgarray[0].bandrank(inimgarray[1:])
        #outimg = pyvips.Image.bandrank(inimgarray, len(inimgarray))
    elif mode=="mean":
        outimg = inimgarray[0]
        for i in range(1,len(inimgarray)):
            outimg = outimg.add(inimgarray[i]);
        #outimg = outimg.linear(1/len(inimgarray), 0).rint().cast('ushort')
        outimg = outimg.linear(1/len(inimgarray), 0)
    elif mode=="sum":
        outimg = inimgarray[0]
        for i in range(1,len(inimgarray)):
            outimg = outimg.add(inimgarray[i]);
        #outimg = outimg.rint()
    else:
        meanimg = inimgarray[0]
        for i in range(1,len(inimgarray)):
            meanimg = meanimg.add(inimgarray[i]);
        meanimg = meanimg.linear(1/len(inimgarray), 0).rint()
        outimg = inimgarray[0].subtract(meanimg).multiply(inimgarray[0].subtract(meanimg))
        for i in range(1,len(inimgarray)):
            outimg = outimg.add(inimgarray[i].subtract(meanimg).multiply(inimgarray[i].subtract(meanimg)));
        #outimg = outimg.linear(1/len(inimgarray), 0).pow(inimgarray[0].linear(0, 0.5)).rint()
        #outimg = outimg.linear(1/len(inimgarray), 0).math2_const("pow",0.5).rint().cast('ushort')
        outimg = outimg.linear(1/len(inimgarray), 0).math2_const("pow",0.5)

    # writing output image
    writeimage(["-fmt", outfmt, outimg, outfilename])


# debayer (demosaic) CFA image using given algorithm
# usage: debayer <algorithm> [-fmt outfmt] [-b bayerpattern_up] <image> [outimage]
def debayer(param):
    algorithm=param[0]
    del param[0]
    if (algorithm == 'malvar'):
        debayer_malvar(param)
    elif (algorithm == 'vng'):
        debayer_vng(param)
    elif (algorithm == 'ahd'):
        debayer_ahd(param)
    else:
        debayer_simple(param)


# debayer (demosaic) using simple bilinear interpolation
# usage: debayer_simple [-fmt outfmt] [-b bayerpattern_up] <image> [outimage]
def debayer_simple(param):
    bpat_up="RGGB"     # row-order: bottom up
    outfilename="-"
    outfmt="ppm"
    for i in range(2):
        if (not param or not isinstance(param[0], str)): break
        if(param[0]=='-fmt'):
            outfmt=param[1]
            del param[0:2]
        elif(param[0]=='-b'):
            bpat_up=param[1]
            del param[0:2]

    # reading input image
    if isinstance(param[0], pyvips.vimage.Image):
        image = param[0]
    else:
        infilename=param[0]
        if (infilename and infilename != '-'):
            image = pyvips.Image.new_from_file(infilename)
        else:
            source = pyvips.Source.new_from_descriptor(sys.stdin.fileno())
            image = pyvips.Image.new_from_source(source, "")

    if(len(param)>1):
        outfilename = param[1]

    # interpolation kernels
    gkernel = pyvips.Image.new_from_array(np.asarray(
        [[0, 1, 0],
         [1, 4, 1],
         [0, 1, 0]]) / 4)
    rbkernel = pyvips.Image.new_from_array(np.asarray(
        [[1, 2, 1],
         [2, 4, 2],
         [1, 2, 1]]) / 4)

    # convert bottom-up bayer pattern into top-down pattern
    bpat_down=bpat_up[2]+bpat_up[3]+bpat_up[0]+bpat_up[1]

    # mask for green/red/blue pixels
    w = image.width
    h = image.height
    if (bpat_down[1:2] == "G"):  # e.g. RGGB
        gmask = pyvips.Image.new_from_array([[0, 1], [1, 0]]).replicate(w/2, h/2)
        if (bpat_down[1] == "R"):
            rmask = pyvips.Image.new_from_array([[0, 0], [0, 1]]).replicate(w/2, h/2)
            bmask = pyvips.Image.new_from_array([[1, 0], [0, 0]]).replicate(w/2, h/2)
        else:
            rmask = pyvips.Image.new_from_array([[1, 0], [0, 0]]).replicate(w/2, h/2)
            bmask = pyvips.Image.new_from_array([[0, 0], [0, 1]]).replicate(w/2, h/2)
    else:
        gmask = pyvips.Image.new_from_array([[1, 0], [0, 1]]).replicate(w/2, h/2)
        if (bpat_down[0] == "R"):
            rmask = pyvips.Image.new_from_array([[0, 0], [1, 0]]).replicate(w/2, h/2)
            bmask = pyvips.Image.new_from_array([[0, 1], [0, 0]]).replicate(w/2, h/2)
        else:
            rmask = pyvips.Image.new_from_array([[0, 1], [0, 0]]).replicate(w/2, h/2)
            bmask = pyvips.Image.new_from_array([[0, 0], [1, 0]]).replicate(w/2, h/2)
    

    # convolve image and create color bands
    gconv = image.conv(gkernel)
    rbconv = image.conv(rbkernel)
    green = ((gmask > 0).ifthenelse(image, 0)).conv(gkernel)
    red   = ((rmask > 0).ifthenelse(image, 0)).conv(rbkernel)
    blue  = ((bmask > 0).ifthenelse(image, 0)).conv(rbkernel)
    outimage = red.bandjoin([green, blue])

    # writing output image
    writeimage(["-fmt", outfmt, outimage, outfilename])


def debayer_halfsize(param):
    bpat_up="RGGB"     # row-order: bottom up
    outfilename="-"
    outfmt="ppm"
    for i in range(2):
        if (not param or not isinstance(param[0], str)): break
        if(param[0]=='-fmt'):
            outfmt=param[1]
            del param[0:2]
        elif(param[0]=='-b'):
            bpat_up=param[1]
            del param[0:2]

    # reading input image
    if isinstance(param[0], pyvips.vimage.Image):
        image = param[0]
    else:
        infilename=param[0]
        if (infilename and infilename != '-'):
            image = pyvips.Image.new_from_file(infilename)
        else:
            source = pyvips.Source.new_from_descriptor(sys.stdin.fileno())
            image = pyvips.Image.new_from_source(source, "")

    if(len(param)>1):
        outfilename = param[1]

    # extract bayer cells
    w = image.width
    h = image.height
    ptl = image.subsample(2, 2)
    ptr = image.embed(-1, 0, w, h).subsample(2, 2)
    pbl = image.embed(0, -1, w, h).subsample(2, 2)
    pbr = image.embed(-1, -1, w, h).subsample(2, 2)

    # create half-size color image
    if (bpat_up == "RGGB"):
        red = pbl
        #green = ptl
        green = (ptl+pbr)/2
        blue = ptr
    outimage = red.bandjoin([green, blue])

    # writing output image
    #outimage.ppmsave(outfilename, format=outfmt, strip=1)
    writeimage(["-fmt", outfmt, outimage, outfilename])


# debayer (demosaic) using high-quality bilinear interpolation (Malvar et al.,
# https://www.microsoft.com/en-us/research/wp-content/uploads/2016/02/Demosaicing_ICASSP04.pdf
# usage: debayer_malvar [-fmt outfmt] [-b bayerpattern_up] <image> [outimage]
def debayer_malvar(param):
    bpat_up="RGGB"     # row-order: bottom up
    outfilename="-"
    outfmt="ppm"
    for i in range(2):
        if (not param or not isinstance(param[0], str)): break
        if(param[0]=='-fmt'):
            outfmt=param[1]
            del param[0:2]
        elif(param[0]=='-b'):
            bpat_up=param[1]
            del param[0:2]

    # reading input image
    if isinstance(param[0], pyvips.vimage.Image):
        image = param[0]
    else:
        infilename=param[0]
        if (infilename and infilename != '-'):
            image = pyvips.Image.new_from_file(infilename)
        else:
            source = pyvips.Source.new_from_descriptor(sys.stdin.fileno())
            image = pyvips.Image.new_from_source(source, "")

    if(len(param)>1):
        outfilename = param[1]

    # interpolation kernels
    g_at_rb_kernel = pyvips.Image.new_from_array(np.asarray(
        [[ 0,  0, -1,  0,  0],
         [ 0,  0,  2,  0,  0],
         [-1,  2,  4,  2, -1],
         [ 0,  0,  2,  0,  0],
         [ 0,  0, -1,  0,  0]]) / 8)
    rb_at_br_kernel = pyvips.Image.new_from_array(np.asarray(
        [[ 0,    0, -1.5,  0,  0  ],
         [ 0,    2,  0,    2,  0  ],
         [-1.5,  0,  6,    0, -1.5],
         [ 0,    2,  0,    2,  0  ],
         [ 0,    0, -1.5,  0,  0  ]]) / 8)
    rb_at_g_in_rb_row_kernel = pyvips.Image.new_from_array(np.asarray(
        [[ 0,    0,  0.5,  0,  0  ],
         [ 0,   -1,  0,   -1,  0  ],
         [-1,    4,  5,    4, -1  ],
         [ 0,   -1,  0,   -1,  0  ],
         [ 0,    0,  0.5,  0,  0  ]]) / 8)
    rb_at_g_in_br_row_kernel = pyvips.Image.new_from_array(np.asarray(
        [[ 0,    0, -1,    0,  0  ],
         [ 0,   -1,  4,   -1,  0  ],
         [ 0.5,  0,  5,    0,  0.5],
         [ 0,   -1,  4,   -1,  0  ],
         [ 0,    0, -1,    0,  0  ]]) / 8)

    # convert bottom-up bayer pattern into top-down pattern
    bpat_down=bpat_up[2]+bpat_up[3]+bpat_up[0]+bpat_up[1]

    # mask for green/red/blue pixels
    w = image.width
    h = image.height
    if (bpat_down[1:2] == "G"):
        gmask = pyvips.Image.new_from_array([[0, 1], [1, 0]]).replicate(w/2, h/2)
        if (bpat_down[1] == "R"):
            #  JPG              FITS
            #  B G B G ...      . . . .
            #  G R G R ...      G R G R ...
            #  . . . .          B G B G ...
            rmask = pyvips.Image.new_from_array([[0, 0], [0, 1]]).replicate(w/2, h/2)
            bmask = pyvips.Image.new_from_array([[1, 0], [0, 0]]).replicate(w/2, h/2)
            g_in_r_row_mask = pyvips.Image.new_from_array([[0, 0], [1, 0]]).replicate(w/2, h/2)
            g_in_b_row_mask = pyvips.Image.new_from_array([[0, 1], [0, 0]]).replicate(w/2, h/2)
        else:
            #  JPG              FITS
            #  R G R G ...      . . . .
            #  G B G B ...      G B G B ...
            #  . . . .          R G R G ...
            rmask = pyvips.Image.new_from_array([[1, 0], [0, 0]]).replicate(w/2, h/2)
            bmask = pyvips.Image.new_from_array([[0, 0], [0, 1]]).replicate(w/2, h/2)
            g_in_r_row_mask = pyvips.Image.new_from_array([[0, 1], [0, 0]]).replicate(w/2, h/2)
            g_in_b_row_mask = pyvips.Image.new_from_array([[0, 0], [1, 0]]).replicate(w/2, h/2)
    else:
        gmask = pyvips.Image.new_from_array([[1, 0], [0, 1]]).replicate(w/2, h/2)
        if (bpat_down[0] == "R"):
            #  JPG              FITS
            #  G B G B ...      . . . .
            #  R G R G ...      R G R G ...
            #  . . . .          G B G B ...
            rmask = pyvips.Image.new_from_array([[0, 0], [1, 0]]).replicate(w/2, h/2)
            bmask = pyvips.Image.new_from_array([[0, 1], [0, 0]]).replicate(w/2, h/2)
            g_in_r_row_mask = pyvips.Image.new_from_array([[0, 0], [0, 1]]).replicate(w/2, h/2)
            g_in_b_row_mask = pyvips.Image.new_from_array([[1, 0], [0, 0]]).replicate(w/2, h/2)
        else:
            #  JPG              FITS
            #  G R G R ...      . . . .
            #  B G B G ...      B G B G ...
            #  . . . .          G R G R ...
            rmask = pyvips.Image.new_from_array([[0, 1], [0, 0]]).replicate(w/2, h/2)
            bmask = pyvips.Image.new_from_array([[0, 0], [1, 0]]).replicate(w/2, h/2)
            g_in_r_row_mask = pyvips.Image.new_from_array([[1, 0], [0, 0]]).replicate(w/2, h/2)
            g_in_b_row_mask = pyvips.Image.new_from_array([[0, 0], [0, 1]]).replicate(w/2, h/2)
    

    # convolve image and create color bands
    green = (gmask == 0).ifthenelse(image.conv(g_at_rb_kernel),
        image)
    red   = (bmask > 0).ifthenelse(image.conv(rb_at_br_kernel),
        (g_in_r_row_mask > 0).ifthenelse(image.conv(rb_at_g_in_rb_row_kernel),
        (g_in_b_row_mask > 0).ifthenelse(image.conv(rb_at_g_in_br_row_kernel),
        image)))
    blue  = (rmask > 0).ifthenelse(image.conv(rb_at_br_kernel),
        (g_in_b_row_mask > 0).ifthenelse(image.conv(rb_at_g_in_rb_row_kernel),
        (g_in_r_row_mask > 0).ifthenelse(image.conv(rb_at_g_in_br_row_kernel),
        image)))
    outimage = red.bandjoin([green, blue])

    # writing output image
    writeimage(["-fmt", outfmt, outimage, outfilename])


def debayer_vng(param):
    debayer_bayer2rgb('VNG', param)

def debayer_ahd(param):
    debayer_bayer2rgb('AHD', param)

def debayer_bayer2rgb(method, param):
    bpat_up="RGGB"     # row-order: bottom up
    outfilename="-"
    outfmt="ppm"
    verbose=False
    for i in range(3):
        if (not param or not isinstance(param[0], str)): break
        if(param[0]=='-fmt'):
            outfmt=param[1]
            del param[0:2]
        elif(param[0]=='-b'):
            bpat_up=param[1]
            del param[0:2]
        elif(param[0]=='-v'):
            verbose=True
            del param[0]

    # reading input image
    if isinstance(param[0], pyvips.vimage.Image):
        image = param[0]
    else:
        infilename=param[0]
        if (infilename and infilename != '-'):
            image = pyvips.Image.new_from_file(infilename)
        else:
            source = pyvips.Source.new_from_descriptor(sys.stdin.fileno())
            image = pyvips.Image.new_from_source(source, "")

    if(len(param)>1):
        outfilename = param[1]

    # convert bottom-up bayer pattern into top-down pattern
    bpat_down=bpat_up[2]+bpat_up[3]+bpat_up[0]+bpat_up[1]

    # call external program bayer2rgb for demosaicing
    # create temp files for input/output of bayer2rgb
    tmpdir=os.getenv('AI_TMPDIR')
    if not tmpdir: tmpdir='/tmp'
    tmp_infile = NamedTemporaryFile(dir=tmpdir, prefix="tmp_image.", suffix=".raw", delete=not verbose)
    tmp_infilename = tmp_infile.name
    tmp_outfile = NamedTemporaryFile(dir=tmpdir, prefix="tmp_rgb.", suffix=".tif", delete=not verbose)
    tmp_outfilename = tmp_outfile.name
    # write image array to tmp_infilename
    #v2np(image.cast('ushort')).tofile(tmp_infilename)
    v2np(image.cast('ushort')).tofile(tmp_infilename)
    # bayer2rgb -f $flippat -m $method -b 16 -s -t -w $1 -v $2 -i $tmpraw -o $tmptif
    command = ['bayer2rgb', '-f', bpat_down, '-m', method, '-b 16', '-t',
        '-w', str(image.width), '-v', str(image.height),
        '-i', tmp_infilename, '-o', tmp_outfilename]
    if verbose:
        print('command=', ' '.join(command), file=sys.stderr)
    process = run(command)
    if (process.returncode != 0):
        print('exitcode=', process.returncode, file=sys.stderr)
        if not verbose:
            print('ERROR during command:', ' '.join(command), file=sys.stderr)
        return(process.returncode)
    
    # read in result file from external program call
    outimage = pyvips.Image.new_from_file(tmp_outfilename)

    # writing output image
    writeimage(["-fmt", outfmt, outimage, outfilename])

    # delete temp files
    #tmp_infile.close()
    #tmp_outfile.close()


# smooth image by computing median value within given box size
# usage: immedian [-fmt outfmt] [-b] [-m boxwidth] <inimg> [outimg]
def immedian(param):
    outfilename=""
    outfmt="pgm"
    msize=3
    has_bayer=False
    for i in range(3):
        if (not param or not isinstance(param[0], str)): break
        if(param[0]=='-fmt'):
            outfmt=param[1]
            del param[0:2]
        elif(param[0]=='-m'):
            msize=param[1]
            del param[0:2]
        elif(param[0]=='-b'):
            has_bayer=True
            del param[0]

    # parameters
    if isinstance(param[0], pyvips.vimage.Image):
        image = param[0]
    else:
        image = pyvips.Image.new_from_file(param[0])
    if(len(param)>1):
        outfilename = param[1]

    w = image.width
    h = image.height

    if has_bayer:
        # median in each channel
        p00 = image.subsample(2, 2).median(msize).zoom(2,2)
        p10 = image.embed(-1, 0, w, h).subsample(2, 2).median(msize).zoom(2,2)
        p01 = image.embed(0, -1, w, h).subsample(2, 2).median(msize).zoom(2,2)
        p11 = image.embed(-1, -1, w, h).subsample(2, 2).median(msize).zoom(2,2)

        index = pyvips.Image.new_from_array([[0, 1], [2, 3]]).replicate(w/2, h/2)
        outimg = index.case([p00, p10, p01, p11])
    else:
        outimg = image.median(msize)

    # writing output image
    if (outfilename):
        writeimage(["-fmt", outfmt, outimg, outfilename])
    else:
        return outimg


# clean bad pixels in image according to mask (bilinear interpolation)
# usage: cleanhotpixel [-fmt outfmt] [-b bayerpattern] <image> <badmask> [outimage]
# default: write result to stdout (pgm format)              . . . . ...
# note: bayerpattern describes filter pattern at the        G B G B ...
#   lower left corner (SAOImage ds9), e.g. RGGB is like:    R G R G ...
def cleanhotpixel(param):
    bayerpattern="" # roworder bottom-up
    outfilename=""
    outfmt="pgm"
    method="median"     # if median use median otherwise mean
    neighbors="nearest" # if nearest then l/r/t/b otherwise tl/tr/bl/br
    for i in range(2):
        if (not param or not isinstance(param[0], str)): break
        if(param[0]=='-fmt'):
            outfmt=param[1]
            del param[0:2]
        elif(param[0]=='-b'):
            bayerpattern=param[1]
            del param[0:2]

    if (not param or len(param)<2 or len(param)>3):
        print("ERROR: cleanhotpixel: wrong number of parameters.", file=sys.stderr)
        exit(-1)

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
    if (outfilename):
        writeimage(["-fmt", outfmt, outimg, outfilename])
    else:
        return outimg


# merge 4 monochrome images into bayered image
# syntax: bmerge [-f] top-left top-right bottom-left bottom-right
def bmerge(param):
    outfilename="-"
    outfmt="pgm"
    if(param[0]=='-f'):
        outfmt='fits'
        del param[0]
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
    writeimage(["-fmt", outfmt, outimg, outfilename])


# subtract background image (scaled and downsized)
# syntax: imbgsub [-fmt outfmt] [-bgm bgmult] [-m outmult] [-b outbg] inpnm bgimg outpnm
# processing:
#   - divide bgimg by bgmult and resize to fit inpnm
#   - subtract modified bgimg
#   - multiply by outmult and shift bg to match outbg
def imbgsub(param):
    outfmt='pnm'
    bgmult=0
    outmult=1
    outbg=1000
    for i in range(4):
        if (not param or not isinstance(param[0], str)): break
        if(param[0]=='-fmt'):
            outfmt=param[1]
            del param[0:2]
        elif(param[0]=='-bgm'):
            bgmult=float(param[1])
            del param[0:2]
        elif(param[0]=='-m'):
            outmult=float(param[1])
            del param[0:2]
        elif(param[0]=='-b'):
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
    writeimage(["-fmt", outfmt, outimg, outfilename])


# subtract column- or row-pattern
# syntax: impatsub [-r] [-fmt outfmt] [-m badmask] [-a add] infile [outfile]
def impatsub(param):
    pattern='column'
    outfmt='pnm'
    outadd=0
    maskname=''
    for i in range(4):
        if (not param or not isinstance(param[0], str)): break
        if(param[0]=='-r'):
            pattern='row'
            del param[0]
        elif(param[0]=='-fmt'):
            outfmt=param[1]
            del param[0:2]
        elif(param[0]=='-a'):
            outadd=float(param[1])
            del param[0:2]
        elif(param[0]=='-m'):
            maskname=param[1]
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
    #print("bands=", n, file=sys.stderr)

    # check outfmt
    if ((n==2 or n>3) and outfmt != 'fits'):
        print("ERROR: bands=", n, "is supported only by FITS file output format (use option -f)", file=sys.stderr)
        exit(-1)

    # reading mask of bad pixels
    if (maskname):
        badmask=pyvips.Image.new_from_file(maskname)[0]
        cboard=pyvips.Image.new_from_array([[0, 1], [1, 0]]).replicate(w/2, h/2)

    if (n>10):
        n=10
    for i in range(n):
        imslice=inimg.extract_band(i)
        minval=imslice.min()
        maxval=imslice.max()
        if (maskname):
            tmpimg=(badmask > 0).ifthenelse(cboard*(maxval-minval)+minval, imslice)
        else:
            tmpimg=imslice
        if (pattern == 'column'):
            index=int(w/2)
            patimg=tmpimg.rank(w, 1, index).crop(index, 0, 1, h).replicate(w,1)
        else:
            index=int(h/2)
            patimg=tmpimg.rank(1, h, index).crop(0, index, w, 1).replicate(1,h)
        if (i==0):
            outimg=imslice.subtract(patimg)
        else:
            outimg=outimg.bandjoin(imslice.subtract(patimg))

    if (outadd != 0):
        outimg=outimg.linear(1,outadd)

    # output
    # writing output image
    writeimage(["-fmt", outfmt, outimg, outfilename])


# write image to file or stdout (default: PNM file)
# syntax: writeimage [-v] [-16|-8] [-fmt format] image [outfilename]
# supported output file formats: PBM PGM PPM PNM TIF PNG FITS
def writeimage(param):
    defaultfmt='pnm'
    fmt=None
    depth=None
    strip=None
    filename=False
    verbose=False
    for i in range(4):
        if (not param or not isinstance(param[0], str)): break
        if(param[0]=='-fmt'):
            fmt=param[1].lower()
            del param[0:2]
        elif(param[0]=="-16"):
            depth=16
            del param[0]
        elif(param[0]=='-8'):
            depth=8
            del param[0]
        elif(param[0]=='-v'):
            verbose=True
            del param[0]
    
    if (not param or len(param)>2):
        print("ERROR: writeimage: wrong number of parameters.", file=sys.stderr)
        exit(-1)

    # reading input image
    if isinstance(param[0], pyvips.vimage.Image):
        image = param[0]
    else:
        image = pyvips.Image.new_from_file(param[0])

    # get name of output file
    if(len(param)>1):
        outfilename = param[1]

    # determine output image format
    # TODO: choose from outfilename
    if (not fmt):
        fmt=defaultfmt

    if (fmt == "fit" or fmt == "fts"): fmt="fits"
    if (fmt == "tiff"): fmt="tif"
    if (fmt == "pnm" or fmt == "ppm" or fmt == "pgm" or fmt == "pbm"):
        strip=True
    if (fmt == "fits" or fmt == "tif" or fmt == "png" or fmt == "vips"):
        strip=False
    if (strip == None):
        print("ERROR: unsupported output image file format", file=sys.stderr)
        exit(-1)

    if (pyvips.base.at_least_libvips(8,14)):
        # target format pnm is recognized and chooses the smallest possible
        # output format
        pass
    else:
        if (image.bands == 1):
            if (fmt == "pnm"): fmt="pgm"
        else:
            if (fmt == "pnm"): fmt="ppm"

    # casting to integer image formats
    if (fmt == "pbm" or fmt == "pgm" or fmt == "ppm" or fmt == "pnm" or fmt == "png"):
        if (image.format == "float" or image.format == "double"):
            if (verbose): print("# casting image to ushort", file=sys.stderr)
            image=image.rint().cast('ushort')
    if (depth == 16 and image.format != 'ushort'):
        if (verbose): print("# casting image to ushort", file=sys.stderr)
        image=image.rint().cast('ushort')
    if (depth == 8 and image.format != 'uchar'):
        if (verbose): print("# casting image to uchar", file=sys.stderr)
        image=image.rint().cast('uchar')
    
    # set interpretation (integer formats only)
    if (image.format == "uchar"):
        if (image.bands == 3):
            if (image.interpretation != "rgb"):
                if (verbose): print("# set interpretation to rgb", file=sys.stderr)
                image=image.copy(interpretation="rgb")
        else:
            if (image.interpretation != "b-w"):
                if (verbose): print("# set interpretation to b-w", file=sys.stderr)
                image=image.copy(interpretation="b-w")
    if (image.format == "ushort"):
        if (image.bands == 3):
            if (image.interpretation != "rgb16"):
                if (verbose): print("# set interpretation to rgb16", file=sys.stderr)
                image=image.copy(interpretation="rgb16")
        else:
            if (image.interpretation != "grey16"):
                if (verbose): print("# set interpretation to grey16", file=sys.stderr)
                image=image.copy(interpretation="grey16")

    if (outfilename and outfilename != '-'):
        if (fmt=='fits'):
            image.fitssave(outfilename)
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
                #os.rename(tmpfile.name, outfilename)
                shutil.move(tmpfile.name, outfilename)
            else:
                # output file format is picked from image.bands
                # format is not used
                # file extension is ignored
                target = pyvips.Target.new_to_file(outfilename)
                image.write_to_target(target, "." + fmt, strip=strip)
    else:
        #print("INFO: writing to stdout", file=sys.stderr)
        target = pyvips.Target.new_to_descriptor(sys.stdout.fileno())
        if (fmt=='fits'):
            tmpfile=NamedTemporaryFile(delete=True)
            image.fitssave(tmpfile.name)
            shutil.copy(tmpfile.name, "/dev/stdout")
        elif (fmt=='vips'):
            # TODO: does not work ...
            membuffer=image.write_to_memory()
            os.write(1, membuffer)
        else:
            image.write_to_target(target, "." + fmt, strip=strip)

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
    for i in range(2):
        if(param[0]=='-c'):
            coord=True
            del param[0]
        elif(param[0]=='-0'):
            useminval=True
            del param[0]
        elif(param[0]=='-1'):
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
    #print('format:', inimg.format, ' interpretation:', inimg.interpretation, file=sys.stderr)
    if (inimg.format == 'uchar' or inimg.format == 'char'):
        minval=0
        maxval=2**8-1
        valfmt="%d"
    elif (inimg.format == 'ushort' or inimg.format == 'short'):
        minval=0
        maxval=2**16-1
        valfmt="%d"
    else:
        # set limits according to data range
        minval=inimg.min()
        maxval=inimg.max()
        # TODO: better use double precision or exponential format
        valfmt="%f"
    
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
    if (coord):
        if (inimg.bands == 1):
            np.savetxt(sys.stdout, arr[mask>0, :], ['%d', '%d', valfmt])
        if (inimg.bands == 3):
            np.savetxt(sys.stdout, arr[mask>0, :], ['%d', '%d', valfmt, valfmt, valfmt])
    else:
        np.savetxt(sys.stdout, arr[mask>0, :], valfmt)

# convert ascii file of pixel values (intensities) into image
# syntax: asciitoimage [-f outfmt] [-s] [-8|-16] inascii outimage w h [bands]
def asciitoimage(param):
    outfmt='pnm'
    bands=1
    # BIP - band-interleaved by pixel = RGBRGBRGB... (PPM)
    # BSQ - band-sequential interleave = RRR...GGG...BBB... (FITS)
    is_bandsequential=False
    dtype='float'
    for i in range(3):
        if (param[0]=='-f'):
            outfmt=param[1].lower()
            del param[0:2]
        elif (param[0]=='-s'):
            is_bandsequential=True
            del param[0]
        elif (param[0]=='-8'):
            dtype='uint8'
            del param[0]
        elif (param[0]=='-16'):
            dtype='uint16'
            del param[0]
    inascii=param[0]
    outfilename=param[1]
    width=int(param[2])
    height=int(param[3])
    if (len(param)>4):
        bands=int(param[4])
    
    nparr = np.loadtxt(inascii, dtype=dtype)
    if (bands == 1):
        nparr = nparr.reshape((height,width))
    else:
        if is_bandsequential:
            nparr=nparr.reshape((bands,height,width)).transpose(1,2,0)
        else:
            nparr = nparr.reshape((height,width,bands))
    outimg = pyvips.Image.new_from_array(nparr)

    # output
    # writing output image
    writeimage(["-fmt", outfmt, outimg, outfilename])


#---------------------------------------
#   helper functions for image processing
#---------------------------------------

# map np dtypes to vips
np_dtype_to_vips_format = {
    'uint8': 'uchar',
    'int8': 'char',
    'uint16': 'ushort',
    'int16': 'short',
    'uint32': 'uint',
    'int32': 'int',
    'float32': 'float',
    'float64': 'double',
    'complex64': 'complex',
    'complex128': 'dpcomplex',
}

# map vips formats to np dtypes
vips_format_to_np_dtype = {
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

# convert vips image into numpy array
def v2np(vipsimage):
    return np.ndarray(buffer=vipsimage.write_to_memory(),
        dtype=vips_format_to_np_dtype[vipsimage.format],
        shape=[vipsimage.height, vipsimage.width, vipsimage.bands])
    

if __name__ == "__main__":
    import sys
    if (len(sys.argv)<2 or sys.argv[1]=="-v" or sys.argv[1]=="--version"):
        print(VERSION)
    else:
        globals()[sys.argv[1]](sys.argv[2:])
    exit()
