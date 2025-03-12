
import sys
import os
import numpy as np
from subprocess import run
from tempfile import NamedTemporaryFile

import pyvips

from imutils import writeimage, v2np

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
    elif (algorithm == 'halfsize'):
        debayer_halfsize(param)
    elif (algorithm == 'green'):
        debayer_green(param)
    elif (algorithm == 'greencopy'):
        debayer_greencopy(param)
    elif (algorithm == 'greensubsample'):
        debayer_greensubsample(param)
    else:
        debayer_simple(param)


# debayer (demosaic) using simple bilinear interpolation
# usage: debayer_simple [-fmt outfmt] [-v] [-b bayerpattern] <image> [outimage]
def debayer_simple(param):
    bpat="RGGB"     # row-order: top down
    outfilename="-"
    outfmt="ppm"
    verbose=False
    for i in range(2):
        if (not param or not isinstance(param[0], str)): break
        if(param[0]=='-fmt'):
            outfmt=param[1]
            del param[0:2]
        elif(param[0]=='-b'):
            bpat=param[1]
            del param[0:2]
        elif(param[0]=='-v'):
            verbose=True
            del param[0]
    if verbose:
        print("# debayer_simple using bpat =", bpat, file=sys.stdout)

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


    # mask for green/red/blue pixels
    w = image.width
    h = image.height
    if (bpat[1:2] == "G"):  # e.g. RGGB
        gmask = pyvips.Image.new_from_array([[0, 1], [1, 0]]).replicate(w/2, h/2)
        if (bpat[0] == "R"):
            rmask = pyvips.Image.new_from_array([[1, 0], [0, 0]]).replicate(w/2, h/2)
            bmask = pyvips.Image.new_from_array([[0, 0], [0, 1]]).replicate(w/2, h/2)
        else:
            rmask = pyvips.Image.new_from_array([[0, 0], [0, 1]]).replicate(w/2, h/2)
            bmask = pyvips.Image.new_from_array([[1, 0], [0, 0]]).replicate(w/2, h/2)
    else:
        gmask = pyvips.Image.new_from_array([[1, 0], [0, 1]]).replicate(w/2, h/2)
        if (bpat[1] == "R"):
            rmask = pyvips.Image.new_from_array([[0, 1], [0, 0]]).replicate(w/2, h/2)
            bmask = pyvips.Image.new_from_array([[0, 0], [1, 0]]).replicate(w/2, h/2)
        else:
            rmask = pyvips.Image.new_from_array([[0, 0], [1, 0]]).replicate(w/2, h/2)
            bmask = pyvips.Image.new_from_array([[0, 1], [0, 0]]).replicate(w/2, h/2)
    

    # convolve image and create color bands
    gconv = image.conv(gkernel)
    rbconv = image.conv(rbkernel)
    green = ((gmask > 0).ifthenelse(image, 0)).conv(gkernel)
    red   = ((rmask > 0).ifthenelse(image, 0)).conv(rbkernel)
    blue  = ((bmask > 0).ifthenelse(image, 0)).conv(rbkernel)
    outimage = red.bandjoin([green, blue])

    # writing output image
    writeimage(["-fmt", outfmt, outimage, outfilename])


# debayer (demosaic) using simple bilinear interpolation of green pixels only
# creating single band (green) image
# usage: debayer_gray [-fmt outfmt] [-v] [-b bayerpattern] <image> [outimage]
def debayer_green(param):
    bpat="RGGB"     # row-order: top down
    outfilename="-"
    outfmt="ppm"
    verbose=False
    for i in range(2):
        if (not param or not isinstance(param[0], str)): break
        if(param[0]=='-fmt'):
            outfmt=param[1]
            del param[0:2]
        elif(param[0]=='-b'):
            bpat=param[1]
            del param[0:2]
        elif(param[0]=='-v'):
            verbose=True
            del param[0]
    if verbose:
        print("# debayer_gray using bpat =", bpat, file=sys.stdout)

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


    # mask for green/red/blue pixels
    w = image.width
    h = image.height
    if (bpat[1:2] == "G"):  # e.g. RGGB
        gmask = pyvips.Image.new_from_array([[0, 1], [1, 0]]).replicate(w/2, h/2)
    else:
        gmask = pyvips.Image.new_from_array([[1, 0], [0, 1]]).replicate(w/2, h/2)
    

    # convolve image and create color bands
    green = ((gmask > 0).ifthenelse(image, 0)).conv(gkernel)
    outimage = green

    # writing output image
    writeimage(["-fmt", outfmt, "-16", outimage, outfilename])


