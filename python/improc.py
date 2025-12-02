
#---------------------------------------
#   functions for image processing
#---------------------------------------

import sys
import os
import math
import re
import numpy as np

import rawpy
import pyvips
from photutils.background import Background2D, SExtractorBackground

from imutils import writeimage, v2np, np2v, np_dtype_to_vips_format
from debayer import debayer


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
# imcrop [-f] [-b] inimg outimg w h xoff yoff
def imcrop(param):
    outfmt='pnm'
    addborder=False
    for i in range(3):
        if (not param or not isinstance(param[0], str)): break
        if(param[0]=='-f'):
            outfmt='fits'
            del param[0]
        if(param[0]=='-b'):
            addborder=True
            del param[0]
    infile = param[0]
    outfile = param[1]
    width = int(param[2])
    height = int(param[3])
    xoff = int(param[4])
    yoff = int(param[5])

    # reading input image
    if (infile and infile != '-'):
        inimg = pyvips.Image.new_from_file(infile)
    else:
        source = pyvips.Source.new_from_descriptor(sys.stdin.fileno())
        inimg = pyvips.Image.new_from_source(source, "")

    b=0
    if addborder:
        d=0-xoff
        if (d>b): b=d
        d=0-yoff
        if (d>b): b=d
        d=xoff+width-inimg.width
        if (d>b): b=d
        d=yoff+height-inimg.height
        if (d>b): b=d
        #print("b={:d}".format(b), file=sys.stderr)
        
    try:
        if addborder:
            w=inimg.width+2*b
            h=inimg.height+2*b
            outimg=inimg.embed(b,b,w,h,extend='copy').crop(xoff+b, yoff+b, width, height)
        else:
            outimg=inimg.crop(xoff, yoff, width, height)
    except Exception as e:
        print(f"An unexpected error occurred: {e}", file=sys.stderr)
        print("ERROR: unable to crop at x,y {:d},{:d} w,h {:d},{:d}".format(xoff, yoff, width, height), file=sys.stderr)
        exit(-1)
    
    # writing output image
    writeimage(["-fmt", outfmt, outimg, outfile])

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


# basic CCD image reduction: outpnm = mult * (inpnm-dark)/flat + add
#   note about sequence of operations
#   - add preadd
#   - multiply premult
#   - flip image (top-bottom)
#   - rotate image (180 degrees)
#   - subtract dark image
#   - divide by flat image
#   - crop image
#   - post rotate (180 degrees)
#   - multiply by mult (array for different bands)
#   - add offset value add (array for different bands)
#   - convert from rgb to gray
#   - interpolate bad pixels
#   - debayer image
# syntax: pnmccdred [-v] [-fmt outfmt|pnm] [-8|-16] [-gray] [-preadd val] [-premult val] [-flip] [-prerot]
#   [-bpat bayerpattern] [-debayer mode] [-cgeom wxh+x+y ] [-resize wxh|mult] [-rot] [-mult mult] [-add add] inpnm outpnm <dark> <flat> <bad>
def pnmccdred(param):
    outfmt='pnm'
    outgray=False
    preadd=0
    premult=1
    bayerpattern="" # CFA pattern of input image as displayed by SAOImage, row-order is top-down
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
            raw = rawpy.imread(infilename)
            # stretch to 16bit
            premult=premult * int(2**16 / raw.white_level)
            cfa = raw.raw_image_visible.copy()
            if (not bayerpattern):
                for ind in raw.raw_pattern.flatten():
                    bayerpattern += "RGBG"[ind]
            if verbose:
                print("# raw DSLR image loaded by rawpy", file=sys.stderr)
                print("# bayer pattern:", bayerpattern, file=sys.stderr)

            # convert to vips image   
            height, width = cfa.shape
            bands=1
            nparr = cfa.reshape(width * height)
            inimg = pyvips.Image.new_from_memory(nparr.data, width, height, bands,
                np_dtype_to_vips_format[str(cfa.dtype)])
            # TODO: check for possible scaling to 16bit in which case we must adjust mult
        except:
            try:
                inimg = pyvips.Image.new_from_file(infilename)
                if verbose:
                    print("# image loaded by libvips", file=sys.stderr)
            except:
                print("ERROR: unsupported input image format.", file=sys.stderr)
                exit(-1)
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
        if bayerpattern: bayerpattern=bayerpattern[2:4]+bayerpattern[0:2]
    if prerot:
        code += """.rot180()"""
        if bayerpattern: bayerpattern=bayerpattern[::-1]
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
            else:
                cleanhotpixel(["-fmt", outfmt, "-b", bayerpattern, tmpimg, bad, outfilename])
        else:
            cleanhotpixel(["-fmt", outfmt, tmpimg, bad, outfilename])
    else:
        if (bayerpattern and debayer_mode):
            tmpimg = eval(code)
            debayer([debayer_mode, "-fmt", outfmt, "-b", bayerpattern, tmpimg, outfilename])
        else:
            outimg = eval(code)
            wopts.append(outimg)
            wopts.append(outfilename)
            writeimage(wopts)


