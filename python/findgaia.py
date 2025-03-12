#!/usr/bin/python3

import sys
import os
import math
import numpy as np

import astropy.units as u
from astropy.io import fits
from astropy.wcs import WCS, WCSHDR_CD00i00j, WCSHDR_PROJPn
from astropy.coordinates import FK5, ICRS, SkyCoord, Distance, Angle
from astroquery.gaia import Gaia
from astropy.table import Column
from astropy.time import Time


# note: function could be replaced by: from misc import regheader
def regheader():
    hdr="# Region file format: DS9 version 4.1\n"
    hdr=hdr + "global color=green dashlist=8 3 width=1 font=\"helvetica 10 normal roman\" select=1 highlite=1 dash=0 fixed=0 edit=1 move=1 delete=1 include=1 source=1\n"
    hdr=hdr + "physical\n"
    return hdr

def tabinfo(tabname):
    gaiatable = Gaia.load_table(tabname)
    print(gaiatable)
    # show basic column information
    for column in gaiatable.columns:
        print('{:16s}|{:12s}|{}'.format(column.name, str(column.unit), column.description))

def tabcolumns(tabname):
    # show detailed column information
    gaiatable = Gaia.load_table(tabname)
    for column in gaiatable.columns:
        print(column)


def findgaia(param):
    tabname="gaiadr3.gaia_source"
    colnames=('source_id', 'ref_epoch', 'ra', 'dec', 'parallax', 'pm', 'pmra', 'pmdec',
        'phot_g_mean_mag', 'phot_bp_mean_mag', 'phot_rp_mean_mag', 'phot_variable_flag',
        'radial_velocity')
    maglim=15
    nmax=1000       # max number of catalog sources
    maxsize=1000    # max size of plot symbol
    doPlot=False
    verbose=False
    syntax='syntax: findgaia [-v] setname radeg decdeg raddeg'.format()
    for i in range(len(param)):
        if(param[0]=='-h'):
            print(syntax, file=sys.stderr)
            exit(1)
        if(param[0]=='-i'):
            tabinfo(tabname)
            exit(1)
        if(param[0]=='-c'):
            tabcolumns(tabname)
            exit(1)
        if(param[0]=='-v'):
            verbose=True
            del param[0]
        if(param[0]=='-m'):
            maglim=float(param[1])
            del param[0:2]
    if (len(param) != 4):
        print(syntax, file=sys.stderr)
        exit(1)

    # read positional arguments
    setname = param[0]
    if (param[1].find(":") < 0):
        radeg = float(param[1])
    else:
        radeg = 15 * Angle(param[1] + " degrees").degree
    if (param[2].find(":") < 0):
        decdeg = float(param[2])
    else:
        decdeg = Angle(param[2] + " degrees").degree
    raddeg = float(param[3])

    
    # TODO: check for required data files
    shead_fname = setname + ".head"
    whead_fname = setname + ".wcs.head"
    
    # output file names
    outreg_fname=setname + '.gaia.reg'
    outfits_fname=setname + '.gaia.fits'
    
    # read obstime from set header text file
    sfile = open(shead_fname, 'r')
    lines = sfile.readlines()
    sfile.close
    tobs=Time(2000.0, format='jyear')
    for line in lines:
        if (line.startswith('JD ')):
            tobs=Time(line.split()[2], format='jd')
            break
    print('tobs =', tobs.iso)

    # read wcs header text file
    # note: eliminate COMMENT lines (might contain non-ASCII characters)
    wfile = open(whead_fname, 'r')
    lines = wfile.readlines()
    wfile.close()
    hstr='';
    for line in lines:
        if (not line.startswith('COMMENT')):
            hstr = hstr + line
    whead = fits.Header.fromstring(hstr, sep='\n')
    # replace TAN in CTYPEi by TPV (to work around PV1_5 : Unrecognized
    #   coordinate transformation parameter,
    #   ref. https://github.com/astropy/astropy/issues/299)
    whead['CTYPE1'] = 'RA---TPV'
    whead['CTYPE2'] = 'DEC--TPV'

    # data query
    query = """SELECT TOP {nmax} {columns} FROM {tab} 
        WHERE DISTANCE({ra},{dec},gaiadr3.gaia_source.ra, gaiadr3.gaia_source.dec) < {rad}
          AND gaiadr3.gaia_source.phot_g_mean_mag < {maglim}
        ORDER BY phot_g_mean_mag""".format(
            nmax=str(nmax),
            columns=','.join(colnames),
            tab=tabname,
            ra=str(radeg),
            dec=str(decdeg),
            rad=str(raddeg),
            maglim=str(maglim))
    #print(query)

    job = Gaia.launch_job_async(query)
    gaiatab = job.get_results()
    #print(gaiatab.info)
    numrows = len(gaiatab)
    print("Number of rows =", numrows)
    gaiaepoch = 'J{:.1f}'.format(np.mean(gaiatab['ref_epoch']))
    print("Gaia epoche =", gaiaepoch)
    
    # show some data for debugging
    if False:
        print(gaiatab['phot_variable_flag'].dtype) # object
        print(type(gaiatab['phot_variable_flag'].data)) # <class 'numpy.ma.core.MaskedArray'>
        s = gaiatab['phot_variable_flag'].astype(str)
        for idx in range(2):
            print('flag =', gaiatab['phot_variable_flag'][idx])
            print(s[idx])
    
    # apply precession
    # note:
    # - deal with MaskedColumn e.g. gaiatab['parallax'] or gaiatab['radial_velocity']
    #   may produces error: RuntimeWarning: invalid value encountered in pmsafe
    #   therefore we need to fill masked (unknown) values
    parallax_mas=gaiatab['parallax'].filled(0.1).value # in mas
    print('parallax min = ', np.min(parallax_mas), 'mas')  # why does it have negative values?
    parallax_mas = np.clip(parallax_mas, a_min=0.01, a_max=10000)
    dist = 1000./parallax_mas * u.pc
    skycoords = SkyCoord(ra=gaiatab['ra'], dec=gaiatab['dec'],
        pm_ra_cosdec=gaiatab['pmra'].filled(0), pm_dec=gaiatab['pmdec'].filled(0),
        radial_velocity=gaiatab['radial_velocity'].filled(0),
        distance=dist,
        frame='icrs', obstime=gaiaepoch).apply_space_motion(new_obstime=tobs)
    
    # output table to FITS file
    # TODO: any column having dtype 'object' must be replaced
    # ref: https://github.com/astropy/astropy/issues/5258
    newcol=Column(gaiatab['phot_variable_flag'].astype(str))
    gaiatab.replace_column('phot_variable_flag', newcol)
    gaiatab.write(outfits_fname, format='fits', overwrite=True)
    # TODO: add some catalog description meta data to FITS header
    
    # convert ra/dec to pixel (FITS) coordinates
    wcs = WCS(whead) #, relax=WCSHDR_CD00i00j | WCSHDR_PROJPn)
    pixcoords = wcs.world_to_pixel(skycoords)
    x, y = pixcoords
    x = x + 1
    y = y + 1
  
    # output to ds9 region file
    outreg = open(outreg_fname, "w+")
    outreg.write(regheader())
    for idx in range(x.size):
        label = '{:.2f}'.format(gaiatab['phot_g_mean_mag'][idx])
        outreg.write('circle({:.3f},{:.3f},5) # text="{}"\n'.format(x[idx], y[idx], label))
        idx = idx + 1
    outreg.close()
        
    
    if (doPlot):
        ralist = gaiatab['ra'].tolist()
        declist = gaiatab['dec'].tolist()

        import matplotlib.pyplot as plt
        ax = plt.gca()
        ax.invert_xaxis()
        ax.axis('equal')
        pointsize = 10 / 10 ** ((gaiatab['phot_g_mean_mag']-maglim+1)/4)
        pointsize = np.clip(pointsize, a_min=0, a_max=maxsize)
        plt.scatter(ralist,declist,s=pointsize,marker='.')
        plt.show()


if (__name__ == "__main__"):
    findgaia(sys.argv[1:])
