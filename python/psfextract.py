#!/usr/bin/python3

"""
set=co01
rlim=6
log=psfextract.log
pdir=~/prog/python/airtools
phottable=psf/$set.phot.fits
fwhm=$(get_header -s $set.head AI_FWHM)
magzero=$(echo $(get_header -s $set.head MAGZERO,EXPTIME,NEXP) | awk '{printf("%.2f", $1+2.5/log(10)*log($2/$3))}')
xy=$(echo id $(get_header -s $set.head AI_CORA,AI_CODEC) | rade2xy - $set.wcs.head | awk '{printf("%.0f %.0f", $2, $3)}')
trail=$(omove2trail $set)
$pdir/psfextract.py    -r $rlim -m $magzero -f $fwhm $set $set.bgs.fits $xy | tee -a $log
$pdir/psfextract.py -R -r $rlim -m $magzero -f $fwhm $set $set.bgs.fits $xy psf/$set.phot.1.fits | tee -a $log
$pdir/psfextract.py -B -r $rlim -m $magzero -f $fwhm $set $set.bgs.fits $xy psf/$set.phot.1.fits | tee -a $log

#$pdir/psfextract.py -r $rlim $set $set.bgs.fits ${set}_m.bgs.fits $xy $trail $phottable

stilts tmatchn matcher=exact nin=3 \
    in1=psf/$set.phot.0.fits values1="uid" suffix1="_R" \
    in2=psf/$set.phot.1.fits values2="uid" suffix2="_G" \
    in3=psf/$set.phot.2.fits values3="uid" suffix3="_B" \
    ocmd="addcol isrgb 'flags_R==0 && flags_B==0 && flux_fit_R>0 && flux_fit_G>0 && flux_fit_B>0'" \
    out=$set.RGBphot.fits

ftselect -f uid_G,x_fit_G,y_fit_G,mag_R,mag_G,mag_B,magerr_G co01.RGBphot.fits "isrgb==true"
"""

VERSION="0.3"
"""
CHANGELOG
    # TODO:
        - improve photometry by running aperture photometry on residual image
        - add option to set user defined psfsize
        - smooth image data for high fwhm
        - apply mask on star psf
        - allow to use different area sizes for psf extraction and star
          subtraction by setting different radii

    0.3 - 17 Jun 2025
        * increased psfsize to 31
        * added options to set saturation, fwhm and magzero
        * added options to work on red/blue color bands using fixed star
          positions
        * new functions: mkcutouts phot2dat
        * save large size result images using float data type instead of double
        * compute mag and magerr
        * propagate total flux of star PSF via FITS header of phottab

    0.2 - 29 May 2025
        * use small psfsize=21
        * improved filtering of sources
        * apply mask on star trails
        * use initial guesses in DAOPhotPSFPhotometry (to keep source
            identifications)
        
    0.1 - 23 Apr 2025
        * initial version
"""

"""
    notes on table column names
    photutils version 1.6.0
    - output of DAOStarFinder
        ['id', 'xcentroid', 'ycentroid', 'sharpness', 'roundness1', 'roundness2', 
        'npix', 'sky', 'peak', 'flux', 'mag']
    - input to subtract_psf
        either table with ['x_fit', 'y_fit', 'flux_fit'] or array interpreted as (x, y, flux)
    - init_guesses as input to DAOPhotPSFPhotometry.do_photometry()
        table with ['x_0', 'y_0'] and optionally 'flux_0'
    - output of DAOPhotPSFPhotometry.do_photometry()
        keeps columns of init_guesses table and adds
        ['flux_0', 'id', 'group_id', 'x_fit', 'y_fit', 'flux_fit', 'flux_unc', 
        'x_0_unc', 'y_0_unc', 'iter_detected']
        
"""

import sys
import os
import math
import re
import time
import datetime
import numpy as np

import pyvips
import matplotlib.pyplot as plt

from astropy.io import fits
from astropy.table import Table
from astropy.nddata import NDData
from astropy.stats import sigma_clipped_stats, SigmaClip
from astropy.visualization import simple_norm
from astropy.modeling.fitting import TRFLSQFitter
from photutils.background import Background2D, SExtractorBackground
from photutils.segmentation import detect_sources
from photutils.detection import DAOStarFinder, IRAFStarFinder
from photutils.aperture import CircularAperture
from photutils.psf import extract_stars, subtract_psf, EPSFBuilder, EPSFModel
from photutils.psf import DAOGroup, BasicPSFPhotometry, DAOPhotPSFPhotometry

import warnings
from astropy.utils.exceptions import AstropyDeprecationWarning
warnings.simplefilter('ignore', AstropyDeprecationWarning)
warnings.filterwarnings('ignore', message='.*The fit may be unsuccessful.*')
warnings.filterwarnings('ignore', message='.*Both init_guesses and finder are different than None.*')

sys.path.append(os.getenv('HOME') + '/prog/python/airtools')
from imutils import writeimage, v2np, np2v, vips_format_to_np_dtype, np_dtype_to_vips_format


def xy2reg(data, regfilename, rad=5, xadd=0, yadd=0, yflip=None):
    '''
    create region file (circles) from xy-points in a table or 2D-array

    for tables several column names are recognized
    for 2D-array we simply assume rows of x,y or x,y,mag or id,x,y,mag
    
    TODO: add options -xadd -yadd to add offsets to point positions
    '''
    # default parameters
    verbose=False
    # recognized table column names
    xcolnames=['x', 'x_fit', 'xcentroid', 'xwin_image', 'xcenter', 'x_0']
    ycolnames=['y', 'y_fit', 'ycentroid', 'ywin_image', 'ycenter', 'y_0']
    idcolnames=['uid', 'src_id', 'id', 'number']
    magcolnames=['mag', 'mag_auto']
    
    x, y = None, None
    sid=None    # optional id column
    mag=None    # optional mag column
    if(isinstance(data, Table)):
        t=data
        tcolnames = t.colnames
        is_error=False

        for xcolname in xcolnames + [s.upper() for s in xcolnames]:
            if (xcolname in tcolnames):
                x=t.columns.get(xcolname).data
                break
        if (x is None):
            is_error=True
            print('ERROR: unknown x column', file=sys.stderr)

        for ycolname in ycolnames + [s.upper() for s in ycolnames]:
            if (ycolname in tcolnames):
                y=t.columns.get(ycolname).data
                break
        if (y is None):
            is_error=True
            print('ERROR: unknown y column', file=sys.stderr)

        for magcolname in magcolnames + [s.upper() for s in magcolnames]:
            if (magcolname in tcolnames):
                mag=t.columns.get(magcolname).data
                break
        if (mag is None):
            print('WARNING: unknown mag column', file=sys.stderr)

        for idcolname in idcolnames + [s.upper() for s in idcolnames]:
            if (idcolname in tcolnames):
                sid=t.columns.get(idcolname).data
                break
        if (sid is None):
            print('WARNING: unknown id column', file=sys.stderr)
        if is_error: exit(-1)
    else:
        if(isinstance(data, np.ndarray)):
            a=data
            if(a.ndim != 2):
                print('ERROR: not a 2D-array', file=sys.stderr)
                exit(-1)
            if(a.shape[1] < 2):
                print('ERROR: too few columns in array', file=sys.stderr)
                exit(-1)
            if(a.shape[1] == 2):
                x = a[:,0]
                y = a[:,1]
                print('WARNING: no magnitudes provided by array', file=sys.stderr)
            if(a.shape[1] >= 3):
                sid = a[:,0]
                x = a[:,1]
                y = a[:,2]
            if(a.shape[1] > 3):
                mag = a[:,3]
        else:
            print('ERROR: input is neither table nor ndarray', file=sys.stderr)
            exit(-1)
    
    # write output file
    hdr='# Region file format: DS9 version 4.1\n'
    hdr=hdr + 'global color=green dashlist=8 3 width=1 font="helvetica 10 normal roman"'
    hdr=hdr + ' select=1 highlite=1 dash=0 fixed=0 edit=1 move=1 delete=1 include=1 source=1\n'
    hdr=hdr + 'physical\n'

    outregfile = open(regfilename, "w+")
    outregfile.write(hdr)
    # TODO: deal with data from masked columns
    for i in range(len(x)):
        if (sid is None): idval=i+1
        else: idval=sid[i]
        xval = x[i] + xadd + 1
        yval = y[i] + yadd
        if (yflip is not None): yval=yflip-yval
        if (mag is None):
            line='circle({:.2f},{:.2f},5) # text={{{:d}}}\n'.format(xval, yval, idval)
        else:
            magval = mag[i]
            line='circle({:.2f},{:.2f},5) # text={{{:d} {:5.2f}}}\n'.format(xval, yval, idval, magval)
        outregfile.write(line)
    outregfile.close()


