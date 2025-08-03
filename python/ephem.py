
import sys
import math
import numpy as np
import ssl
import requests

from astroquery.jplhorizons import Horizons
from astropy.table import vstack

from misc import parse_csv
from timeconv import jd2ymd, ymd2jd, ymd2time
from comets import cometname, hmag, lcoma


def addephem (param):
    '''
    add ephemerides data to csv file using dates given therein
    '''
    # param
    #   csvfile   reqired fields: utime, date, source, obsid, mag, coma, method, filter, soft
    #               where utime is unix time in seconds and date is yyyymmdd.dd
    #   comet     (short) comet name
    #
    # options
    #   -p phase0 if set then apply phase effect correction to magnitudes
    #
    # output: text file with following fields:
    #   position 1     2    3      4     5   6    7    8     9      10     11   12         13    14      15
    #   fields:  utime date source obsid mag hmag coma lcoma method filter soft log(r_sun) r_sun d_earth ph_angle
    phase0=None
    doCache=True
    verbose=False
    for i in range(2):
        if(param[0] == '-p'):
            phase0=float(param[1])
            del param[0:2]
    if (len(param) != 2):
        print("usage: addephem csvfile comet", file=sys.stderr)
        exit(-1)
    else:
        csvfile=param[0]
        comet=param[1]
    
    # derive long comet name
    longcometname=cometname(comet)
    if (longcometname == ""):
        print("ERROR: unsupported comet name", file=sys.stderr)
        exit(-1)

    # read CSV input data
    data=parse_csv(csvfile)
    nobs=len(data['date'])
    if verbose: print('#', nobs, 'records read', file=sys.stderr)
    spandays=(float(max(data['utime'])) - float(min(data['utime'])))/3600/24

    # limit list of epoches by rounding dates
    if verbose:
        for i in range(10):
            print(data['date'][i], ymd2time(data['date'][i]).jd, file=sys.stderr)
    if (spandays < 30):
        # no rounding
        jdlist = [ymd2time(datestr).jd for datestr in data['date']]
    else:
        if (spandays < 100):
            # rounding to 0.1 days
            jdlist = [round(ymd2time(datestr).jd * 10)/10 for datestr in data['date']]
        else:
            if (spandays < 200):
                # rounding to 0.2 days
                jdlist = [round(ymd2time(datestr).jd * 5)/5 for datestr in data['date']]
            else:
                if (spandays < 400):
                    # rounding to 0.5 days
                    jdlist = [round(ymd2time(datestr).jd * 2)/2 for datestr in data['date']]
                else:
                    # rounding to 1 day
                    jdlist = [round(ymd2time(datestr).jd) for datestr in data['date']]
                    
    if verbose: print(len(jdlist), file=sys.stderr)
    
    # collect ephemerides data
    junk=0
    junksize=100
    ujdlist=np.unique(jdlist)
    n=len(ujdlist)
    # TODO: use np.unique(jdlist)
    if verbose:
        print("# using {:d} dates to match {:d} observations".format(n,nobs), file=sys.stderr)
    for i in range(n):
        if (i%junksize == 0):
            # need to operate on junks because JPL queries are limited to ~100 epoches
            first=junk*junksize
            last=min(first+junksize, n)
            hor=Horizons(id=longcometname, epochs=list(ujdlist[first:last]), id_type='designation')
            if (hor == None):
                print('ERROR: object "' + longcometname + '" not known by JPL Horizons', file=sys.stderr)
                exit(-1)
            try:
                if (i==0):
                    eph=hor.ephemerides(closest_apparition=True, cache=doCache)
                else:
                    eph=vstack([eph, hor.ephemerides(closest_apparition=True, cache=doCache)])
            except requests.exceptions.SSLError as e:
                if ('SSLCertVerificationError' in str(e)):
                    print('ERROR: SSLError (SSLCertVerificationError)', file=sys.stderr)
                else:
                    print('ERROR: SSLError', file=sys.stderr)
                print('ERROR: unable to retrieve ephemerides from JPL', file=sys.stderr)
                exit(-1)
            except Exception as e:
                print('ERROR (uncatched):', type(e), file=sys.stderr)
                print('ERROR: unable to retrieve ephemerides from JPL', file=sys.stderr)
                exit(-1)
            junk=junk+1

    for i in range(nobs):
        jd=jdlist[i]
        # note: eph is sorted by date, not by list of epoches, therefore we
        #   need to match the valid entry by its jd
        curr_eph = eph[eph["datetime_jd"] == jd][0]
        earth_dist = curr_eph["delta"]
        sun_dist = curr_eph["r"]
        phase_angle = curr_eph["alpha"] # angle between sun-target-observer
        if (phase0):
            # ref: https://asteroid.lowell.edu/comet/dustphase/
            # TODO: curve only valid for phase_angle<60
            phase_corr = 2.5 * (\
                -0.01807 * (phase_angle - phase0) +\
                0.000177 * (phase_angle**2 - phase0**2))
            if (data['mag'][i][-1]==':'):
                mag='{:.2f}:'.format(float(data['mag'][i][0:-1]) + phase_corr)
            else:
                mag='{:.2f}'.format(float(data['mag'][i]) + phase_corr)
        else:
            phase_corr=0
            mag=data['mag'][i]

        # print records
        print('{} {} {} {}'.format(
            data['utime'][i],
            data['date'][i],
            data['source'][i],
            data['obsid'][i]
            ),
            end='')
        print(' {} {:.2f} {} {:.0f}'.format(
            mag,
            hmag(data['mag'][i], earth_dist) + phase_corr,
            data['coma'][i],
            lcoma(data['coma'][i], earth_dist)
            ),
            end='')
        print(' {} {} {} {:.4f} {:.4f} {:.4f} {:.1f}'.format(
            data['method'][i],
            data['filter'][i],
            data['soft'][i],
            math.log10(sun_dist),
            sun_dist,
            earth_dist,
            phase_angle
            ))
    exit()


