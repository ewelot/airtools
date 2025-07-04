
import sys
import os
import shutil
import numpy as np
from tempfile import NamedTemporaryFile

import pyvips



# write image to file or stdout (default: PNM file)
# syntax: writeimage [-v] [-32|-16|-8] [-fmt format] image [outfilename]
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
        elif(param[0]=="-32"):
            depth=32
            del param[0]
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
    if (depth == 32 and image.format == 'double'):
        if (verbose): print("# casting image to float", file=sys.stderr)
        image=image.cast('float')
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


# list pixels in equally spaced, quadratic background regions
# usage: bgpixels [-s bsize] image
def bgpixels(param):
    nx=4
    ny=3
    size=20
    for i in range(3):
        if(param[0]=='-s'):
            size=int(param[1])
            del param[0:2]
    infilename = param[0]
    
    # reading input images
    if (infilename and infilename != '-'):
        inimg = pyvips.Image.new_from_file(infilename)
    else:
        source = pyvips.Source.new_from_descriptor(sys.stdin.fileno())
        inimg = pyvips.Image.new_from_source(source, "")
    
    # get some image properties
    w=inimg.width
    h=inimg.height
    if (inimg.format == 'uchar' or inimg.format == 'char'):
        valfmt="%d"
    elif (inimg.format == 'ushort' or inimg.format == 'short'):
        valfmt="%d"
    else:
        valfmt="%f"

    # list pixels
    for j in range(ny):
        y0=(0.2+0.6*j/(ny-1))*h - size/2
        for i in range(nx):
            x0=(0.2+0.6*i/(nx-1))*w - size/2
            area = inimg.crop(x0, y0, size, size)
            arr=v2np(area).reshape(area.width*area.height, area.bands)
            idx=(1+i+j*nx)*np.ones((size*size,1))
            np.savetxt(sys.stdout, np.hstack((idx,arr)), valfmt)


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


# get statistics on image region defined by mask (svg image)
# syntax: regstat [-m] [-g] image mask badmask
def regstat(param):
    mode=''
    greenonly=False
    if(param[0]=='-m'):
        mode='minmax'
        del param[0]
    if(param[0]=='-g'):
        greenonly=True
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
    if (greenonly and ncol == 3):
        xximg=inimg[1]
        inimg=xximg
        ncol=1
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


def bgnoise(inimg):
    # determine bg noise by evaluating 9 subimages
    # note: only green channel is used if image is RGB
    bsize=30
    if isinstance(inimg, pyvips.vimage.Image):
        pass
    else:
        inimg = pyvips.Image.new_from_file(inimg)

    # in case of RGB image extract green channel only
    if (inimg.bands == 3):
        inimg = inimg[1]

    w = inimg.width
    h = inimg.height
    sd=[]
    for xc in np.round(np.linspace(0.2*w, 0.8*w, 4)):
        for xc in np.round(np.linspace(0.2*h, 0.8*h, 3)):
            data=v2np(inimg.crop(xc-bsize/2, xc-bsize/2, bsize, bsize)).reshape(bsize*bsize)
            for it in range(3):
                mn=np.median(data)
                data=data[data<mn+3*np.std(data)]
            sd.append(np.std(data))
    sd=np.array(sd)
    #print('{:.1f}'.format(np.quantile(sd, 0.3)))
    return np.quantile(sd, 0.3)


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

# convert vips image to numpy array
def v2np(vipsimage):
    if (vipsimage.bands == 1):
        shape=[vipsimage.height, vipsimage.width]
    else:
        shape=[vipsimage.height, vipsimage.width, vipsimage.bands]
    return np.ndarray(buffer=vipsimage.write_to_memory(),
        dtype=vips_format_to_np_dtype[vipsimage.format],
        shape=shape)
    
# convert numpy array to vips image
def np2v(array):
    return pyvips.Image.new_from_array(array)
        #, array.shape[1], array.shape[0], 1,
        #np_dtype_to_vips_format[array.dtype])
