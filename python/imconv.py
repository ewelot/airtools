
import sys
import numpy as np

import pyvips

from imutils import writeimage


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
    rgb = r.bandjoin([g, b])
    writeimage(["-fmt", "ppm", rgb, outppm])
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

    outimg = inimg.linear(mult,add)
    writeimage(["-fmt", "pnm", outimg, outpnm])
    exit()


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