# extract green image by using simple copy of green pixels, red/blue pixels
# are replaced by adjacing green pixels
# usage: debayer_greencopy [-fmt outfmt] [-v] [-b bayerpattern] <image> [outimage]
def debayer_greencopy(param):
    bpat="RGGB"     # row-order: top down
    outfilename="-"
    outfmt="ppm"
    verbose=False
    for i in range(2):
        if (not param or not isinstance(param[0], str)): break
        if(param[0]=='-fmt'):
            outfmt=param[1]
            del param[0:2]
        elif(param[0]=='-b'):
            bpat=param[1]
            del param[0:2]
        elif(param[0]=='-v'):
            verbose=True
            del param[0]
    if verbose:
        print("# debayer_greencopy using bpat =", bpat, file=sys.stdout)

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

    w = image.width
    h = image.height

    # extract bayer cells (1=top-left)
    p1 = image.subsample(2, 2)
    p2 = image.embed(-1, 0, w, h).subsample(2, 2)
    p3 = image.embed(0, -1, w, h).subsample(2, 2)
    p4 = image.embed(-1, -1, w, h).subsample(2, 2)

    if True:
        # combine/replicate green bayer cells
        if (bpat == "RGGB"):
            bmerge([p2,p3,p3,p2,outfilename])
        if (bpat == "BGGR"):
            bmerge([p2,p3,p3,p2,outfilename])
        if (bpat == "GBRG"):
            bmerge([p1,p4,p4,p1,outfilename])
        if (bpat == "GRBG"):
            bmerge([p1,p4,p4,p1,outfilename])
    else:
        # create half-size image
        if (bpat[0] == "G"):
            outimage = (p1+p4)/2
        else:
            outimage = (p2+p3)/2
        # writing output image
        writeimage(["-fmt", outfmt, "-16", outimage, outfilename])


# extract downsized green image by using subsample of green pixels
# usage: debayer_greensubsample [-fmt outfmt] [-v] [-b bayerpattern] <image> [outimage]
def debayer_greensubsample(param):
    bpat="RGGB"     # row-order: top down
    outfilename="-"
    outfmt="ppm"
    sample=4
    verbose=False
    for i in range(2):
        if (not param or not isinstance(param[0], str)): break
        if(param[0]=='-fmt'):
            outfmt=param[1]
            del param[0:2]
        elif(param[0]=='-b'):
            bpat=param[1]
            del param[0:2]
        elif(param[0]=='-v'):
            verbose=True
            del param[0]
    if verbose:
        print("# debayer_greencopy using bpat =", bpat, file=sys.stdout)

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

    w = image.width
    h = image.height

    # extract bayer cells (1=top-left)
    p1 = image.subsample(sample, sample)
    p2 = image.embed(-1, 0, w, h).subsample(sample, sample)

    if (bpat == "RGGB"):
        outimage=p2
    if (bpat == "BGGR"):
        outimage=p2
    if (bpat == "GBRG"):
        outimage=p1
    if (bpat == "GRBG"):
        outimage=p1

    # writing output image
    writeimage(["-fmt", outfmt, "-16", outimage, outfilename])


# no interpolation, creating RGB pixel from 2x2 bayer cells
# usage: debayer_halfsize [-fmt outfmt] [-b bayerpattern_up] <image> [outimage]
def debayer_halfsize(param):
    bpat="RGGB"     # row-order: top down
    outfilename="-"
    outfmt="ppm"
    for i in range(2):
        if (not param or not isinstance(param[0], str)): break
        if(param[0]=='-fmt'):
            outfmt=param[1]
            del param[0:2]
        elif(param[0]=='-b'):
            bpat=param[1]
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

    w = image.width
    h = image.height

    # extract bayer cells (1=top-left)
    p1 = image.subsample(2, 2)
    p2 = image.embed(-1, 0, w, h).subsample(2, 2)
    p3 = image.embed(0, -1, w, h).subsample(2, 2)
    p4 = image.embed(-1, -1, w, h).subsample(2, 2)

    # create half-size color image
    if (bpat == "RGGB"):
        red = p1
        #green = ptl
        green = (p2+p3)/2
        blue = p4
    if (bpat == "BGGR"):
        red = p4
        #green = ptl
        green = (p2+p3)/2
        blue = p1
    if (bpat == "GBRG"):
        red = p3
        #green = ptl
        green = (p1+p4)/2
        blue = p2
    if (bpat == "GRBG"):
        red = p2
        #green = ptl
        green = (p1+p4)/2
        blue = p3
    outimage = red.bandjoin([green, blue])

    # writing output image
    #outimage.ppmsave(outfilename, format=outfmt, strip=1)
    writeimage(["-fmt", outfmt, outimage, outfilename])


