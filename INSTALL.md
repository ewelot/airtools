

## Installation of binary packages

Binary packages are provided for the following Linux distributions:

  - Ubuntu 20.04 "Focal" 
  - Debian 10 "Buster"
  - Debian 11 "Bullseye"

Ubuntu packages are tested on Xubuntu LTS distributions and should work on
any Ubuntu desktop flavour (e.g. native Ubuntu, Kubuntu, Lubuntu). 

Adding the binary package repository of the AIRTOOLS software is done by
adding an entry to the package managment sources.
If e.g. your distribution is based on Ubuntu 20.04 "Focal" you should run the
following commands in a terminal:

    DIST=focal
    REPO=http://fg-kometen.vdsastro.de/airtools/debian
    SRCFILE=/etc/apt/sources.list.d/airtools.list
    sudo bash -c "echo deb [trusted=yes] $REPO $DIST main > $SRCFILE"

If you are running a different distribution, you must replace the setting of
DIST by using your distributions code name (e.g. bullseye) in the command
sequence above.

Installation (or any later update) is done by invoking the following commands:

    sudo apt update
    sudo apt install airtools


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
- python3-pyvips (https://github.com/libvips/pyvips)
- python3-ephem (https://rhodesmill.org/pyephem)

If you have questions regarding the detailed procedure, do not hesitate to
contact the author of the AIRTOOLS software.


## Documentation

Documentation is available under the `/usr/share/doc/airtools-doc/` directory
after successful installation of the binary packages. The most up-to-date
documentation is always found on GitHub's
[doc directory](doc/).