# convert from (noisy) RGB image to color image by using LRGB techniques
# syntax: lrgb [-f|-t] [-16] [-m metric] [-s sigma] inppm outppm bgR,bgG,bgB rmsg
def lrgb(param):
    outfmt='ppm'
    metric="Lch"    # Lch (best), Lab (ugly), HSV (not working), RGB
    sigma=2
    depth=8
    bg=0
    while (param[0][0:1] == "-"):
        if(param[0]=='-m'):
            metric=param[1]
            del param[0:2]
        if(param[0]=='-s'):
            sigma=float(param[1])
            del param[0:2]
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

    # color smoothing
    if (metric == "Lch"):
        #print(inimg.interpretation)
        l,c,h = inimg.subtract(bg).colourspace("lch").bandsplit()
        #l = l.gaussblur(0.4)
        #c = c.linear(0.9,0)
        h = h.gaussblur(sigma).linear(1.0,0)
        if (depth == 16):
            outimg = l.bandjoin([c,h]).colourspace("rgb16").linear(1,bg)
        else:
            outimg = l.bandjoin([c,h]).colourspace("srgb").linear(1,bg)
    if (metric == "Lab"):
        #print(inimg.interpretation)
        l,a,b = inimg.subtract(bg).colourspace("lab").bandsplit()
        #l = l.gaussblur(0.4)
        a = a.gaussblur(sigma).linear(1.0,0)
        b = b.gaussblur(sigma).linear(1.0,0)
        if (depth == 16):
            outimg = l.bandjoin([a,b]).colourspace("rgb16").linear(1,bg)
        else:
            outimg = l.bandjoin([a,b]).colourspace("srgb").linear(1,bg)
    if (metric == "HSV"):
        h,s,v = inimg.subtract(bg).colourspace("hsv").bandsplit()
        #v = v.gaussblur(0.4)
        h = h.gaussblur(sigma).linear(1.0,0)
        #s = s.gaussblur(sigma).linear(1.0,0)
        if (depth == 16):
            outimg = h.bandjoin([s,v]).colourspace("rgb16").linear(1,bg)
        else:
            outimg = h.bandjoin([s,v]).colourspace("srgb").linear(1,bg)
    if (metric == "RGB"):
        #print(inimg.interpretation)
        l,x,y = inimg.subtract(bg).colourspace("lch").bandsplit()
        x,c,h = inimg.subtract(bg).gaussblur(sigma).colourspace("lch").bandsplit()
        #l = l.gaussblur(0.4)
        if (depth == 16):
            outimg = l.bandjoin([c,h]).colourspace("rgb16").linear(1,bg)
        else:
            outimg = l.bandjoin([c,h]).colourspace("srgb").linear(1,bg)
  
    # writing output image
    writeimage(["-fmt", outfmt, outimg, outfilename])


# apply badmask to image 
def immask(param):
    outfmt='pnm'
    do_invert=False     # invert mask
    outfilename=""
    for i in range(1):
        if(param[0]=='-fmt'):
            outfmt=param[1]
            del param[0:2]
        if(param[0]=='-i'):
            do_invert=True
            del param[0]
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
    
    if (do_invert):
        outimg=(maskimg > 0).ifthenelse(inimg, 0)
    else:
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
    for i in range(4):
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