def phot2dat(phottab, outfilename, xadd=0, yadd=0, intype='phot'):
    '''
    write photometry data text file
    note: coordinate systems are offset by (0.5,0.5)
    '''
    # required table column names
    if (intype == 'phot'):
        idcol,xcol,ycol,magcol,magerrcol = 'uid','x_fit','y_fit','mag','magerr'
    else:
        idcol,xcol,ycol,magcol,magerrcol = 'id','xcentroid','ycentroid','mag','mag'

    for c in (idcol,xcol,ycol,magcol,magerrcol):
        if (not c in phottab.colnames):
            print('ERROR: missing column {}'.format(c), file=sys.stderr)
            exit(-1)

    # write output file
    outfile = open(outfilename, "w+")
    for i in range(len(phottab)):
        r=phottab[i]
        magerr=r[magerrcol]
        if (intype != 'phot'): magerr=1
        #if (yflip is not None): yval=yflip-yval
        line='{:10s}  {:7.2f} {:7.2f}  {:6.3f} {:6.3f} {:6.3f}    0   0     0   0 {:5.3f}\n'.format(
            str(r[idcol]), r[xcol]+xadd+0.5, r[ycol]+yadd+0.5, r[magcol], r[magcol], r[magcol], magerr)
        outfile.write(line)
    outfile.close()


def readsextable(sextable_filename):
    '''
    read sources from single source extractor output catalog
    '''
    hdus = fits.open(sextable_filename)
    extlist = []
    for i in range(len(hdus)):
        hdu = hdus[i]
        if isinstance(hdu, fits.hdu.image.PrimaryHDU): continue
        if (hdu.header['EXTNAME'] == 'LDAC_OBJECTS'):
            extlist.append(i)
    hdus.close()
    print(extlist)
    if (len(extlist) == 0):
        print('ERROR: no LDAC_OBJECTS table found', file=sys.stderr)
        exit(-1)
    if (len(extlist) != 1 and len(extlist) != 3):
        print('ERROR: unsupported number of LDAC_OBJECTS tables', file=sys.stderr)
        exit(-1)
    # read sources extracted from single image plane
    if (len(extlist) == 3):
        # use second (green) image plane
        extnum=extlist[1]
    else:
        extnum=extlist[0]
    print('reading LDAC_OBJECTS table at extension {:d}'.format(extnum+1))
    sources = Table.read(sextable_filename, format='fits', hdu=extnum)
    xcolname, ycolname = 'xcentroid', 'ycentroid'
    sources.rename_column('XWIN_IMAGE', xcolname)
    sources.rename_column('YWIN_IMAGE', ycolname)
    sources.rename_column('NUMBER',    'id')
    sources.rename_column('MAG_AUTO',  'mag')
    sources.rename_column('FLUX_AUTO', 'flux')
    sources.rename_column('FLAGS',     'flags')
    
    # TODO: converting to python image coordinates
    #   the returned positions might need to be offset when using with cropped image
    #sources[xcolname] = sources[xcolname] - 1
    #sources[ycolname] = inimg.height - sources[ycolname]
    return(sources)


def background(img, bsize, do_plot_segmentimage=False):
    # background estimation from star stack
    # first iteration - simple statistics
    data = v2np(img)
    bg0 = Background2D(data, bsize, filter_size=1,
            bkg_estimator=SExtractorBackground())
    median, sd = bg0.background_median, bg0.background_rms_median
    print('median={:.1f} sd={:.1f}'.format(median, sd), flush=True)
    data = data - bg0.background
    # second iteration - mask bright sources before running statistics
    segment_map = detect_sources(data, 4*sd, npixels=5)
    if do_plot_segmentimage:
        plt.figure()
        plt.title('Segment image ...')
        plt.imshow(segment_map, origin=origin, cmap=segment_map.cmap,
            interpolation='nearest')
        plt.show(block=False)
    mask = segment_map.data.astype(bool)
    # TODO: print percentage of masked pixels
    bg1 = Background2D(data, bsize, filter_size=3, mask=mask,
            bkg_estimator=SExtractorBackground())
    median, sd = bg1.background_median, bg1.background_rms_median
    print('median={:.1f} sd={:.1f}'.format(median, sd), flush=True)
    bgdata = bg0.background + bg1.background
    return(sd, bgdata)


def mktrailmask(trail, trailwidth, imsize=None):
    '''
    returns vips image
    trail - length/pix,angle/deg,center/fraction of length
    notes:
        - angle is measured from right over top
        - center describes the location at time of reference image
        - trail vector corresponds to motion of the target, motion of field
          stars in a comet stack therefore is opposite (angle+180)
    '''
    tlen,ta,ctr = trail
    if (imsize is None):
        imsize=2*int(tlen*max(ctr, 1-ctr) + trailwidth/2 + 2)+1
    img=pyvips.Image.black(imsize, imsize)
    # start coordinates
    tarad = math.radians(ta+180)
    x1,y1 = (imsize-1)/2+tlen*ctr*math.cos(tarad), (imsize-1)/2-tlen*ctr*math.sin(tarad)
    x2,y2 = (imsize-1)/2-tlen*(1-ctr)*math.cos(tarad), (imsize-1)/2+tlen*(1-ctr)*math.sin(tarad)
    img=img.draw_line(255,x1,y1,x2,y2)
    ksize=2*int(trailwidth/2+0.5)+1
    kernel = pyvips.Image.mask_ideal(ksize, ksize, 1, optical=True, reject=True, uchar=True)
    img=(img.conv(kernel) > 0).ifthenelse(1,0)
    return(img)


