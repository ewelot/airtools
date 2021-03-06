#!/usr/bin/python3

# Version 1.0
# Changelog ...

import sys
import math
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
    if (len(param) < 3):
        print("usage: mkephem cephem start end [g] [k] [num]")
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

    # convert start and end from yyyymmdd to JD
    if (start > 10000000 and start < 30000000): start=ymd2jd(start)
    if (end   > 10000000 and end   < 30000000): end=ymd2jd(end)
    # convert start and end from unix time to JD
    if (start > 30000000): start=2440587.5+start/86400.0
    if (end   > 30000000): end=2440587.5+end/86400.0
    
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

# convert FITS cube to PPM (stdout)
def fitscubetoppm(param):
    infits = param[0]
    outpnm = param[1]

    # reading input image
    if (infits and infits != '-'):
        inimg = pyvips.Image.new_from_file(infits)
    else:
        source = pyvips.Source.new_from_descriptor(sys.stdin.fileno())
        inimg = pyvips.Image.new_from_source(source, "")

    inimg.copy(interpretation="rgb16").ppmsave(outpnm, strip=1)
    exit()

# crop an image
# imcrop [-f] inimg outimg w h xoff yoff
def imcrop(param):
    outfmt='ppm'
    outstrip=True
    if(param[0]=='-f'):
        outfmt='fits'
        outstrip=False
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
    if (outfile and outfile != '-'):
        if (outfmt=='fits'):
            outimg.fitssave(outfile)
        else:
            outimg.ppmsave(outfile, strip=1)
    else:
        target = pyvips.Target.new_to_descriptor(sys.stdout.fileno())
        outimg.write_to_target(target, "." + outfmt, strip=outstrip)
    exit()


# image statistics (per channel output: min max median (stddev))
# imstat -m "$fname"
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

# basic CCD image reduction: outpnm = mult * (inpnm-dark)/flat + add
#   note about sequence of operations
#   - add preadd
#   - multiply premult
#   - flip imahe (top-bottom)
#   - rotate image (180 degrees)
#   - subtract dark image
#   - divide by flat image
#   - multiply by mult (array for different bands)
#   - add offset value add (array for different bands)
#   - optionally convert from rgb to gray
# syntax: pnmccdred [-f] [-g] [-preadd val] [-premult val] [-tb] [-r180] inpnm outpnm dark flat mult add
def pnmccdred(param):
    outfmt='ppm'
    outstrip=True
    outgray=False
    preadd=0
    premult=1
    flip=False
    rot=False
    if(param[0]=='-f'):
        outfmt='fits'
        outstrip=False
        del param[0]
    if(param[0]=='-g'):
        outgray=True
        del param[0]
    if(param[0]=='-preadd'):
        preadd=float(param[1])
        del param[0:2]
    if(param[0]=='-premult'):
        premult=float(param[1])
        del param[0:2]
    if(param[0]=='-tb'):
        flip=True
        del param[0]
    if(param[0]=='-r180'):
        rot=True
        del param[0]
    infilename = param[0]
    outfilename = param[1]
    np = len(param)
    if (np > 2): dark = param[2]
    if (np > 3): flat = param[3]
    if (np > 4): mult = param[4]
    if (np > 5): add = param[5]
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
    if rot:
        code += """.rotate(180)"""
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
    # workaround for fitssave which otherwise creates FITS cube
    # HAS NO EFFECT!
    #if (inimg.bands == 1 and outfmt == 'fits'):
    #    code += """.bandmean().copy(interpretation='grey16')"""
    outimg = eval(code)
    

    # writing output image
    if (outfilename and outfilename != '-'):
        if (outfmt=='fits'):
            outimg.fitssave(outfilename)
        else:
            outimg.ppmsave(outfilename, strip=1)
    else:
        target = pyvips.Target.new_to_descriptor(sys.stdout.fileno())
        outimg.write_to_target(target, "." + outfmt, strip=outstrip)

    exit()