def pnmcombine(param):
    mode='mean' # min, max, mean, median, stddev
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
    elif mode=="min":
        outimg = inimgarray[0].bandrank(inimgarray[1:], index=0)
    elif mode=="max":
        nimg = len(inimgarray)
        outimg = inimgarray[0].bandrank(inimgarray[1:], index=nimg-1)
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


# smooth image by computing median value within given box size
# usage: immedian [-fmt outfmt] [-b] [-m boxwidth] <inimg> [outimg]
def immedian(param):
    outfilename=""
    outfmt="pnm"
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


# smooth image by gaussian blur
# TODO: optionally scale down image before bluring and scale up afterwards
# usage: imblur [-fmt outfmt] [-b blur] [-s scale] <inimg> [outimg]
def imblur(param):
    outfilename=""
    outfmt="pnm"
    blur=1  # sigma in gaussian
    scale=1
    for i in range(3):
        if (not param or not isinstance(param[0], str)): break
        if(param[0]=='-fmt'):
            outfmt=param[1]
            del param[0:2]
        elif(param[0]=='-s'):
            scale=int(param[1])
            del param[0:2]
        elif(param[0]=='-b'):
            blur=float(param[1])
            del param[0:2]

    # parameters
    if isinstance(param[0], pyvips.vimage.Image):
        image = param[0]
    else:
        image = pyvips.Image.new_from_file(param[0])
    if(len(param)>1):
        outfilename = param[1]

    w = image.width
    h = image.height

    if (scale == 1):
        outimg = image.gaussblur(blur)
    else:
        outimg = image.gaussblur(blur)

    # writing output image
    if (outfilename):
        writeimage(["-fmt", outfmt, outimg, outfilename])
    else:
        return outimg


# resize image by given scale factor
# TODO: allow scaling to a predefined output size
# usage: imscale [-fmt outfmt] [-n | -l] [-s scale] <inimg> [outimg]
def imresize(param):
    outfilename=""
    outfmt="pnm"
    kernel="VIPS_KERNEL_CUBIC"
    scale=1
    for i in range(4):
        if (not param or not isinstance(param[0], str)): break
        if(param[0]=='-fmt'):
            outfmt=param[1]
            del param[0:2]
        elif(param[0]=='-n'):
            kernel='VIPS_KERNEL_NEAREST'
            del param[0]
        elif(param[0]=='-l'):
            kernel='VIPS_KERNEL_LANCZOS3'
            del param[0]
        elif(param[0]=='-s'):
            scale=float(param[1])
            del param[0:2]

    # parameters
    if isinstance(param[0], pyvips.vimage.Image):
        image = param[0]
    else:
        image = pyvips.Image.new_from_file(param[0])
    if(len(param)>1):
        outfilename = param[1]

    w = image.width
    h = image.height

    outimg = image.resize(scale, kernel=kernel)

    # writing output image
    if (outfilename):
        writeimage(["-fmt", outfmt, outimg, outfilename])
    else:
        return outimg