def mkephem (param):
    '''
    create ephemerides for solar system object at equally spaced intervals
    '''
    # options
    #   -g g      model parameter (defaults to value provided by JPL Horizons elements)
    #   -k k      model parameter (defaults to value provided by JPL Horizons elements)
    # param
    #   cname     comet name like 13P or 2017K2
    #   start     start date (yyyymmdd or jd)
    #   end       end date (yyyymmdd or jd)
    #   num       number of equally spaced data points
    # output: text file with following fields:
    #   position 1     2    3   4    5          6     7
    #   fields:  utime date mag hmag log(r_sun) r_sun d_earth
    # reading command line parameters
    num=100
    dateunit="yyyymmdd"
    doReturnArray=False
    verbose=False
    doCache=True
    if (param[0] == "-s"):
        dateunit="unixseconds"
        del param[0]
    if (param[0] == "-g"):
        g=float(param[1])
        del param[0:2]
    if (param[0] == "-k"):
        k=float(param[1])
        del param[0:2]
    if (param[0] == "-a"):
        doReturnArray=True  # not implemented yet!!
        del param[0]
    if (len(param) < 3):
        print("usage: mkephem [-s] [-g g] [-k k] comet start end [num]")
        exit(-1)
    else:
        comet=param[0]
        start=float(param[1])
        end=float(param[2])
    if (len(param) > 3):
        num=int(param[3])
    
    # derive long comet name
    longcometname=cometname(comet)
    if (longcometname == ""):
        print("ERROR: unsupported comet name", file=sys.stderr)
        exit(-1)

    # convert start and end from yyyymmdd or unix time to JD
    if (dateunit == "yyyymmdd"):
        start=ymd2jd(start)
        end=ymd2jd(end)
    else:
        # convert start and end from unix time to JD
        start=2440587.5+start/86400.0
        end=2440587.5+end/86400.0
    
    # get elements from JPL
    hor=Horizons(id=longcometname, epochs=(start+end)/2, id_type='designation')
    if (hor == None):
        print('ERROR: object "' + longcometname + '" not known by JPL Horizons')
        exit(-1)
    eph=hor.ephemerides(closest_apparition=True, cache=doCache)
    # if not given use magnitude model parameters from JPL Horizons
    if not 'g' in locals(): g=eph[0]["M1"]
    if not 'k' in locals(): k=eph[0]["k1"]/2.5
    print('# model: m = {:.2f} + 5log(D) + {:.2f}*2.5log(r)'.format(g, k))

    # list of epoches
    if verbose:
        for i in range(10):
            print(data['date'][i], ymd2time(data['date'][i]).jd, file=sys.stderr)
    jdlist = np.linspace(start, end, num)
    if verbose: print(len(jdlist), file=sys.stderr)

    # print header line
    print('# utime        date        mag   hmag  log(r) r      d')

    junk=0
    junksize=50
    for i in range(num):
        if (i%junksize == 0):
            # need to operate on junks because JPL queries are limited to ~50 epoches
            first=junk*junksize
            last=min(first+junksize, num)
            hor=Horizons(id=longcometname, epochs=list(jdlist[first:last]), id_type='designation')
            if (hor == None):
                print('ERROR: object "' + longcometname + '" not known by JPL Horizons')
                exit(-1)
            eph=hor.ephemerides(closest_apparition=True, cache=doCache)
            junk=junk+1
        jd=jdlist[i]
        # note: eph is sorted by date, not by list of epoches, therefore we
        #   prefer to match the currently valid entry by its jd
        e = eph[i%junksize]
        mag=g+5*math.log10(e["delta"])+k*2.5*math.log10(e["r"])
        unixtime=(jd-2440587.5)*86400.0
        utdate=jd2ymd(jd)
        print('{:.0f} {}'.format(
            unixtime,
            utdate
            ),
            end='')
        print(' {:.3f} {:.3f}'.format(
            mag,
            hmag(mag, e["delta"])
            ),
            end='')
        print(' {:.4f} {:.4f} {:.4f}'.format(
            math.log10(e["r"]),
            e["r"],
            e["delta"]
            ))


