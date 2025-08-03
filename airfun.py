#!/usr/bin/python3

VERSION="2.5.1"
"""
CHANGELOG
    2.5.1 - 31 Jul 2025
        * comets.cometname: handle name of interstellar comet
        * generally ignore AstropyDeprecationWarning

    2.5 - 17 Apr 2025
        * improc.imcrop: added option -b to keep requested crop size by adding
            black border if required
        * imutils.v2np: create 2D numpy array if input image has single band

    2.4 - 27 Dec 2024
        * new requirement: python3-photutils
        * new function improc.bgmap

    2.4a3 - 24 Dec 2024
        * improc.imbgsub: added option -s to split RGB images into 2D images
            for each color band

    2.4a2 - 24 Nov 2024
        * improc.immask: added option -i to use inverted mask
        * new function imutils.bgpixels
        * new functions findgaia.findgaia improc.imblur improc.imresize

    2.4a1 - 30 Sep 2024
        * split code into separate modules
        * new module coords.py containing functions used for converting pixel
            coordinates
        * new functions debayer_green bgnoise findpath

    2.3.7 - 06 Sep 2024
        * new requirements: astroquery.jplhorizons, astropy.time (replacing ephem)
        * ignore AstropyDeprecationWarning (reqired due to astroquery versions
          of some older Xubuntu distributions)
        * addephem, mkephem: modified to use astroquery.jplhorizons
        * regstat: added option -g to only analyze green channel of RGB image
        * ymd2jd, ymd2time, jd2ymd: modified to use astropy.time

    2.3.7a1 - 10 Jul 2024
        * impatsub: enhanced to support blurring of row/column pattern by
            using new option -b <gaussblur>
        * new function np2v

    2.3.6 - 11 May 2024
        * cleanhotpixel: interpret bayerpattern top-down

    2.3.5 - 21 Apr 2024
        * pnmccdred: if operating on DSLR raw image then get bayerpattern using
            rawpy/libraw (if not set by user parameter)
        * debayer*: parameter bpat is now interpreted top down

    2.3.4 - 15 Mar 2024
        * enhanced lrgb, it now defaults to operate in Lch color space and
            applies gaussian blur on hue only
        * new function imcompress
        
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

import os
import sys
import importlib
import argparse
import logging

import warnings
from astropy.utils.exceptions import AstropyDeprecationWarning
warnings.simplefilter('ignore', AstropyDeprecationWarning)

# default paths to search for modules
# list of paths starting with highest priority are
#   - program directory of airfun.py
#   - python system directories
#   - user defined modulepath (argument after -m option)
#   - current working dir
#   - develmodulepath if program directory of airfun.py is not below /usr
#   - distmodulepath (used with debian package installation)
distmodulepath = '/usr/lib/airtools/python3'
develmodulepath = os.environ['HOME'] + '/' + 'prog/python/airtools'

# log file name if logging is enabled
logfilename='/tmp/airfun.log'


def get_module(funcname):
    # get module name of directly callable functions
    modulename=None
    # list of function names within given module
    f_improc = [ 'pnmccdred', 'imcrop', 'immedian', 'imblur', 'imresize', 'pnmcombine', 'bmerge', 'cubeslice' ]
    f_improc = f_improc + [ 'lrgb', 'bgmap', 'imbgsub', 'pnmreplaceborder', 'impatsub', 'imcompress' ]
    f_improc = f_improc + [ 'immask', 'combinemasks', 'createmask', 'mkcluster' ]
    #
    f_imutils = [ 'listpixels', 'writeimage', 'datarange', 'regstat', 'imstat', 'bgpixels' ]
    f_rawproc = [ 'rawimsize', 'rawtogray' ]
    f_imconv = [ 'svgtopbm', 'ppmtogray', 'fitscubetoppm', 'fits3toppm', 'asciitoimage' ]
    f_ephem = [ 'addephem', 'mkephem' ]

    # match with lists
    if (funcname in f_improc):  modulename = 'improc'
    if (funcname in f_imutils): modulename = 'imutils'
    if (funcname in f_rawproc): modulename = 'rawproc'
    if (funcname in f_imconv):  modulename = 'imconv'
    if (funcname in f_ephem):   modulename = 'ephem'

    # others
    if (funcname == 'cometname'): modulename = 'comets'
    
    if (modulename):
        return importlib.import_module(modulename)
    else:
        if (verbose):
            print('WARNING: assuming module name equals function name', funcname, file=sys.stderr)
        return importlib.import_module(funcname)



# parse arguments
parser = argparse.ArgumentParser()
parser.add_argument("-v", "--version", action="store_true",
    help="show program version")
parser.add_argument("-m", "--modulepath",
    help="add user module path")
parser.add_argument("--verbose", action="store_true",
    help="show additional messages")
parser.add_argument("-l", "--log", action="store_true",
    help="send log messages to file " + logfilename)
parser.add_argument("funccall", nargs=argparse.REMAINDER, metavar="...",
    help="function call")

# store arguments into variables
args = parser.parse_args()
verbose = args.verbose
usermodulepath = args.modulepath
do_log = args.log
do_log = True   #### EDIT ####

if (args.version):
    print(VERSION)
    if verbose:
        print('file =', __file__)
        print('sys.path =', sys.path)
    exit()

if (not args.funccall):
    parser.print_usage()
    if verbose: print('sys.path =', sys.path)
    exit()

funcname=args.funccall[0]
if (len(args.funccall) > 1):
    funcargs=args.funccall[1:]
else:
    funcargs=[]

# some debug info
if False:
    print('function = ', funcname)
    print('funcargs = ', funcargs)
    if verbose: print('is verbose')
    exit()



# optionally setup logging to temp file
if do_log:
    logger = logging.getLogger('airfun.py')
    logging.basicConfig(filename=logfilename, encoding='utf-8', level=logging.INFO, format='%(asctime)s %(message)s')

# add modulepaths
if (usermodulepath):
    sys.path.append(usermodulepath)
sys.path.append('.')
if not __file__.startswith('/usr'):
    sys.path.append(develmodulepath)
sys.path.append(distmodulepath)
if verbose:
    print('module paths =', sys.path, file=sys.stderr)


# import module functions
if verbose:
    print('Search for module required by', funcname, file=sys.stderr)
module = get_module(funcname)

# emulate "from module import *"
# get all function names of module
if "__all__" in module.__dict__:
    names = module.__dict__["__all__"]
else:
    # otherwise we import all names that don't begin with _
    names = [x for x in module.__dict__ if not x.startswith("_")]
# now merge them into global namespace
globals().update({k: getattr(module, k) for k in names})

# run function call
if verbose:
    print('Calling function', funcname, file=sys.stderr)
if do_log:
    logger.info('airfun.py ' + funcname)
result = getattr(module, funcname)(funcargs)

if isinstance(result, str) | isinstance(result, int):
    print(result)
else:
    if result:
        print(type(result))

exit()