def filterpsfsources(sources, imsize, psfsize, saturation, fwhm, nbright):
    '''
    returns subset of sources suitable for building ePSF
    
    note: sources is output of DAOFind
    imsize is boxsize of crop
    '''
    # filter settings to identify close neighbors of bright sources (not used
    # as psf stars
    dmag = 2.5      # max. mag diff to identify close neighbors
    dmax = 3*fwhm+3 # max. distance to count as close neighbor
    xcolname, ycolname, fluxcolname = 'xcentroid', 'ycentroid', 'flux'

    # number of brigthest sources to check at most
    nmax = int(1.5*nbright+0.5)

    # brightest non-saturated sources not located close to edge of star field
    # TODO: trail length should be taken into account
    dx, dy = sources[xcolname] - imsize/2, sources[ycolname] - imsize/2
    isinside = np.sqrt(dx**2 + dy**2) < imsize/2-2*psfsize
    sources.sort(fluxcolname, reverse=True)
    mask = isinside & (sources['peak']<saturation)
    if ('roundness2' in sources.colnames):
        # do statistics on roundness2 to eliminate outliers
        r2mean, r2md, r2sd = sigma_clipped_stats(sources[mask][0:nmax]['roundness2'], sigma=3, maxiters=4)
        r2low, r2high = r2md - 4*r2sd, r2md + 4*r2sd
        print('limits on roundness2: {:.2f} - {:.2f}'.format(r2low, r2high))
        mask = mask & (sources['roundness2']>r2low) & (sources['roundness2']<r2high)
    brightsources = sources[mask][0:nmax]

    
    isok = np.zeros(len(brightsources), dtype=bool)
    brightmaglim = brightsources['mag'][0] + 1.0
    for i in range(nmax):
        # exclude stars with very bright sources within psfsize/2+2*fwhm
        x, y = brightsources[xcolname][i], brightsources[ycolname][i]
        #print('{:2d} {:4.0f} {:4.0f} {:4.1f}'.format(i,x,y,mag))
        s=sources[(sources['mag'] < brightmaglim)]
        inx = abs(s[xcolname] - x) < psfsize/2+1*fwhm
        iny = abs(s[ycolname] - y) < psfsize/2+1*fwhm
        if (sum(inx & iny) > 1):
            continue

        # exclude stars with close neighbors 
        s=sources[(sources['mag'] < brightsources['mag'][i] + dmag)]
        #print('{:d}: checking {:d} sources'.format(i,len(s)))
        dx, dy = s[xcolname] - x, s[ycolname] - y
        d = np.sqrt(dx**2 + dy**2)
        if (sum(d < dmax) > 1):
            continue
        isok[i] = True
        if (sum(isok) >= nbright): break
    print('number of bright sources eliminated: {:d} (out of {:d})'.format(i+1 - sum(isok), i+1), flush=True)
    
    return(brightsources[isok])


def filtertrailedsources(sources, trail, fwhm, nbright):
    '''
    returns subset of sources suitable for building ePSF of star trail

    note: sources is phot catalog (output of PSFPhotometry)
    '''
    dmag = 1.5      # max. mag diff to identify close neighbors
    xcolname, ycolname, fluxcolname = 'x_fit', 'y_fit', 'flux_fit'
    imax = 1000     # intensity of center source

    for c in (xcolname, ycolname, fluxcolname, 'flags'):
        if (not c in sources.colnames):
            print('ERROR: missing column {}'.format(c), file=sys.stderr)
            exit(-1)

    tlen,ta,ctr = trail
    # TODO: width of trail mask shall be between 2*fwhm+2 and 5*fwhm+3 depending on tlen/fwhm
    
    # create trail "mask" image
    trailwidth = 2.5*fwhm + 3
    trailimg=mktrailmask(trail, trailwidth) # square image mask, trail=1, bg=0
    #writeimage(['-fmt', 'fits', trailimg, sname + '.trailimg.fits'])
    # create image of size 2x maskimg
    imsize = 2*trailimg.width
    # add center psf star trail (trailimg) at center using intensity 1000
    left=int(trailimg.width/2)
    top=int(trailimg.width/2)
    srcimg=pyvips.Image.black(imsize, imsize).insert(trailimg.linear(imax,0), left, top)

    # number of brigthest sources to check at most
    nmax = int(1.5*nbright+0.5)

    # filter previously defined psf sources or brightest sources
    sources.sort(fluxcolname, reverse=True)
    if ('ispsf' in sources.colnames):
        psfsources = sources[sources['ispsf']]
    else:
        # choose brightest non-flagged sources
        psfsources = sources[sources['flags']==0][0:nmax]
    
    # find suitable trail sources
    isok = np.zeros(len(psfsources), dtype=bool)
    #brightmaglim = psfsources['mag'][0] + dmag
    for i in range(len(psfsources)):
        # exclude trails which have very bright neighbors within psfsize/2+fwhm
        x, y = psfsources[xcolname][i], psfsources[ycolname][i]
        psfid = str(psfsources['uid'][i])
        if ('src_id' in psfsources.colnames): psfid = str(psfsources['src_id'][i])

        if ('issat' in sources.colnames):
            s=sources[(sources['mag'] < psfsources['mag'][0]) | sources['issat']]
        else:
            s=sources[(sources['mag'] < psfsources['mag'][0])]
        s['dx'] = s[xcolname] - x
        s['dy'] = s[ycolname] - y
        s['inx'] = abs(s['dx']) < imsize/2+fwhm
        s['iny'] = abs(s['dy']) < imsize/2+fwhm
        s=s[s['inx'] & s['iny'] & (abs(s['dx'])>0) & (abs(s['dy'])>0)]
        if (len(s) > 0):
            continue

        # exclude trails with bright neighbors overlapping inner part of trail
        if ('issat' in sources.colnames):
            s=sources[(sources['mag'] < psfsources['mag'][i] + dmag) | sources['issat']]
        else:
            s=sources[(sources['mag'] < psfsources['mag'][i] + dmag)]
        s['dx'] = s[xcolname] - x
        s['dy'] = s[ycolname] - y
        s['inx'] = abs(s['dx']) < imsize/2+2*fwhm
        s['iny'] = abs(s['dy']) < imsize/2+2*fwhm
        s=s[s['inx'] & s['iny']]
        if (len(s) > 1):
            sumimg = pyvips.Image.black(imsize, imsize)
            for j in range(len(s)):
                # add neighbor star trails (trailimg with offset position)
                dx = int(s['dx'][j] + trailimg.width/2)
                dy = int(s['dy'][j] + trailimg.width/2)
                nbimg = pyvips.Image.black(imsize, imsize).insert(trailimg, dx, dy, expand=False)
                sumimg = sumimg + nbimg
            # check for overlap (max intensity > imax)
            if (sumimg.max() > imax+1):
                #writeimage(['-fmt', 'fits', sumimg, sname + '.notrail_' + psfid + '.fits'])
                continue
        isok[i] = True
        if (sum(isok) >= nbright): break
    return(psfsources[isok])