# debayer (demosaic) using high-quality bilinear interpolation (Malvar et al.,
# https://www.microsoft.com/en-us/research/wp-content/uploads/2016/02/Demosaicing_ICASSP04.pdf
# usage: debayer_malvar [-fmt outfmt] [-b bayerpattern_up] <image> [outimage]
def debayer_malvar(param):
    bpat="RGGB"     # row-order: top down
    outfilename="-"
    outfmt="ppm"
    for i in range(2):
        if (not param or not isinstance(param[0], str)): break
        if(param[0]=='-fmt'):
            outfmt=param[1]
            del param[0:2]
        elif(param[0]=='-b'):
            bpat=param[1]
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

    # mask for green/red/blue pixels
    w = image.width
    h = image.height
    if (bpat[1:2] == "G"):  # e.g. RGGB
        gmask = pyvips.Image.new_from_array([[0, 1], [1, 0]]).replicate(w/2, h/2)
        if (bpat[0] == "R"):
            rmask = pyvips.Image.new_from_array([[1, 0], [0, 0]]).replicate(w/2, h/2)
            bmask = pyvips.Image.new_from_array([[0, 0], [0, 1]]).replicate(w/2, h/2)
            g_in_r_row_mask = pyvips.Image.new_from_array([[0, 1], [0, 0]]).replicate(w/2, h/2)
            g_in_b_row_mask = pyvips.Image.new_from_array([[0, 0], [1, 0]]).replicate(w/2, h/2)
        else:
            rmask = pyvips.Image.new_from_array([[0, 0], [0, 1]]).replicate(w/2, h/2)
            bmask = pyvips.Image.new_from_array([[1, 0], [0, 0]]).replicate(w/2, h/2)
            g_in_r_row_mask = pyvips.Image.new_from_array([[0, 0], [1, 0]]).replicate(w/2, h/2)
            g_in_b_row_mask = pyvips.Image.new_from_array([[0, 1], [0, 0]]).replicate(w/2, h/2)
    else:
        gmask = pyvips.Image.new_from_array([[1, 0], [0, 1]]).replicate(w/2, h/2)
        if (bpat[1] == "R"):
            rmask = pyvips.Image.new_from_array([[0, 1], [0, 0]]).replicate(w/2, h/2)
            bmask = pyvips.Image.new_from_array([[0, 0], [1, 0]]).replicate(w/2, h/2)
            g_in_r_row_mask = pyvips.Image.new_from_array([[1, 0], [0, 0]]).replicate(w/2, h/2)
            g_in_b_row_mask = pyvips.Image.new_from_array([[0, 0], [0, 1]]).replicate(w/2, h/2)
        else:
            rmask = pyvips.Image.new_from_array([[0, 0], [1, 0]]).replicate(w/2, h/2)
            bmask = pyvips.Image.new_from_array([[0, 1], [0, 0]]).replicate(w/2, h/2)
            g_in_r_row_mask = pyvips.Image.new_from_array([[0, 0], [0, 1]]).replicate(w/2, h/2)
            g_in_b_row_mask = pyvips.Image.new_from_array([[1, 0], [0, 0]]).replicate(w/2, h/2)
    

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
    bpat="RGGB"     # row-order: top down
    outfilename="-"
    outfmt="ppm"
    verbose=False
    for i in range(3):
        if (not param or not isinstance(param[0], str)): break
        if(param[0]=='-fmt'):
            outfmt=param[1]
            del param[0:2]
        elif(param[0]=='-b'):
            bpat=param[1]
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
    command = ['bayer2rgb', '-f', bpat, '-m', method, '-b 16', '-t',
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