# dynamic compression (above a given threshold)
# usage: imcompress [-fmt outfmt] [-m mode] <image> <threshold> <compmult> [outimage]
def imcompress(param):
    outfilename=""
    outfmt="pnm"
    mode="simple" # available modes: simple, tanh, sqrt, lut
    for i in range(2):
        if (not param or not isinstance(param[0], str)): break
        if(param[0]=='-fmt'):
            outfmt=param[1]
            del param[0:2]
        elif(param[0]=='-m'):
            mode=param[1]
            del param[0:2]
 
    if(len(param)<3):
        print("ERROR: imcompress: wrong number of parameters.", file=sys.stderr)
        exit(-1)
        
    # parameters
    infilename=param[0]
    threshold=float(param[1])
    compmult=float(param[2])    # only used by mode=sqrt
    if(len(param)>3):
        outfilename = param[3]
    
    # read input image
    if isinstance(infilename, pyvips.vimage.Image):
        image = infilename
    else:
        image = pyvips.Image.new_from_file(infilename)
    
    if (mode == "sqrt"):
        # create contour-like mask of pixels having intensity > threshold
        # note: operating on all bands of RGB image 
        for i in range(image.bands):
            if (i==0):
                mask=(image.extract_band(i) > threshold).ifthenelse(1,0)
            else:
                mask=(image.extract_band(i) > threshold).ifthenelse(1,mask)
        morphmask = pyvips.Image.mask_ideal(3, 3, 0, optical=1, uchar=1)
        large = mask.morph(morphmask, "VIPS_OPERATION_MORPHOLOGY_DILATE")
        small = mask.morph(morphmask, "VIPS_OPERATION_MORPHOLOGY_ERODE")
        statsmask = large.subtract(small)
        writeimage(["-fmt", "pnm", statsmask, "x.statsmask.pgm"])

        # bandwise thresholding by mean value within statsmask
        npix=(statsmask > 0).ifthenelse(1,0).stats().getpoint(2, 0)[0]
        print("npix=", npix, file=sys.stderr)

    # apply compression above mean
    for i in range(image.bands):
        imband=image.extract_band(i)
        if (mode == "simple"):
            mean=threshold
            # new = x/(1+x/t)
            t=10000
            x = imband.linear(1, -1*mean)
            y = x.linear(1/t,1)
            add=(1-compmult)*mean
            imcomp=(imband > mean).ifthenelse(x.divide(y).linear(1,mean), imband).linear(compmult, add)
        if (mode == "tanh"):
            mean=threshold
            # new = x/sqrt(1+(x/t)^2)
            t=10000
            x = imband.linear(1, -1*mean)
            y = x.linear(1/t,0).math2_const("pow", 2).linear(1, 1)
            imcomp=(imband > mean).ifthenelse(x.divide(y.math2_const("pow", 0.5)).linear(1,mean), imband)
        if (mode == "sqrt"):
            mean=(statsmask > 0).ifthenelse(imband, 0).stats().getpoint(2, 0)[0]/npix
            print(i, " mean=", mean, file=sys.stderr)
            add=(1-compmult)*mean
            #imcomp=(imband > mean).ifthenelse(imband.linear(compmult, add), imband)
            imcomp=(imband > mean).ifthenelse(imband.linear(1, -1*mean).math2_const("pow", compmult).linear(1,mean), imband)
        if (mode == "lut"):
            mean=threshold
            mean=0
            x = imband.linear(1, -1*mean)
            s=5    # shadow adjustment
            m=20   # mid-tone adjustment
            h=10   # high-lights adjustment
            lut=pyvips.Image.tonelut(in_max=65535, out_max=10000, Lb=0, \
                Ps=0.1, Pm=0.5, Ph=0.8, S=s, M=m, H=h)
            imcomp=(imband > mean).ifthenelse(imband.linear(1, -1*mean).maplut(lut).linear(1,mean), imband)

        if (i==0):
            outimg = imcomp
        else:
            outimg = outimg.bandjoin(imcomp)
            
    # writing output image
    if (outfilename):
        writeimage(["-fmt", outfmt, outimg, outfilename])
    else:
        return outimg