def mask_stars(data, postab, bsize):
    """
    mask out data which are not close to positions provided by postab
    data are kept near positions within box of bsize*bsize, anything
    outside of those areas is set to zero
    
    data - 2D ndarray
    postab - table containing x-, y-coordinates in first two columns
    returns: modified data array
    
    TODO: maybe add some noise to outside data to avoid false sources in
        subsequent DAOPhotPSFPhotometry
    """
    mask = data * 0
    i=0
    for row in np.array(postab):
        x, y = row[0], row[1]
        x1, y1 = math.floor(x - bsize/2), math.floor(y - bsize/2)
        if (x1<0): x1=0
        if (y1<0): y1=0
        x2, y2 = math.ceil(x + bsize/2), math.ceil(y + bsize/2)
        if (x2>data.shape[1]): x2=data.shape[1]
        if (y2>data.shape[0]): y2=data.shape[0]
        #if(i<2): print('x={:d}:{:d}  y={:d}:{:d}'.format(x1,x2,y1,y2))
        mask[y1:y2, x1:x2] = 1
        i=i+1
    return(data * mask)


def flag_bad_sources(phottab, cropgeom, maxfluxerr=20, maxposerr=3, starpositions=None, maxstardist=1):
    """
    flag false/uncertain detections in photometry table
    optionally flag stars at given positions as well
    
    phottab       - PSF photometry output table, required columns: x_0_unc
                    y_0_unc flux_fit flux_unc
    cropgeom      - geometry of valid image area: xoff, yoff, width, height
    maxfluxerr    - flux uncertainty in percent of flux
    maxposerr     - position uncertainty in pixel
    starpositions - table containing x,y coordinates of star positions
    maxstardist   - max distance from position to skip sources
    """
    # add flags column if it does not exist
    if ('flags' in phottab.colnames):
        print('WARNING: flag_bad_sources resets existing column flags', file=sys.stderr)
    phottab['flags'] = 0
    
    # outside valid image area
    margin = 3
    xmin, xmax = cropgeom[0]+margin, cropgeom[0]+cropgeom[2]-margin
    ymin, ymax = cropgeom[1]+margin, cropgeom[1]+cropgeom[3]-margin
    mask = (phottab['x_fit'] <= xmin) | (phottab['x_fit'] >= xmax)
    mask = mask | (phottab['y_fit'] <= ymin) | (phottab['y_fit'] >= ymax)
    phottab['flags'][mask] += 1
    
    # large flux error or unknown flux error
    fluxpercent = 100 * phottab['flux_unc'] / abs(phottab['flux_fit'])
    mask = (fluxpercent > maxfluxerr) | (phottab['flux_unc'] == 0)
    phottab['flags'][mask] += 2

    # large position error or unrealistic small position error (near 0)
    if (maxposerr > 0):
        poserr = np.sqrt(phottab['x_0_unc']**2 + phottab['y_0_unc']**2)
        mask = (poserr > maxposerr) | (poserr < 0.000001)
        phottab['flags'][mask] += 4
    
    # flag stars near starpositions
    if (starpositions is not None):
        mask = mask & False
        for pos in np.array(starpositions):
            d = np.sqrt((phottab['x_fit'] - pos[0])**2 + (phottab['y_fit'] - pos[1])**2)
            mask = mask | (d<maxstardist)
        phottab['flags'][mask] += 8
    return(phottab)


def mkcutouts(stars, srctab, title, pngfilename=None, shownearby=False, showplot=False):
    '''
    show star cutouts
    stars   - EPFSStars created by extract_stars
    srctab  - table containing id,x,y of original sources
    '''
    ncols = 10
    smult = 1.6
    nstars = stars.n_all_stars
    nrows = int(nstars/ncols + 0.99)
    bsize = stars[0].data.shape[0]  # cutout window width/height
    lognorm = simple_norm(stars[0].data, 'log', percent=95.0)
    origin='upper'  # origin used for plotting images

    fig, ax = plt.subplots(nrows=nrows, ncols=ncols, figsize=(smult*ncols, smult*nrows),
        layout="constrained", sharex=True, sharey=True)
    fig.get_layout_engine().set(w_pad=0.02, h_pad=0.02)
    fig.suptitle(title)
    ax = ax.ravel()
    #for i in range(np.min(nrows * ncols, len(stars))):
    maxoff = 0.6*bsize    # max dx/dy of source from center
    mosaic = np.zeros((nrows*bsize, ncols*bsize), stars[0].data.dtype)
    for i in range(nrows*ncols):
        if (i<len(stars)):
            # mosaic
            mrow0=int(i/ncols)*bsize
            mcol0=(i-int(i/ncols)*ncols)*bsize
            mosaic[mrow0:(mrow0+bsize), mcol0:(mcol0+bsize)] = stars[i].data
            
            # sub-image of figure
            ax[i].imshow(stars[i], norm=lognorm, origin=origin, cmap='viridis')
            
            # find nearby sources belonging to this star cutout
            #s = srctab[nearby_mask]
            dx = srctab.columns[1] - stars.center_flat[i, 0]
            dy = srctab.columns[2] - stars.center_flat[i, 1]
            centermask = (dx == 0) & (dy == 0)
            centerid = srctab[centermask].columns[0][0]
            ax[i].set_title(centerid, fontsize=10)            
            nearby = srctab[(abs(dx)<maxoff) & (abs(dy)<maxoff) & (~ centermask)]
            #s = s[(dx<maxoff) & (dy<maxoff)]
            if (shownearby) & (len(nearby)>0):
                # note: this takes really long ...
                x = nearby.columns[1] - stars.center_flat[i, 0] + bsize/2
                y = nearby.columns[2] - stars.center_flat[i, 1] + bsize/2
                xypos=np.transpose((x, y))
                aps = CircularAperture(xypos, r=3)
                aps.plot(ax=ax[i], color='red', lw=1.0)
        else:
            ax[i].imshow(stars[0].data*0-100, norm=lognorm, origin=origin, cmap='viridis')
    if (pngfilename is not None):
        plt.savefig(pngfilename)
    mosaicfilename = os.path.splitext(pngfilename)[0] + '.fits'
    writeimage(['-fmt', 'fits', np2v(mosaic), mosaicfilename])
    if showplot: plt.show(block=False)


