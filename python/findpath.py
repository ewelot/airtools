#!/usr/bin/python3

import sys
import os
import math
import numpy as np

from scipy.optimize import curve_fit
from scipy.optimize import OptimizeWarning
import matplotlib.pyplot as plt
import warnings
warnings.simplefilter('ignore', OptimizeWarning)

import pyregion
import pyvips

from imutils import bgnoise, v2np, np2v, writeimage
from misc import gaussian1D, regheader
from coords import fits2cart, cart2fits, cart2pol, pol2cart, impix2fits


# syntax: findpath [-f] [-p] [-w stripwidth] [-m medwidth] [-s stddev] inimg regfile [outfilebase]
def findpath(param):
    showplot=False  # for each vector show path data points
    saverot=False   # for each vector save (large) rotated image
    pwidthmax=15    # max FWHM of a path

    outfmt='png'
    verbose=False
    swidth_mult=1.  # multiplyer to change width of image strip to extract
    length_mult=1.  # multiplyer to change length of window along x-axis to compute quartile
    stddev_mult=1.  # multiplyer to change noise value in image
    syntax='syntax: findpath [-f] [-w swidth_mult] [-l length_mult] [-s stddev_mult] inimg regfile outfilebase'.format()
    for i in range(len(param)):
        if(param[0]=='-h'):
            print(syntax, file=sys.stderr)
            exit(1)
        if(param[0]=='-f'):
            outfmt='fits'
            del param[0]
        if(param[0]=='-v'):
            verbose=True
            del param[0]
        if(param[0]=='-p'):
            showplot=True
            del param[0]
        if(param[0]=='-w'):
            swidth_mult=float(param[1])
            del param[0:2]
        if(param[0]=='-l'):
            length_mult=float(param[1])
            del param[0:2]
        if(param[0]=='-s'):
            stddev_mult=float(param[1])
            del param[0:2]
    if (len(param) < 2 or len(param) > 3):
        print(syntax, file=sys.stderr)
        exit(1)

    infilename = param[0]
    regfilename = param[1]
    imgnum = os.path.basename(infilename).split('.')[0]
    if (len(param) > 2):
        outfilebase = param[2]
    else:
        outfilebase = imgnum + ".path"


    # reading input image
    if (infilename and infilename != '-'):
        inimg = pyvips.Image.new_from_file(infilename)
    else:
        source = pyvips.Source.new_from_descriptor(sys.stdin.fileno())
        inimg = pyvips.Image.new_from_source(source, "")

    # reading DS9 region file
    regions = pyregion.open(regfilename)

    # in case of RGB image extract green channel only
    if (inimg.bands == 3):
        inimg = inimg[1]
    stddev=stddev_mult*bgnoise(inimg)
    if verbose:
        print('# noise={:.1f}'.format(stddev), file=sys.stderr)

    # output region file containing polygons around paths
    outregfile = open(outfilebase + ".reg", "w+")
    outregfile.write(regheader())

    # parse vectors in regfile
    pathnum=0
    for region in regions:
        if (region.name != 'vector'):
            # TODO: copy region to outregfile
            continue
        pathnum = pathnum+1

        # image strip
        outstripimgfilename=outfilebase + str(pathnum) + "." + outfmt
        # text data file containing valid path points in imgstrip
        fname=outfilebase + str(pathnum) + ".dat"
        outdatafile = open(fname, "w+")
        outdatafile.write("# num x center ampl fwhm err_center err_fwhm\n")
        # region file containing path points and region in imgstrip
        fname=outfilebase + str(pathnum) + ".reg"
        outstripregfile = open(fname, "w+")
        outstripregfile.write(regheader())

        if saverot:
            # rotated image of single path
            outrotimgfilename=outfilebase + str(pathnum) + "_rot." + outfmt
            # region file containing path region in rotated image
            fname = outfilebase + str(pathnum) + "_rot.reg"
            outrotregfile = open(fname, "w+")
            outrotregfile.write(regheader())

        # read vector data, x,y are FITS coordinates of start point
        # x, y, length, angle (ccw)
        x1, y1, vl, va = region.coord_list
        
        # determine width of image strip to be used for path detection
        swidth = 2*int(swidth_mult * (30+vl/150) / 2)
        length = 2*int(length_mult * (30+vl/300) / 2)
        
        # middle point (FITS)
        pi=math.pi
        xm = x1 + vl/2*math.cos(va*pi/180)
        ym = y1 + vl/2*math.sin(va*pi/180)
        if verbose:
            print('# xm={:.1f} ym={:.1f}'.format(xm, ym), file=sys.stderr)
        # distance from image center (counting right, up)
        dx, dy = np.subtract(fits2cart(xm, ym), (inimg.width/2, inimg.height/2))
        # polar coordinates with respect to image center
        r, pa = cart2pol(dx, dy)
        # rotated middle point
        # note: vips rotate does rotate an image clockwise not counterclockwise!
        xrot, yrot = pol2cart(r, pa - va*pi/180)   # right of and above center
        if verbose:
            print('# r={:.1f} pa={:.1f} xrot={:.0f} yrot={:.0f}'.format(r, pa*180/pi, xrot, yrot), file=sys.stderr)
        
        # offset of upper point of image box above center of rotated image
        yoff = round(yrot + 0.5 + swidth/2)
        
        # extract and smooth image strip
        ranknum=int(length/6)
        imgrot = inimg.rotate(va)
        imgstrip = imgrot.crop(0, imgrot.height/2-yoff, imgrot.width, swidth).rank(length, 1, ranknum)

        # determine range of valid columns in imgstrip
        #   start and end of non-border pixels containing valid image data
        #   start and endpoint of vector: width/2+xrot +- vl/2
        val = v2np(imgstrip.crop(0,swidth/2,imgstrip.width,1)).reshape(imgstrip.width)
        idx = np.arange(imgstrip.width)
        datastart=np.min(idx[val>0])    # first non-zero pixel
        dataend=np.max(idx[val>0])      # last non-zero pixel
        xstart=np.max([datastart+length/2, imgstrip.width/2 + xrot-vl/2])
        xend=np.min([dataend-length/2, imgstrip.width/2 + xrot+vl/2])
        if verbose:
            print('# xrange: {:.1f} {:.1f}'.format(xstart, xend))
        
        # fit gaussian profiles perpendicular to vector at several points
        xstrip=[]
        center=[]
        pfwhm=[]
        for x in np.arange(xstart, xend, length):
            # column to be extracted from image strip
            x = int(x + np.random.normal(0, length/3))
            # pixel index coordinates from top to bottom in imgstrip:
            xdata = np.array(range(swidth))
            # intensity value of single column in imgstrip:
            ydata = v2np(imgstrip.crop(x,0,1,swidth)).reshape(swidth)
            
            # gaussian fit to determine line center and width
            p0guess = [np.median(ydata), 100, np.mean(xdata), 3]   # initial guess of ybase, ampl, xcenter, sigma
            # note: it is much better to not provide initial guess, e.g. p0=p0guess
            try:
                popt, pcov = curve_fit(gaussian1D, xdata, ydata)
                # TODO: ignore: OptimizeWarning: Covariance of the parameters could not be estimated
                perr = np.sqrt(np.diag(pcov))
                ybase, ampl, xcenter, sigma = popt
                err_ybase, err_ampl, err_xcenter, err_sigma = perr
                
                fwhm = np.abs(2.355*sigma)
                err_fwhm = 2.355*err_sigma
                
                if False:
                    yfit = gaussian1D(xdata, ybase, ampl, xcenter, sigma)
                    plt.plot(xdata, ydata, 'ko', label='data')
                    plt.plot(xdata, yfit, '-k', label='fit')
                    plt.show()
                
                amplmin=5*stddev/np.sqrt(length)
                if (fwhm < pwidthmax and ampl > amplmin and
                    err_xcenter < pwidthmax/2 and err_fwhm < pwidthmax):
                    line='{:d} {:.0f} {:.1f} {:.0f} {:.1f} {:.1f} {:.1f}\n'.format(
                        pathnum, x, swidth - xcenter, ampl, fwhm, err_xcenter, err_fwhm)
                    outdatafile.write(line)
                    
                    # save data for later plotting
                    xstrip.append(x)
                    center.append(xcenter)  # top-down (pixel index y coordinate)
                    pfwhm.append(fwhm)

                    # append to output region
                    line='circle({:.1f},{:.1f},{:.1f}) # color=yellow text={{{:d}}}\n'.format(
                        x, swidth - xcenter, fwhm, pathnum)
                    outstripregfile.write(line)
            except RuntimeError:
                pass

        # closing output data file
        outdatafile.close()
        
        # writing output images of rotated image and image strip
        if saverot:
            writeimage(["-fmt", outfmt, imgrot, outrotimgfilename])
        writeimage(["-fmt", outfmt, imgstrip, outstripimgfilename])
        
        if (len(xstrip) < 5):
            print('ERROR: {} unable to trace vector {:d}'.format(regfilename, pathnum), file=sys.stderr)
            color="red"
            line='# vector({},{},{},{}) vector=1 color={}\n'.format(x1, y1, vl, va, color)
            outregfile.write(line)
            continue
        else:
            # convert lists to arrays
            xstrip=np.array(xstrip)
            center=np.array(center)
            pfwhm=np.array(pfwhm)

        # fit polynome line to gaussian center points
        deg=1
        if (len(xstrip) > 10): deg=2
        if (len(xstrip) > 30): deg=3
        coeff, cov = np.polyfit(xstrip, center, deg=deg, cov=True)
        yres = center - np.polyval(coeff, xstrip)
        rms = np.sqrt(sum(yres**2)/(len(xstrip)-deg-1))
        if verbose:
            print('path {:d}: n={:d} deg={:d} resid={:.1f}'.format(pathnum, len(xstrip), deg, rms))

        # remove outliers
        outitermax=5
        outiter=0
        valid = np.abs(yres) < 2.5*rms
        if (len(xstrip[valid]) < len(xstrip)):
            outiter = outiter+1
            xok = xstrip[valid]
            yok = center[valid]
            pfok = pfwhm[valid]
            coeff, cov = np.polyfit(xok, yok, deg=deg, cov=True)
            yres = yok - np.polyval(coeff, xok)
            rms = np.sqrt(sum(yres**2)/(len(xok)-deg-1))
            if verbose:
                print('path {:d}: iter={:d} num={:d} deg={:d} resid={:.1f} fwhm={:.1f}'.format(
                    pathnum, outiter, len(xok), deg, rms, np.median(pfok)))

            # remove outliers and fit again
            while outiter < outitermax and rms > 0.2*np.median(pfok):
                valid = np.abs(yres) < 2.5*rms
                if (len(xok[valid]) == len(xok)):
                    break
                outiter = outiter+1
                xok = xok[valid]
                yok = yok[valid]
                pfok = pfok[valid]
                coeff, cov = np.polyfit(xok, yok, deg=deg, cov=True)
                yres = yok - np.polyval(coeff, xok)
                rms = np.sqrt(sum(yres**2)/(len(xok)-deg-1))
        else:
            xok=xstrip
            pfok=pfwhm

        # write results to output
        if (rms > 0.5*np.median(pfok)):
            print('ERROR: {}: unable to get reasonable fit of vector {:d}'.format(regfilename, pathnum), file=sys.stderr)
            color="yellow"
            line='# vector({},{},{},{}) vector=1 color={}\n'.format(x1, y1, vl, va, color)
            outregfile.write(line)
            continue
        else:
            n=len(np.arange(xstart, xend, length))
            npts='{:d}/{:d}/{:d}'.format(len(xok), len(xstrip), n)
            s='{} {:d} l={:.0f}:'.format(imgnum, pathnum, vl)
            print('{:15s} iter={:d} num={:12s} deg={:d} resid={:.1f} fwhm={:.1f}'.format(
                s, outiter, npts, deg, rms, np.quantile(pfok, 0.75)))
            
        
        # create polygon region around fitted path and write it to output file
        pwidth = 3*np.quantile(pfok, 0.75) + 4    # width of fitted path
        polyS="polygon("    # polygon region referring to image strip
        polyR="polygon("    # polygon region referring to rotated image
        poly="polygon("     # polygon region referring to input image
        for xp in np.linspace(xstart-length, xend+length, 7):
            # get lower points of polygon
            # xp, yp are impix coordinates of path in imgstrip
            yp = np.polyval(coeff, xp)
            # fits coordinates of lower points of polygon in imgstrip
            x, y = impix2fits(xp, yp, imgstrip.height)
            y = y - pwidth/2
            polyS = polyS + '{:.1f},{:.1f},'.format(x, y)
            
            # fits coordinates of lower points of polygon in imgrot
            y = y + imgrot.height/2+yoff-imgstrip.height
            polyR = polyR + '{:.1f},{:.1f},'.format(x, y)
            # cartesian coordinates of lower points of polygon in imgrot
            x, y = fits2cart(x, y)
            # polar coordinates in imrot
            r, pa = cart2pol(x-imgrot.width/2, y-imgrot.height/2)
            # offset of rotated points from center of imgrot and inimg
            dx, dy = pol2cart(r, pa+va*pi/180)
            # fits coordinates of lower points of polygon in inimg
            x, y = np.add(cart2fits(dx, dy), (inimg.width/2, inimg.height/2))
            poly  = poly  + '{:.1f},{:.1f},'.format(x, y)
            
            if False:
                # coordinates (right, up) with respect to center of rotated image
                dxr = xp - imgrot.width/2 - 0.5
                dyr = yoff - np.polyval(coeff, xp) - 0.5 - pwidth/2
                r, pa = cart2pol(dxr, dyr)
                # coordinates (right, up) with respect to center of input image
                dx, dy = pol2cart(r, pa+va*pi/180)
                # fits coordinates in input image
                x = inimg.width/2 + dx + 0.5
                y = inimg.height/2 + dy + 0.5
                polyS = polyS + '{:.1f},{:.1f},'.format(xp+1, swidth-np.polyval(coeff, xp)+pwidth/2)
                poly  = poly  + '{:.1f},{:.1f},'.format(x, y)
        for xp in np.linspace(xend+length, xstart-length, 7):
            # get upper points of polygon
            # xp, yp are impix coordinates of path in imgstrip
            yp = np.polyval(coeff, xp)
            # fits coordinates of lower points of polygon in imgstrip
            x, y = impix2fits(xp, yp, imgstrip.height)
            y = y + pwidth/2
            polyS = polyS + '{:.1f},{:.1f},'.format(x, y)

            # fits coordinates of lower points of polygon in imgrot
            y = y + imgrot.height/2+yoff-imgstrip.height
            polyR = polyR + '{:.1f},{:.1f},'.format(x, y)
            # cartesian coordinates of lower points of polygon in imgrot
            x, y = fits2cart(x, y)
            # polar coordinates in imrot
            r, pa = cart2pol(x-imgrot.width/2, y-imgrot.height/2)
            # offset of rotated points from center of imgrot and inimg
            dx, dy = pol2cart(r, pa+va*pi/180)
            # fits coordinates of lower points of polygon in inimg
            x, y = np.add(cart2fits(dx, dy), (inimg.width/2, inimg.height/2))
            poly  = poly  + '{:.1f},{:.1f},'.format(x, y)

            if False:
                # upper points of polygon
                dxr = xp - imgrot.width/2 - 0.5
                dyr = yoff - np.polyval(coeff, xp) - 0.5 + pwidth/2
                r, pa = cart2pol(dxr, dyr)
                # coordinates (right, up) with respect to center of input image
                dx, dy = pol2cart(r, pa+va*pi/180)
                # fits coordinates in input image
                x = inimg.width/2 + dx + 0.5
                y = inimg.height/2 + dy + 0.5
                polyS = polyS + '{:.1f},{:.1f},'.format(xp+1, swidth-np.polyval(coeff, xp)-pwidth/2)
                poly  = poly  + '{:.1f},{:.1f},'.format(x, y)
        polyS = polyS[:-1] + ')\n'
        polyR = polyR[:-1] + ')\n'
        poly  = poly[:-1]  + ')\n'
        outstripregfile.write(polyS)
        outstripregfile.close()
        if saverot:
            outrotregfile.write(polyR)
            outrotregfile.close()
        outregfile.write(poly)
        
        # plotting
        if showplot:
            plt.plot(xstrip, center, 'ko', label='data')
            xfit = np.linspace(xstart, xend, length)
            yfit = np.polyval(coeff, xfit)
            plt.plot(xfit, yfit, '-k', label='fit')
            plt.title('Path No.' + str(pathnum))
            plt.show()

    outregfile.close()
