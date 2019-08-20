
import sys
import math
from collections import defaultdict
from csv import DictReader
import ephem

# csv file parser (column names are in first row)
def parse_csv(filename, fieldnames=None, delimiter=','):
    result = defaultdict(list)
    with open(filename) as infile:
        reader = DictReader(
            infile, fieldnames=fieldnames, delimiter=delimiter
        )
        for row in reader:
            for fieldname, value in row.items():
                result[fieldname].append(value)
    return result

# convert UT date string yyyymmdd to JD
def ymd2jd (ymd):
    s=str(ymd)
    datestr=s[0:4] + '/' + s[4:6] + '/' + s[6:]
    return ephem.julian_date(datestr)

# convert JD to UT date string yyyymmdd.dd
def jd2ymd (jd):
    d=ephem.Date(jd - ephem.julian_date(0))
    x=d.triple()
    s='{:04d}{:02d}{:05.2f}'.format(x[0],x[1],x[2])
    return s

# convert mag to heliocentric mag
def hmag(mag, d_earth):
    if (type(mag) is str):
        mag=float(mag.rstrip(':'))
    val=mag-5*math.log10(d_earth)
    return val

# convert coma size from arcmin to linear diameter in km
def lcoma(coma, d_earth):
    coma=float(coma)
    if coma < 0: return coma
    val=d_earth*ephem.meters_per_au*math.tan(math.pi*coma/60/180)/1000
    return val


def addephem (param):
    # param
    #   csvfile   reqired fields: date, source, obsid, mag, coma, method, filter
    #               where date is yyyymmdd.dd
    #   cephem    comet ephemeris record from xephem edb file
    #
    # output: text file with following fields:
    #   position 1  2    3      4     5   6    7    8     9      10     11         12    13
    #   fields:  jd date source obsid mag hmag coma lcoma method filter log(r_sun) r_sun d_earth
    if (len(param) != 2):
        print("usage: addephem csvfile cephem")
        exit(-1)
    else:
        csvfile=param[0]
        cephem=param[1]

    # TODO: parse comet ephem database (xephem edb format)
    k2=ephem.readdb(cephem)

    data=parse_csv(csvfile)
    n=len(data['date'])
    for i in range(n):
        str=data['date'][i]
        if (str[0]=='#'):
            continue
        datestr=str[0:4] + '/' + str[4:6] + '/' + str[6:]
        k2.compute(datestr)
        print('{:.3f} {} {} {}'.format(
            ephem.julian_date(datestr),
            data['date'][i],
            data['source'][i],
            data['obsid'][i]
            ),
            end='')
        print(' {} {:.2f} {} {:.0f}'.format(
            data['mag'][i],
            hmag(data['mag'][i], k2.earth_distance),
            data['coma'][i],
            lcoma(data['coma'][i], k2.earth_distance)
            ),
            end='')
        print(' {} {} {:.4f} {:.4f} {:.4f}'.format(
            data['method'][i],
            data['filter'][i],
            math.log10(k2.sun_distance),
            k2.sun_distance,
            k2.earth_distance
            ))
    exit()


def mkephem (param):
    # param
    #   cephem    comet ephemeris record from xephem edb file
    #   start     start date (yyyymmdd or jd)
    #   end       end date (yyyymmdd or jd)
    #   g         model parameter
    #   k         model parameter
    # output: text file with following fields:
    #   position 1  2    3   4    5          6     7
    #   fields:  jd date mag hmag log(r_sun) r_sun d_earth
    # reading command line parameters
    if (len(param) < 3):
        print("usage: mkephem cephem start end [g] [k] [num]")
        exit(-1)
    else:
        cephem=param[0]
        start=float(param[1])
        end=float(param[2])
    if (len(param) > 3):
        if param[3]: g=float(param[3])
        if param[4]: k=float(param[4])
    if (len(param) > 5):
        num=int(param[5])

    # convert start and end from yyyymmdd to JD
    if (start > 10000000): start=ymd2jd(start)
    if (end > 10000000): end=ymd2jd(end)

    # TODO: parse comet ephem database
    k2=ephem.readdb(cephem)
    if 'g' in locals(): k2._g=g
    if 'k' in locals(): k2._k=k
    print('# model: m = {:.2f} + 5log(D) + {:.2f}*2.5log(r)'.format(k2._g,k2._k))


    # print header line
    print('# jd        date        mag   hmag  log(r) r      d')

    if not 'num' in locals(): num=100   # number of intervals
    for i in range(num+1):
        jd=start+i*(end-start)/(num)
        utdate=jd2ymd(jd)
        k2.compute(ephem.Date(jd - ephem.julian_date(0)))
        print('{:.3f} {}'.format(
            jd,
            utdate
            ),
            end='')
        print(' {} {:.2f}'.format(
            k2.mag,
            hmag(k2.mag, k2.earth_distance)
            ),
            end='')
        print(' {:.4f} {:.4f} {:.4f}'.format(
            math.log10(k2.sun_distance),
            k2.sun_distance,
            k2.earth_distance
            ))
    exit()


if __name__ == "__main__":
    import sys
    globals()[sys.argv[1]](sys.argv[2:])