#ppmtogray $ppm $tmp1 $1,$2,$3
# convert from PPM to PGM using user supplied channel multipliers
# syntax: ppmtogray -f inppm outpgm [multR,multG,multB]
def ppmtogray(param):
    outfmt='ppm'
    outstrip=True
    if(param[0]=='-f'):
        outfmt='fits'
        outstrip=False
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
    if (outfilename and outfilename != '-'):
        if (outfmt=='fits'):
            outimg.fitssave(outfilename)
        else:
            outimg.ppmsave(outfilename, strip=1)
    else:
        target = pyvips.Target.new_to_descriptor(sys.stdout.fileno())
        outimg.write_to_target(target, "." + outfmt, strip=outstrip)
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
    
    ramp = pyvips.Image.new_from_array(range(histimg2.width))
    # mean value for each band: sum(hist*ramp)/area
    statsimg = histimg2.multiply(ramp).stats()
    mean = [statsimg.getpoint(2, i+1)[0]/incnt for i in range(ncol)]
    # determine max value for each band
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
    mode='mean'
    outfmt='ppm'
    outstrip=True
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
    if (outfilename and outfilename != '-'):
        if (outfmt=='fits'):
            outimg.fitssave(outfilename)
        else:
            outimg.ppmsave(outfilename, strip=1)
    else:
        target = pyvips.Target.new_to_descriptor(sys.stdout.fileno())
        outimg.write_to_target(target, "." + outfmt, strip=outstrip)
    exit()

# clean bad pixels according to mask
# usage: cleanbadpixel <image> <badmask> [outimage]
# default: write result to stdout (pgm format)
def cleanbadpixel(param):
    outfilename="-"
    outfmt="ppm"
    outstrip=True
    infilename = param[0]
    maskfilename = param[1]
    if(len(param)>2):
        outfilename = param[2]

    image = pyvips.Image.new_from_file(infilename)
    badmask = pyvips.Image.new_from_file(maskfilename)

    w = image.width
    h = image.height
    p00 = image.subsample(2, 2).median(3).zoom(2,2)
    p10 = image.embed(-1, 0, w, h).subsample(2, 2).median(3).zoom(2,2)
    p01 = image.embed(0, -1, w, h).subsample(2, 2).median(3).zoom(2,2)
    p11 = image.embed(-1, -1, w, h).subsample(2, 2).median(3).zoom(2,2)

    index = pyvips.Image.new_from_array([[0, 1], [2, 3]]).replicate(w/2, h/2)
    median = index.case([p00, p10, p01, p11])

    outimg = (badmask > 0).ifthenelse(median, image)
    # writing output image
    if (outfilename and outfilename != '-'):
        if (outfmt=='fits'):
            outimg.fitssave(outfilename)
        else:
            outimg.ppmsave(outfilename, strip=1)
    else:
        target = pyvips.Target.new_to_descriptor(sys.stdout.fileno())
        outimg.write_to_target(target, "." + outfmt, strip=outstrip)
    exit()

# subtract background image (scaled and downsized)
# syntax: imbgsub [-f] [-bgm bgmult] [-m outmult] [-b outbg] inpnm bgimg outpnm
# processing:
#   - divide bgimg by bgmult and resize to fit inpnm
#   - subtract modified bgimg
#   - multiply by outmult and shift bg to match outbg
def imbgsub(param):
    outfmt='ppm'
    outstrip=True
    bgmult=0
    outmult=1
    outbg=1000
    if(param[0]=='-f'):
        outfmt='fits'
        outstrip=False
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
    if (outfilename and outfilename != '-'):
        if (outfmt=='fits'):
            outimg.fitssave(outfilename)
        else:
            outimg.ppmsave(outfilename, strip=1)
    else:
        target = pyvips.Target.new_to_descriptor(sys.stdout.fileno())
        outimg.write_to_target(target, "." + outfmt, strip=outstrip)

    exit()





if __name__ == "__main__":
    import sys
    globals()[sys.argv[1]](sys.argv[2:])