# clean bad pixels in image according to mask (bilinear interpolation)
# usage: cleanhotpixel [-fmt outfmt] [-b bayerpattern] <image> <badmask> [outimage]
# default: write result to stdout (pgm format)
# note: bayerpattern describes filter pattern at the top left corner (as viewed
#   by SAOImage ds9), e.g. RGGB is like:
#   R G R G ...
#   G B G B ...
#   . . . . ...
def cleanhotpixel(param):
    bayerpattern="" # row-order: top-down
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
        if (bayerpattern[0:1] == "G"):
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
    for i in range(2):
        if (not param or not isinstance(param[0], str)): break
        if(param[0]=='-f'):
            outfmt='fits'
            del param[0]
    infilename00 = param[0]
    infilename10 = param[1]
    infilename01 = param[2]
    infilename11 = param[3]
    if(len(param)>4):
        outfilename = param[4]

    if isinstance(infilename00, pyvips.vimage.Image):
        p00 = infilename00.zoom(2,2)
    else:
        p00 = pyvips.Image.new_from_file(infilename00).zoom(2,2)
    if isinstance(infilename10, pyvips.vimage.Image):
        p10 = infilename10.zoom(2,2)
    else:
        p10 = pyvips.Image.new_from_file(infilename10).zoom(2,2)
    if isinstance(infilename01, pyvips.vimage.Image):
        p01 = infilename01.zoom(2,2)
    else:
        p01 = pyvips.Image.new_from_file(infilename01).zoom(2,2)
    if isinstance(infilename11, pyvips.vimage.Image):
        p11 = infilename11.zoom(2,2)
    else:
        p11 = pyvips.Image.new_from_file(infilename11).zoom(2,2)
    w = p00.width
    h = p00.height

    index = pyvips.Image.new_from_array([[0, 1], [2, 3]]).replicate(w/2, h/2)
    outimg = index.case([p00, p10, p01, p11])

    # writing output image
    writeimage(["-fmt", outfmt, outimg, outfilename])


# create thumbnail bg map of an image by "averaging" bsize x bsize pixels
# optionally subtracting a reference image first
# syntax bgmap [-fmt outfmt] [-b bsize] [-r refimg] [-a add] <inimage> [outimage]
def bgmap(param):
    outfmt='pnm'
    bsize=128
    refimgname=None
    outfilename="-"
    add=0
    sizediv=2
    for i in range(5):
        if (not param or not isinstance(param[0], str)): break
        if(param[0]=='-fmt'):
            outfmt=param[1]
            del param[0:2]
        elif(param[0]=='-a'):
            add = tuple(float(val) for val in tuple(param[1].split(",")))
            del param[0:2]
        elif(param[0]=='-b'):
            bsize=int(param[1])
            del param[0:2]
        elif(param[0]=='-r'):
            refimgname=param[1]
            del param[0:2]
    infilename = param[0]
    if (len(param) > 1):
        outfilename = param[1]

    # reading input images
    if (infilename and infilename != '-'):
        inimg = pyvips.Image.new_from_file(infilename)
    else:
        source = pyvips.Source.new_from_descriptor(sys.stdin.fileno())
        inimg = pyvips.Image.new_from_source(source, "")
    if (refimgname):
        refimg = pyvips.Image.new_from_file(refimgname)

    # subsample images to lower processing time
    megapix = inimg.width * inimg.height / 1024. /1024.
    if (megapix > 8):
        inimg = inimg.subsample(2,2)
        bsize = int(bsize/2)
        if (refimgname):
            refimg = refimg.subsample(2,2)

    # image data (numpy array)
    if (refimgname):
        tmpimg=inimg.subtract(refimg).linear(1, add)
    else:
        tmpimg=inimg.linear(1, add)
    
    # create background image (bandwise)
    # sortimg=np2v(np.sort(v2np(tmpimg), axis=1))
    for i in range(inimg.bands):
        data=v2np(tmpimg[i]).reshape(tmpimg.height, tmpimg.width)
        bg = Background2D(data, (bsize, bsize), filter_size=(1, 1),
            bkg_estimator=SExtractorBackground())
        bgimg = np2v(bg.background_mesh)
        if (i==0):
            outimg = bgimg
        else:
            outimg = outimg.bandjoin(bgimg)

    # data casting
    if (outfmt == 'fits'):
        outimg=outimg.cast('float')
    else:
        outimg=outimg.rint().cast('ushort')

    # writing output image
    writeimage(["-fmt", outfmt, outimg, outfilename])