def buildepsf(data, psfsources, xcolname, ycolname, psfsize, psfsample, fwhm, do_center,
    outprefix, istrail=False, iteration=0, do_show_plots=True):
    # extract subimages around psf stars
    nddata = NDData(data=data)
    stars = extract_stars(nddata, Table(psfsources[xcolname, ycolname], names=('x','y')), size=psfsize)
    if (len(stars) != len(psfsources)):
        print('ERROR: number of star cutouts does not match psfsources')
        exit(1)

    # create plot of cutouts
    if (not istrail):
        plottitle="PSF" + str(iteration) + " Stars"
        pngfilename=outprefix + '.psfstars' + str(iteration) + ".png"
    else:
        plottitle="Trail" + str(iteration) + " Stars"
        pngfilename=outprefix + '.trailstars' + str(iteration) + '.png'
    if ('src_id' in psfsources.colnames): idcolname='src_id'
    else:
        if ('uid' in psfsources.colnames): idcolname='uid'
        else: idcolname='id'
    mkcutouts(stars, psfsources[(idcolname, xcolname, ycolname)], plottitle,
        pngfilename=pngfilename, shownearby=False, showplot=do_show_plots)

    sigmaclip=SigmaClip(sigma_lower=3, sigma_upper=3, maxiters=5, cenfunc='median', stdfunc='std', grow=False)
    normrad = fwhm + 1
    if (do_center):
        epsf_builder = EPSFBuilder(oversampling=psfsample, maxiters=10, progress_bar=False,
            sigma_clip=sigmaclip, norm_radius=normrad, center_accuracy=0.01)
    else:
        epsf_builder = EPSFBuilder(oversampling=psfsample, maxiters=5, progress_bar=False,
            sigma_clip=sigmaclip, norm_radius=normrad, recentering_maxiters=0, center_accuracy=2*fwhm)
    epsf, fitted_stars = epsf_builder(stars)
    if do_show_plots:
        plt.figure()
        plt.title('PSF' + str(iteration))
        norm = simple_norm(epsf.data, 'log', percent=99.0)
        plt.imshow(epsf.data, norm=norm, origin=origin, cmap='viridis')
        plt.colorbar()
        plt.show(block=False)

    if (not istrail):
        fitsfilename = outprefix + '.psf' + str(iteration) + ".fits"
    else:
        fitsfilename = outprefix + '.trail' + str(iteration) + ".fits"
    writeimage(['-fmt', 'fits', np2v(epsf.data), fitsfilename])

    # reset background and apply trail mask
    if (istrail):
        # bg statistics
        trail=istrail
        # TODO: trail width should be larger if the trail is short
        #  maximum is subsize-4
        trailwidth = 4*fwhm + 4
        print('trailwidth={:.1f}'.format(trailwidth))
        trailmask=mktrailmask(np.multiply(trail,(psfsample,1,1)), psfsample*trailwidth, imsize=epsf.data.shape[0]) # square image mask, trail=1, bg=0
        if (do_center):
            fitsfilename = outprefix + '.trailmask' + str(iteration) + ".fits"
            writeimage(['-fmt', 'fits', trailmask, fitsfilename])
        mvalues = np.ma.array(epsf.data, mask=v2np(trailmask)>0).reshape(-1)
        bgval = np.median(mvalues.compressed())
        bgsd = np.std(mvalues.compressed())
        print('psf stats: bgmedian={:.6f} bgstddev={:.6f}'.format(bgval, bgsd))
        epsf = EPSFModel(np.multiply(epsf.data-bgval, v2np(trailmask)), oversampling=psfsample)
    return(epsf)

        
def remove_nearby_stars(data, sources, psfsources, xcolname, ycolname, fluxcolname, psfsize, subsize,
    separation, threshold, fwhm, epsf, fitsize, magzero, istrail=False, isrefband=True):

    debug=False
    if debug:
        print('sources: ' + str(sources.colnames))
        print('psfsources: ' + str(psfsources.colnames))
    # find sources near psf stars
    nearby_mask = np.zeros(len(sources), dtype=bool)   # nearby source = True
    maxoff = 0.8*psfsize + fwhm
    for i in range(len(psfsources)):
        dx = abs(sources[xcolname] - psfsources[xcolname][i])
        dy = abs(sources[ycolname] - psfsources[ycolname][i])
        nearby_mask = nearby_mask | ((dx<maxoff) & (dy<maxoff))
    if ('flags' in sources.colnames):
        nearby_mask = nearby_mask & (sources['flags']==0)

    if not istrail:
        daoaprad=0.8*fwhm+1
        daocycles=1
        # mask image data to speed up DAOPhotPSFPhotometry
        data_masked = mask_stars(data, psfsources[[xcolname, ycolname]], 1.6*psfsize)
        phottab = psfphot(data_masked, sources[nearby_mask], xcolname, ycolname, fluxcolname, psfsize, subsize,
            separation, threshold, fwhm, epsf, fitsize, daocycles, magzero, isrefband=isrefband)
        # flag sources close to psfsources
        if isrefband:
            for psfid in psfsources['id']:
                phottab['flags'][phottab['src_id'] == psfid] += 8
        else:
            for psfid in psfsources['uid']:
                phottab['flags'][phottab['uid'] == psfid] += 8
        print('number of nearby sources = {:d}'.format(len(phottab[phottab['flags']==0])))
        if debug & isrefband:
            del phottab.meta['version']
            phottab.write('x.tmp_nearby_tab.fits', format='fits', overwrite=True)
        # TODO: sources near psf stars maybe over-corrected
        #   - evaluate phottab to exclude bright sources near psfpositions
    else:
        # apply fluxratio trailpsf/starpsf
        values = epsf.data.reshape(-1)
        sumflux = np.sum(values)
        psfflux=sources.meta['PSFFLUX']
        fluxratio=sumflux/psfflux
        print('divide {} by fluxratio={:.3f}'.format(fluxcolname, fluxratio))
        phottab = sources[nearby_mask]
        for psfid in psfsources['id']:
            phottab['flags'][phottab['id'] == psfid] += 8
        phottab[fluxcolname] = phottab[fluxcolname] / fluxratio
    resid = subtract_psf(data, epsf, phottab[phottab['flags']==0], subshape=(subsize,subsize))
    if debug & isrefband:
        outfits='x.resid_stars.fits'
        if (istrail): outfits='x.resid_trails.fits'
        writeimage(['-fmt', 'fits', '-32', np2v(resid), outfits])
    return(resid)


def psfphot(data, sources, xcolname, ycolname, fluxcolname, psfsize, subsize,
    separation, threshold, fwhm, epsf, fitsize, daocycles, magzero, isrefband=True):
    # run precise PSF photometry
    print('running psfphot (daocycles={:d})'.format(daocycles))
    daoaprad=0.8*fwhm+1
    if (isrefband):
        # keep all input columns (created by DAOStarFinder)
        xydata=sources
        xydata.rename_column('id', 'src_id')
    else:
        # keep only required columns (coords and flux) and column to identify sources
        xydata=sources[sources['flags']==0][('uid', xcolname, ycolname, fluxcolname, 'flags')]
        xydata.rename_column(fluxcolname, 'flux_0')
    xydata.rename_column(xcolname, 'x_0')
    xydata.rename_column(ycolname, 'y_0')
    if (not isrefband):
        # use fixed star positions from refband
        print('using fixed star positions')
        epsf.x_0.fixed = True
        epsf.y_0.fixed = True
    # choose TRFLSQFitter which is default in newer photutils
    psfphot = DAOPhotPSFPhotometry(separation, threshold, fwhm, epsf, fitsize,
        fitter=TRFLSQFitter(), aperture_radius=daoaprad, subshape=subsize, niters=daocycles)
    phot = psfphot.do_photometry(data, init_guesses=xydata)

    # restore input table x/y column names for photometry of refband
    if (isrefband):
        phot.rename_column('x_0', xcolname)
        phot.rename_column('y_0', ycolname)
    #print('phot colnames=' + str(phot.colnames))

    # build new id column containing unique values
    if (isrefband):
        phot.sort(('iter_detected', 'group_id', 'id'))
        phot['uid'] = np.arange(1,len(phot)+1)

    # clean/check sources
    n = len(phot)
    if (isrefband):
        maxposerr = 0.5*fwhm
        maxfluxerr = 30
    else:
        maxposerr=0
        maxfluxerr = 40
    valid_geometry = (psfsize/2, psfsize/2, data.shape[1]-psfsize, data.shape[0]-psfsize)
    phot = flag_bad_sources(phot, valid_geometry, maxfluxerr=maxfluxerr, maxposerr=maxposerr)
    nbad = len(phot[phot['flags'] > 0])
    print('flagged {:d} spurious detections out of {:d}'.format(nbad,n), flush=True)

    # compute mag and magerr for all sources
    if (('mag' in phot.colnames) and ('src_mag' not in phot.colnames)):
        phot.rename_column('mag', 'src_mag')
    phot['mag'] = 99.
    phot['magerr'] = 99.
    mask = (phot['flags'] == 0) & (phot['flux_fit'] > 0)
    phot['mag'][mask] = magzero - 2.5/np.log(10) * np.log(phot['flux_fit'][mask])
    fhigh = phot['flux_fit']+phot['flux_unc']/2
    flow = phot['flux_fit']-phot['flux_unc']/2
    flow[flow<0] = 1/10**6
    phot['magerr'][mask] = -2.5/np.log(10) * np.log(flow[mask]/fhigh[mask])
    return(phot)


