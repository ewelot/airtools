

## Installation on Linux

Please refer to [this chapter](https://github.com/ewelot/airtools/blob/master/doc/manual-en.md#installation-on-linux)
in the user manual.

## Installation on Windows

Please refer to [this chapter](https://github.com/ewelot/airtools/blob/master/doc/manual-en.md#installation-on-windows-using-a-linuxairtools-appliance)
in the user manual.

## Compiling and Installing from source code

If you are running a Linux distribution for which there are no binary packages
provided then you might compile and install the software by yourself.
The compilation depends on a number of libraries. On a Debian/Ubuntu based
distribution they can be installed by the following example command:

    apt-get install libnetpbm10-dev libjasper-dev libjpeg-dev libcfitsio3-dev \
        libtiff5-dev libfftw3-dev libblas-dev libatlas-base-dev \
        libplplot-dev plplot12-driver-xwin plplot12-driver-cairo libshp-dev \
        libcurl4-gnutls-dev

Please note that package names may be different, depending on your Linux
distribution.

In order to run the AIRTOOLS software you must install additional software
either by means of binary packages provided by your distribution or
by compiling/installing them from sources by yourself:

- missfits, scamp, sextractor, skymaker, stiff, swarp (https://github.com/astromatic)
- astrometry.net (https://nova.astrometry.net)
- stilts (http://www.star.bris.ac.uk/~mbt/stilts)
- saods9 (https://sites.google.com/cfa.harvard.edu/saoimageds9)
- xpa-tools (https://hea-www.harvard.edu/RD/xpa)
- wcstools (http://tdc-www.harvard.edu/software/wcstools)
- cfitsio-examples (https://heasarc.gsfc.nasa.gov/docs/software/fitsio/cexamples.html)
- pyvips (https://github.com/libvips/pyvips)
- rawpy (https://github.com/letmaik/rawpy)
- python3-ephem (https://rhodesmill.org/pyephem)

If you have questions regarding the detailed procedure, do not hesitate to
contact the author of the AIRTOOLS software.


## Documentation

Documentation is available under the `/usr/share/doc/airtools-doc/` directory
after successful installation of the binary packages. The most up-to-date
documentation is always found on GitHub's
[doc directory](doc/).
