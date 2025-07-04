
# Astronomical Image Reduction TOOLSet

AIRTOOLS is a software for astronomical image reduction
of both CCD and DSLR observations on Linux. A graphical user interface is
build on top of command-line programs which combine a large number of
tools readily available on most Linux desktops, including
ImageMagick, GraphicsMagick, Netpbm, WCSTools, Gnuplot.

The primary intention of the software is the photometric analysis
of comet observations. A new approach by means of large aperture photometry
allows to measure the total coma brightness in a consistent way.

The underlying AIRTOOLS programs make use of powerful third party software
commonly used in professional astronomy or image analysis projects:
- [SAOImage DS9](http://ds9.si.edu/site/Home.html): image display, catalog
  viewer and analysis GUI
- [Astromatic software](http://www.astromatic.net) by E.Bertin: automatic source
  detection (sextractor), astrometric calibration (scamp), stacking (swarp),
  modeling (skymaker) and more
- [Stilts](http://www.starlink.ac.uk/stilts/) by M. Taylor: powerful table
  processing
- [CFITSIO examples](http://heasarc.gsfc.nasa.gov/docs/software/fitsio/cexamples.html):
  basic FITS routines
- [libvips](https://libvips.github.io/libvips/): A fast and memory efficient
  image processing library with bindings to many programming languages
- [Astropy](https://www.astropy.org): Core functionality and common tools
  for astronomy and astrophysics research with Python

<img src="doc/images/splash.png" alt="AIRTOOLS in action" width="900" />
(Screenshot of an AIRTOOLS session)

## Documentation

A preliminary [user manual](doc/manual-en.md) has been added.
It features an in depth installation guide for all users, including those
running a Windows or MacOS X operating system.

Video tutorials of typical AIRTOOLS sessions are in preparation. For
illustrative purposes an older tutorial covering the comet extraction and
photometry part using a previous AIRTOOLS version is still available
[here](https://www.youtube.com/watch?v=sK9D_M06ovA).