def psfextract(param):
    '''
    extract and subtract PSF from image
    notes:
    - if costack is not provided then extract star PSF from ststack
    - if phottable is provided as additional parameter, then take initial
      object positions from this table (e.g. for R/B bands in RGB image we
      should provide phottable as created from G band)
    - If both ststack and costack are provided then extract star trail PSF from
      costack. Both phottable and trail parameters are required. The phottable
      must have been created from star stack matching the same color band.
    '''
    syntax='syntax: psfextract [-v] [-R|G|B] [-r rlim] [-n nbright] [-f fwhm] [-m magzero] [-s saturation] [-nophot] sname ststack [costack] xcenter ycenter [phottable] [trail_length,angle,ctrfrac]'
    
    
    #########################################
    #   settings
    #########################################
    
    # default values, maybe overwritten by command line options
    verbose=False
    color='G'
    saturation=55000    # saturation level
    fwhm=3.5        # approximate fwhm of stars
    magzero=26.3    # arbitrary value
    rlim=6
    nbright=60
    do_psf_phot=True

    # fixed settings
    outdir='psf'
    origin='upper'  # origin used for plotting images
    bsize=20        # box width used by bg estimator
    # settings for ePSF builder
    do_remove_nearby_sources=True
    psfsize=31      # min. box size of star cutout window
    psfsample=2     # PSF upsampling factor
    # normrad=fwhm+1 # aperture radius used for normalizing flux
    # settings for PSF photometry
    do_basic_psfphot=False  # if set then use (~2x) faster BasicPSFPhotometry
                    # instead of DAOPhotPSFPhotometry
    do_init_guesses=True   # if set then use initial positions
    # separation=2*fwhm+1 # max separation of stars solved as a group
    snthres=4       # threshold used by DAOPhotPSFPhotometry
    daocycles=2     # number of DAOPhotPSFPhotometry iterations (at refband)
    # daoaprad=0.8*fwhm+1 # aperture radius used to measure initial flux in DAOPhotPSFPhotometry


    # show/hide plot windows
    do_show_plots=False
    do_plot_segmentimage=False
    do_plot_sources=False
    do_plot_stars0=True
    do_plot_psf0=True
    do_plot_stars1=True
    do_plot_psf1=True
    do_plot_residuals=False


    #########################################
    #   command line options and parameters
    #########################################
    
    # default values of optional parameters
    trail=None
    costackfilename=None
    photcatfilename=None

    for i in range(len(param)):
        if(param[0]=='-h'):
            print(syntax, file=sys.stderr)
            exit(1)
        if(param[0]=='-v'):
            verbose=True
            del param[0]
        if(param[0]=='-R'):
            color='R'
            del param[0]
        if(param[0]=='-G'):
            color='G'
            del param[0]
        if(param[0]=='-B'):
            color='B'
            del param[0]
        if(param[0]=='-nophot'):
            do_psf_phot=False
            del param[0]
        if(param[0]=='-r'):
            rlim=float(param[1])
            del param[0:2]
        if(param[0]=='-n'):
            nbright=int(param[1])
            del param[0:2]
        if(param[0]=='-f'):
            fwhm=float(param[1])
            del param[0:2]
        if(param[0]=='-m'):
            magzero=float(param[1])
            del param[0:2]
        if(param[0]=='-s'):
            saturation=float(param[1])
            del param[0:2]

    if (len(param) != 4 and len(param) != 5 and len(param) != 7):
        print(syntax, file=sys.stderr)
        exit(-1)
    
    sname=param[0]
    ststackfilename = param[1]
    if (len(param) in [4, 5]):
        xcenter=float(param[2])   # image coordinates of crop center (top-left corner is (0,0))
        ycenter=float(param[3])
    if (len(param) == 5):
        photcatfilename = param[4]
    if (len(param) == 7):
        costackfilename = param[2]
        xcenter=float(param[3])   # image coordinates of crop center (top-left corner is (0,0))
        ycenter=float(param[4])
        photcatfilename = param[5]
        trail=param[6]
    
    # check files
    for fname in (ststackfilename, costackfilename, photcatfilename):
        if (fname and (not os.path.exists(fname))):
            print('ERROR: file ' + fname + ' does not exist', file=sys.stderr)
            exit(-1)

    # check format of trail parameter
    if trail:
        try:
            tlen,ta,ctr = [float(s) for s in trail.split(',')]
            trail=(tlen, ta, ctr)
        except:
            print('ERROR: wrong format of trail parameter (must be length,angle,ctrfrac)', file=sys.stderr)
            exit(-1)

    # in case of RGB image determine image band to process
    band, refband = 0, 0
    ststackimg = pyvips.Image.new_from_file(ststackfilename)
    if (ststackimg.bands == 3):
        refband=1
        band='RGB'.find(color)
        if ((color != 'G') and (not photcatfilename)):
            print('ERROR: photcat filename is missing (required for color B/R)', file=sys.stderr)
            exit(-1)
    if ((band == refband) and (trail is None) and (photcatfilename is not None)):
        print('ERROR: providing photcat file is not allowed', file=sys.stderr)
        exit(-1)

    # setting and checking table column names
    if photcatfilename:
        # using input table previousely created by psfextract (mostly based on
        # results of PSFPhotometry)
        idcolname, xcolname, ycolname, fluxcolname = 'uid', 'x_fit', 'y_fit', 'flux_fit'

        try:
            t=Table.read(photcatfilename)
        except:
            print('ERROR: photcat is not a FITS table', file=sys.stderr)
            exit(-1)
        for c in (idcolname, xcolname, ycolname, fluxcolname):
            if (not c in t.colnames):
                print('ERROR: missing column {} in photcat'.format(c), file=sys.stderr)
                exit(-1)
    else:
        # table created by DAOFinder later on
        idcolname, xcolname, ycolname, fluxcolname = 'id', 'xcentroid', 'ycentroid', 'flux'
    

    #########################################
    #   start processing
    #########################################
    
    datestring = datetime.datetime.now().strftime("%Y-%m-%d %X")
    print('#### psfextract v' + str(VERSION) + ', ' + datestring)

    doFind=True
    if photcatfilename: doFind=False
    bandinfo=""
    if (ststackimg.bands == 3): bandinfo=' (' + color + ' band)'
    if (not trail):
        print('{}: extracting star PSF{}'.format(sname, bandinfo))
    else:
        print('{}: extracting trail PSF{}'.format(sname, bandinfo))
    print('photcat={} xcol={} trail={} doFind={} doPhot={}'.format(
        str(photcatfilename), xcolname, str(trail), str(doFind), str(do_psf_phot)))
    #print('#### all checks passed, program stopped (debugging)', file=sys.stderr)
    #exit(-1)

    start_time = time.time()
    
    # DAOPSFPhotometry cycles
    if (band != refband): daocycles=1

    # reading input images
    # note: ststackimg has been loaded previously (see checkings)
    #ststackimg = pyvips.Image.new_from_file(ststackfilename)
    if trail:
        costackimg = pyvips.Image.new_from_file(costackfilename)

    # creating directory for output files
    if not os.path.exists(outdir): os.makedirs(outdir)
    outprefix=outdir + "/" + sname + '.' + str(band)
    
    # determine window sizes
    if (fwhm>5): psfsize = psfsize + 2*int(0.8*fwhm-3)
    if (not trail):
        fitsize=int(0.8*fwhm + 1.3)*2+1  # box size used for psf fitting, odd value
    else:
        fitsize=int(0.8*fwhm + tlen + 2)*2+1
        psfsize = 1 + 2 * int((psfsize + 1.3*tlen + 1)/2)
    subsize=2*int(0.9*psfsize/2)+1
    print('rlim={} fwhm={} psfsize={:d} subsize={:d} fitsize={:d}'.format(str(rlim), str(fwhm), psfsize, subsize, fitsize), flush=True)

    # set distances/radii depending on fwhm
    normrad=fwhm+1      # aperture radius used for normalizing flux
    separation=2*fwhm+1 # max separation of stars solved as a group
    daoaprad=0.8*fwhm+1 # aperture radius used to measure initial flux in DAOPhotPSFPhotometry
    print('separation={:.1f} normrad={:.1f} daoaprad={:.1f}'.format(separation, normrad, daoaprad))

    # determine crop region
    imgwidth=ststackimg.width
    imgheight=ststackimg.height
    rmax = math.sqrt(imgwidth**2 + imgheight**2) * rlim/100
    left, right = int(xcenter - rmax - psfsize), int(xcenter + rmax + psfsize)
    top, bottom = int(ycenter - rmax - psfsize), int(ycenter + rmax + psfsize)
    if (left < 0): left=0
    if (right >= imgwidth): right=imgwidth-1
    if (top < 0): top=0
    if (bottom >= imgheight): bottom=imgheight-1
    xcenter = xcenter - left
    ycenter = ycenter - top
    cropwidth =  right-left+1
    cropheight = bottom-top+1
    print('rmax={:.0f}; crop left={:d} top={:d} width={:d} height={:d}'.format(rmax, left,top,cropwidth,cropheight))
    

    #########################################
    #   background subtraction
    #########################################
    
    # crop image (single band) and subtract background
    stcropimg = ststackimg.crop(left, top, cropwidth, cropheight)[band]
    if (not trail):
        cropimg = stcropimg
    else:
        cropimg = costackimg.crop(left, top, cropwidth, cropheight)[band]
    sd, bgdata = background(stcropimg, bsize, do_plot_segmentimage=do_plot_segmentimage)
    data = v2np(cropimg) - bgdata
    if (not trail):
        bgimg = pyvips.Image.black(imgwidth, imgheight).insert(np2v(bgdata), left, top)
        writeimage(['-fmt', 'fits', '-32', bgimg, outprefix + '.bg.fits'])


    #########################################
    #   select PSF stars
    #########################################

    # find sources
    if not photcatfilename:
        # find sources in input image
        # note: on defocused images it may find many spurious sources (~500%)
        finder = DAOStarFinder(fwhm=fwhm, threshold=snthres*sd, exclude_border=True)
        sources = finder(data)
        # adding back crop offsets before witing fits table
        outtab = Table(sources)
        outtab[xcolname] += left
        outtab[ycolname] += top
        del outtab.meta['version']
        #print(outtab.meta['version']['photutils'])
        outtab.write(outdir + "/" + sname + '.sources.fits', format='fits', overwrite=True)
    else:
        # read sources from user provided table (result from previous psfextract call)
        sources = Table.read(photcatfilename)
        if ('flags' in sources.colnames):
            # only consider real sources
            sources = sources[sources['flags']==0]
        # subtract crop offset
        sources[xcolname] -= left
        sources[ycolname] -= top
        
    print('number of sources: {:d}'.format(len(sources)), flush=True)

    # filter suitable psf sources
    sources.sort(fluxcolname, reverse=True)
    if not trail:
        if (band == refband):
            psfsources = filterpsfsources(sources, cropwidth, psfsize, saturation, fwhm, nbright)
            fitsfilename = outdir + "/" + sname + '.psfsources.fits'
            regfilename = outdir + "/" + sname + '.psfsources.reg'
        else:
            psfsources = sources[sources['ispsf']]
            fitsfilename = None
            regfilename = None
    else:
        psfsources = filtertrailedsources(sources, trail, fwhm, nbright)
        fitsfilename = outdir + "/" + sname + '.trailsources.fits'
        regfilename = outdir + "/" + sname + '.trailsources.reg'
    print('number of psf sources: {:d}'.format(len(psfsources)), flush=True)
    # saving psfsources
    # columns are same as sources
    # coordinates in saved files refer to input image coordinates
    if fitsfilename:
        outtab = Table(psfsources)
        outtab[xcolname] += left
        outtab[ycolname] += top
        if ('version' in outtab.meta):
            del outtab.meta['version']
        outtab.write(fitsfilename, format='fits', overwrite=True)
    if regfilename:
        xy2reg(psfsources, regfilename, xadd=left, yadd=top, yflip=imgheight)

    # show image and bright detections
    lognorm = simple_norm(data, 'log', percent=99.0)
    psfpositions=np.transpose((psfsources[xcolname], psfsources[ycolname]))
    apertures = CircularAperture(psfpositions, r=4.0)
    if do_plot_sources:
        plt.figure()
        #plt.margins(0)
        plt.subplots_adjust(bottom=0.05, top=0.95, left=0.05, right=0.95)
        plt.title('Source detections')
        # show some source positions
        for i in range(5):
            print('{:d} {:6.1f} {:6.1f} {:4.1f}'.format(i, psfsources[i][xcolname], psfsources[i][ycolname], psfsources[i]['mag']))
        plt.imshow(data, norm=lognorm, origin=origin, cmap='viridis')
        apertures.plot(color='red', lw=1.5, alpha=0.5)
        if do_show_plots: plt.show(block=False)


    #########################################
    #   build effective PSF
    #########################################
    
    do_center = (not trail) and (band==refband)
    epsf = buildepsf(data, psfsources, xcolname, ycolname, psfsize, psfsample, fwhm, do_center,
        outprefix, istrail=trail, iteration=0, do_show_plots=do_show_plots)
    print('initial psf extraction finished in {:.2f}s'.format(time.time() - start_time), flush=True)

    #if do_show_plots: plt.show()
    #exit(0)
    

    if do_remove_nearby_sources:
        print('removing sources near psf stars ...', flush=True)
        resid = remove_nearby_stars(data, sources, psfsources, xcolname, ycolname, fluxcolname, psfsize, subsize,
            separation, snthres*sd, fwhm, epsf, fitsize, magzero, istrail=trail, isrefband=band==refband)

        # psf extraction on image where nearby stars are removed
        print('building improved PSF ...', flush=True)
        do_center = (not trail) and (band==refband)
        #print(psfsources.colnames)
        #print(xcolname, ycolname)
        epsf = buildepsf(resid, psfsources, xcolname, ycolname, psfsize, psfsample, fwhm, do_center,
            outprefix, istrail=trail, iteration=1, do_show_plots=do_show_plots)
        print('improved psf extraction finished in {:.2f}s'.format(time.time() - start_time), flush=True)

    # statistics on psf data
    values = epsf.data.reshape(-1)
    sumflux = np.sum(values)
    maxflux = np.max(values)
    if (not trail):
        # determine magcorr to be applied on magnitudes during precise psf photometry
        # this is required as the flux measurement in DAOPhotPSFPhotometry uses a
        # small photometric aperture (normrad)
        photmask=mktrailmask((0,1,1), psfsample*normrad*2+0.5, imsize=epsf.data.shape[0])
        if (band==refband):
            writeimage(['-fmt', 'fits', photmask, outdir + "/" + sname + '.photmask1.fits'])
        mvalues = np.ma.array(epsf.data, mask=v2np(photmask)==0).reshape(-1)
        ratio = sumflux/np.sum(mvalues.compressed())  # >1
        magcorr = 2.5 / np.log(10) * np.log(ratio)  # >0
        print('psf stats: sum={:.3f} max={:.4f} magcorr={:.3f}'.format(sumflux,maxflux,magcorr))
    else:
        # bg statistics
        trailmask=mktrailmask(np.multiply(trail,(psfsample,1,1)), psfsample*5*fwhm+1, imsize=epsf.data.shape[0]) # square image mask, trail=1, bg=0
        if (band==refband):
            writeimage(['-fmt', 'fits', trailmask, outdir + "/" + sname + '.trailmask1.fits'])
        mvalues = np.ma.array(epsf.data, mask=v2np(trailmask)>0).reshape(-1)
        bgval = np.median(mvalues.compressed())
        bgsd = np.std(mvalues.compressed())
        print('psf stats: sum={:.3f} max={:.4f} bgmedian={:.6f} bgstddev={:.6f}'.format(sumflux, maxflux, bgval, bgsd))

        # determine fluxratio trailpsf/starpsf
        # this ratio must be applied to the trail PSF before subtracting star trails
        psfflux=sources.meta['PSFFLUX']
        normarea = 3.1416*(psfsample*normrad)**2
        #normarea = epsf.data.size
        fluxratio=(sumflux-bgval*normarea)/psfflux
        print('fluxratio={:.3f}'.format(fluxratio))

        # subtract background and mask the trail
        epsf = EPSFModel((epsf.data - bgval)*v2np(trailmask), oversampling=psfsample)

    plt.figure()
    plt.title('PSF Histogram')
    plt.hist(values[values < 0.0005], bins=100)
    if do_show_plots: plt.show(block=False)


    #if do_show_plots: plt.show()
    #exit(0)


    #########################################
    #   PSF photometry
    #########################################

    if (not trail) and do_psf_phot:
        print('running PSF photometry ...', flush=True)
        magzero = magzero - magcorr
        phot = psfphot(data, sources, xcolname, ycolname, fluxcolname, psfsize, subsize,
            separation, snthres*sd, fwhm, epsf, fitsize, daocycles, magzero, isrefband=band==refband)
    
        # identify saturated sources
        # identify psf sources
        if (band==refband):
            if ('peak' in phot.colnames):
                phot['issat'] = phot['peak'] > saturation
                phot['issat'][phot['peak'].mask] = False
                # TODO: measure brightest sources
                #   choose 1% of non-saturated stars
                #   start mesuring from brightest one in box ~1.5*fwhm
                #   stop if flux < 0.8*flux_of_last_saturated_star
                phot['ispsf'] = False
                for sid in psfsources['id']:
                    phot['ispsf'][phot['src_id'] == sid] = True
            else:
                # TODO: analyze sources and psfsources and find closest match in phot
                #   to identify saturated sources and psf sources
                print('WARNING: unable to add columns issat and ispsf')
                pass
    
        # add some metadata (will be written to FITS header)
        phot.meta['PSFFLUX'] = sumflux
        phot.meta['PSFMCOR'] = magcorr
        phot.meta['PHOTVERS'] = phot.meta['version']['photutils']

        # add crop offsets to xy coordinates to match input image
        # before writing fits table
        outtab = Table(phot)
        outtab['x_fit'] += left
        outtab['y_fit'] += top
        del outtab.meta['version']
        outtab.write(outdir + "/" + sname + '.phot.' + str(band) + '.fits', format='fits', overwrite=True)
        xy2reg(phot, outdir + "/" + sname + '.phot.' + str(band) + '.reg', xadd=left, yadd=top, yflip=imgheight)
        if (band == refband):
            phot2dat(phot, outdir + "/" + sname + '.starphot.' + str(band) + 'dat', xadd=left, yadd=top)
            if ('ispsf' in phot.colnames):
                phot2dat(phot[phot['ispsf']==True][0:30], outdir + "/" + sname + '.psfphot' + str(band) + '.dat', xadd=left, yadd=top)
        print('psf photometry finished in {:.2f}s'.format(time.time() - start_time), flush=True)

    # TODO: on any other image band:
    # extract PSF
    # remove nearby sources
    # extract improved PSF
    # run BasisPSFPhotometry using fixed positions provided by phot (cleaned)


    #########################################
    #   subtract PSF
    #########################################

    # create residual image using positions, fluxes and epsf
    if not trail:
        if not do_psf_phot:
            print('WARNING: psf photometry has been skipped')
            print('program finished in {:.2f}s'.format(time.time() - start_time))
            exit(1)
        print('subtracting stars ...')
        phottab = phot
    else:
        print('subtracting star trails ...', flush=True)
        phottab = sources
        phottab['flux_fit'] = phottab['flux_fit'] / fluxratio
    #subdata = subtract_psf(data+bgdata, epsf, phottab[phottab['flags']==0]['x_fit','y_fit','flux_fit'], subshape=(subsize,subsize))
    subdata = subtract_psf(data+bgdata, epsf, phottab[phottab['flags']==0], subshape=(subsize,subsize))
    #subdata = subtract_psf(data, epsf, phot)
    subimg = np2v(subdata)
    #skyimg = cropimg - subimg
    #writeimage(['-fmt', 'fits', '-32', skyimg, outdir + "/" + sname + '.skymodel.' + str(band) + '.fits'])
    if not trail:
        outimg = ststackimg[band].insert(subimg, left, top)
        writeimage(['-fmt', 'fits', '-32', outimg, outprefix + '.stsub.fits'])
    else:
        outimg = costackimg[band].insert(subimg, left, top)
        writeimage(['-fmt', 'fits','-32', outimg, outprefix + '.cosub.fits'])

    print('program finished in {:.2f}s'.format(time.time() - start_time), flush=True)


    # leave windows open
    if do_show_plots: plt.show(block=True)


if (__name__ == "__main__"):
    psfextract(sys.argv[1:])