# subtract background image (scaled and downsized)
# syntax: imbgsub [-fmt outfmt] [-s] [-bgm bgmult] [-m outmult] [-b outbg] inimg bgimg outpnm
# processing:
#   - divide bgimg by bgmult and resize to fit inimg
#   - subtract modified bgimg
#   - multiply by outmult and add outbg
#   - optionally slice output image, adding slice number (band index+1) to output file name
def imbgsub(param):
    outfmt='pnm'
    bgmult=1
    outmult=1
    outbg=1000
    do_adjust_bg=False
    do_slice=False
    for i in range(5):
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
        elif(param[0]=='-s'):
            do_slice=True
            del param[0]
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
    cflag=False
    if False:
        if (xscale > 15 and yscale > 15):
            xscale, yscale = xscale/9, yscale/9
            bgimg2=bgimg.linear(1/bgmult, 0).resize(3, centre=cflag)
            bgimg2=bgimg2.resize(3, centre=cflag)
            bgimg2=bgimg2.resize(xscale, vscale=yscale, centre=cflag)
        elif (xscale > 5 and yscale > 5):
            xscale, yscale = xscale/3, yscale/3
            bgimg2=bgimg.linear(1/bgmult, 0).resize(3, centre=cflag)
            bgimg2=bgimg2.resize(xscale, vscale=yscale, centre=cflag)
        else:
            bgimg2=bgimg.linear(1/bgmult, 0).resize(xscale, vscale=yscale, centre=cflag)
    else:
        bgimg2=bgimg.linear(1/bgmult, 0).resize(xscale, vscale=yscale, centre=cflag)

    if do_adjust_bg:
        # adjust level of bgim2 to match that of inimg
        inmedian = np.zeros(inimg.bands)
        cw, ch = int(inimg.width/2), int(inimg.height/2)
        tmpim = inimg.crop(int(cw/2), int(ch/2), cw, ch)
        for i in range(inimg.bands):
            inmedian[i]=np.median(v2np(tmpim[i]))
        #print(inmedian, file=sys.stderr)
        
        bgmedian = 0 * inmedian
        tmpim = bgimg2.crop(int(cw/2), int(ch/2), cw, ch)
        for i in range(inimg.bands):
            bgmedian[i]=np.median(v2np(tmpim[i]))
        #print(bgmedian, file=sys.stderr)
        bgimg2 = bgimg2.linear(1, list(inmedian-bgmedian))
    
    # subtract bgimg2
    if (outfmt == 'fits'):
        outimg=inimg.subtract(bgimg2).linear(outmult, outbg).cast('float')
    else:
        outimg=inimg.subtract(bgimg2).linear(outmult, outbg).rint().cast('ushort')

    # output
    # writing output image(s)
    if do_slice:
        outbase, outext = os.path.splitext(outfilename)
        if (outimg.bands == 1):
            writeimage(["-fmt", outfmt, outimg[0], outbase + ".gray" + outext])
        if (outimg.bands == 3):
            writeimage(["-fmt", outfmt, outimg[0], outbase + ".red" + outext])
            writeimage(["-fmt", outfmt, outimg[1], outbase + ".grn" + outext])
            writeimage(["-fmt", outfmt, outimg[2], outbase + ".blu" + outext])
    else:
        writeimage(["-fmt", outfmt, outimg, outfilename])


# subtract column- or row-pattern
# syntax: impatsub [-r] [-fmt outfmt] [-m badmask] [-a add] [-b gaussblur] infile [outfile]
def impatsub(param):
    pattern='column'
    outfmt='pnm'
    outadd=0
    sigma=0.01
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
        elif(param[0]=='-b'):
            sigma=float(param[1])
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
            sortimg=np2v(np.sort(v2np(tmpimg), axis=1))
            patimg=sortimg.gaussblur(sigma).crop(index, 0, 1, h).replicate(w,1)
        else:
            index=int(h/2)
            sortimg=np2v(np.sort(v2np(tmpimg), axis=0))
            patimg=sortimg.gaussblur(sigma).crop(0, index, w, 1).replicate(1,h)
        if (i==0):
            outimg=imslice.subtract(patimg)
            #writeimage(["-fmt", outfmt, tmpimg, "x.check.pgm"])
            #writeimage(["-fmt", outfmt, sortimg, "x.sorted.pgm"])
        else:
            outimg=outimg.bandjoin(imslice.subtract(patimg))

    if (outadd != 0):
        outimg=outimg.linear(1,outadd)

    # output
    # writing output image
    writeimage(["-fmt", outfmt, outimg, outfilename])


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
