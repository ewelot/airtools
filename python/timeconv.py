
import warnings
from astropy.utils.exceptions import AstropyDeprecationWarning
warnings.simplefilter('ignore', AstropyDeprecationWarning)
from astropy.time import Time
from astropy.time import TimeDelta


# convert UT date (format YYYYMMDD[.dd]) to Time object
def ymd2time(date):
    s=str(date)
    isoday=s[0:4] + '-' + s[4:6] + '-' + s[6:8]
    if(len(s)>8): dayfrac=float(s[8:])
    else: dayfrac=0
    time = Time(isoday) + TimeDelta(dayfrac, format='jd')
    return time


# convert UT date (format YYYYMMDD[.dd]) to JD
def ymd2jd(ymd):
    return ymd2time(ymd).jd


# convert JD to UT date (output format YYYYMMDD.dd)
def jd2ymd (jd):
    t=Time(jd, format='jd').ymdhms
    ymd=t.year*10000+t.month*100+t.day+t.hour/24+t.minute/60/24+t.second/3600/24
    return '{:.2f}'.format(ymd)


def daterange (dates, interval):
    # dates is list of values using format YYYYMMDD.dd
    s=min(dates)
    start=Time(s[0:4] + '-' + s[4:6] + '-' + s[6:8])
    s=max(dates)
    stop=Time(s[0:4] + '-' + s[4:6] + '-' + s[6:8]) + TimeDelta(1, format='jd')
    print('# date range spans:', stop-start, 'days')
    return {'start':start.iso, 'stop':stop.iso, 'step':f'{24*60*interval:.0f}m'}
