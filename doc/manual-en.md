  - [<span class="toc-section-number">1</span>
    Introduction](#introduction)
  - [<span class="toc-section-number">2</span>
    Installation](#installation)
      - [<span class="toc-section-number">2.1</span> Installing Oracle
        VirtualBox](#installing-oracle-virtualbox)
      - [<span class="toc-section-number">2.2</span> Setup of a Virtual
        Machine for Linux OS](#setup-of-a-virtual-machine-for-linux-os)
      - [<span class="toc-section-number">2.3</span> Booting Install
        Medium of the Xubuntu Linux
        distribution](#booting-install-medium-of-the-xubuntu-linux-distribution)
      - [<span class="toc-section-number">2.4</span> Installing Xubuntu
        Linux](#installing-xubuntu-linux)
      - [<span class="toc-section-number">2.5</span> Xubuntu Desktop
        Basics](#xubuntu-desktop-basics)
      - [<span class="toc-section-number">2.6</span> Installing
        VirtualBox Guest
        Additions](#installing-virtualbox-guest-additions)
      - [<span class="toc-section-number">2.7</span> Installing the
        AIRTOOLS software](#installing-the-airtools-software)
      - [<span class="toc-section-number">2.8</span> Updating the
        AIRTOOLS software](#updating-the-airtools-software)
  - [<span class="toc-section-number">3</span> The AIRTOOLS Graphical
    User Interface](#the-airtools-graphical-user-interface)
  - [<span class="toc-section-number">4</span> The first AIRTOOLS
    Project](#the-first-airtools-project)
      - [<span class="toc-section-number">4.1</span> What is a
        Project?](#what-is-a-project)
      - [<span class="toc-section-number">4.2</span> Setting up the
        first Project](#setting-up-the-first-project)
      - [<span class="toc-section-number">4.3</span> Parameter
        Files](#parameter-files)
      - [<span class="toc-section-number">4.4</span> Raw Images and
        Image Set Definition](#raw-images-and-image-set-definition)
  - [<span class="toc-section-number">5</span> Image
    Reduction](#image-reduction)
      - [<span class="toc-section-number">5.1</span> Master Darks and
        Flats](#master-darks-and-flats)
      - [<span class="toc-section-number">5.2</span> Image
        Calibration](#image-calibration)
      - [<span class="toc-section-number">5.3</span> Background
        evaluation](#background-evaluation)
      - [<span class="toc-section-number">5.4</span> Image
        Registration](#image-registration)
      - [<span class="toc-section-number">5.5</span> Stacking and
        Astrometry](#stacking-and-astrometry)
  - [<span class="toc-section-number">6</span> Large Aperture Comet
    Photometry](#large-aperture-comet-photometry)
      - [<span class="toc-section-number">6.1</span> Comet
        Observation](#comet-observation)
      - [<span class="toc-section-number">6.2</span> PSF Extraction and
        Star Removal](#psf-extraction-and-star-removal)
      - [<span class="toc-section-number">6.3</span> Measuring the
        Comet](#measuring-the-comet)
      - [<span class="toc-section-number">6.4</span> Photometric
        Calibration](#photometric-calibration)

# Introduction

The AIRTOOLS software - or **A**stronomical **I**mage **R**eduction
**TOOLS**et - has been developed for the purpose of calibrating and
analyzing images of astronomical objects captured by CCD or DSLR
cameras. The software provides a large number of functions for basic
image calibration (e.g. bias-, dark-, flatfield calibration, raw
development of bayered images), for automated object recognition,
registration and stacking as well as automated astrometric and
photometric calibration routines.

Moreover specialized tools have been developed to process comet
observations with the goal of obtaining total coma brightness estimates
matching closely those of visual observers. The invention of “Large
Aperture Photometry” should allow to complement visual observations,
extending to fainter magnitude limits (due to deep exposures) with the
benefit of added reproducibility.

Recently a graphical user interface has been added to make the software
more user friendly. It tries to derive suitable parameters for the
underlying functions and programs to hide as much complexity as possible
from the average user. Internally a large number of open source software
programs for image analysis and visualization is used,
e.g. *ImageMagick*, *GraphicsMagick*, *Netpbm* und *Gnuplot*. Powerful
and extremely versatile tools well known in the professional area of
astronomical image reduction are used as well, e.g.

  - [SAOImage DS9](http://ds9.si.edu/site/Home.html): Image viewer with
    extensible tools for analysis and catalog access
  - [Astromatic Software](http://www.astromatic.net) by E. Bertin: Most
    notably *sextractor* (Object recognitionand extraction), *scamp*
    (astrometry), *swarp* (image transformation and stacking),
    *skymaker* (modelling objects)
  - [Stilts](http://www.starlink.ac.uk/stilts/) by M. Taylor: Analysis,
    filtering and transforming tabular data (e.g. FITS tables)
  - [WCSTools](http://tdc-www.harvard.edu/software/wcstools/) by J.
    Mink: Tools to create and manipulate coordinate system information
  - [libvips](https://libvips.github.io/libvips/): A fast and memory
    efficient image processing library with bindings to many programming
    languages

The AIRTOOLS software is freely available. The project - including
source code - is hosted at <https://github.com/ewelot/airtools>.
Pre-compiled binary packages are provided for several Linux
distributions.

The AIRTOOLS software has been developed in the hope to proove useful.
Its development relies on your feedback, so please do not hesitate to
ask any question at <t_lehmann@freenet.de>. Any suggestion or comment or
call for help is welcome.

 

Good luck and clear skies\!

Thomas Lehmann, Weimar (Germany)

# Installation

The AIRTOOLS software must be installed on a Linux operating system,
which is not commonly used in the amateur astronomy community. There
exist several approaches on how to fullfill this requirement:

  - use a dedicated Linux computer or
  - configure your computer for dual booting of either Windows (or OS/X)
    or Linux or
  - set up a virtualization software which runs the entire Linux OS in
    an encapsulated application on your Windows (or OS/X) computer

We will focus on the third approach as it is probably the most
convenient way of running Linux on Windows or OS/X hosts. Once the Linux
OS is up and running the AIRTOOLS software itself must be installed. The
overall installation process therefore can be outlined by the following
steps which are described in depth later on:

  - install the virtualization software
  - setup a virtual machine for the Linux OS
  - install the Linux OS on the virtual machine
  - install AIRTOOLS on the (virtual) Linux system

The full installation will take about half an hour to complete.

## Installing Oracle VirtualBox

VirtualBox (<http://www.virtualbox.org>) is a free and powerful
virtualization software for enterprise and home users. Get the latest
software package (version 6.1.18 at the time of writing) for your host
operating system from the
[Downloads](https://www.virtualbox.org/wiki/Downloads) page and install
it.

Subsequently you should install the “Oracle VM VirtualBox Extension
Pack” for improved performance and additional virtual hardware
features. Get it from the appropriate section of the previously
mentioned download page. Click on “All supported platforms” and open it
using the Oracle VM VirtualBox software. You might be asked to provide
credentials to allow installation.

## Setup of a Virtual Machine for Linux OS

Start the Oracle VirtualBox Manager, if not running already. Click on
the “New” button and fill in the name of the new VM, e.g. xubuntu-vm.
Depending on the name you have choosen you might have to select
Type=“Linux” and Version=“Ubuntu (64-bit)”. Continue by pressing
“Next”.

Set the memory size to \>=2 GB (recommended 4 GB or up to 75% of
physical RAM) and press “Next”.

Create a virtual hard disk of type VDI of fixed size. You can use the
proposed file name but it is recommended to create the virtual disk file
on a fast physical hard disk drive, e.g. SSD. The file size should be
\>=50 GB to serve for roughly 10-20 comet observations, based on 10-20
individual exposures each. If you intent to use the AIRTOOLS software
regularly to analyze all your comet observations then you should create
a much larger virtual hard disk. After pressing the “Create” button the
virtual machine is created.

It is recommended to tweak some additional parameters for improved
performance. Click the “Settings” button to access the following tabs:

  - Tab System/Processor: increase number of CPU to \>=2 (up to number
    of physical cores)
  - Tab Display/Screen: increase Memory to 64 MB
  - Tab USB: choose USB 3.0 Controller

Finally you should create a desktop icon to directly launch the virtual
machine. Locate the name of the virtual machine on the left side of the
VirtualBox Manager, press the right mouse and select “Create Shortcut on
Desktop”.

![Setup of a virtual machine in the Oracle VirtualBox
Manager](images/virtualbox-manager.png "virtualbox manager")

## Booting Install Medium of the Xubuntu Linux distribution

Download the ISO image file of the latest Xubuntu LTS release from
<http://xubuntu.org/>. Please note the imprtant **LTS** version label,
which indicates a “Long Term Support” release. This Linux OS version is
well supported by the AIRTOOLS software. Choose a mirror download close
to your location and download the 64-bit desktop image. At the time of
this writing it is named `xubuntu-20.04.2.0-desktop-amd64.iso`.

The ISO image file is used in place of a install medium for the virtual
machine. To do so you have to start the VirtualBox software (if not
running already) and press the “Settings” button of the selected virtual
machine.

Select the “Storage” tab. Within “Storage Devices” click on the CD
symbol (labeled “Empty”) and from “Attributes” click the CD symbol near
the right border of the window and select the previously downloaded ISO
file. Pressing “OK” will save your modified settings and you are ready
to start the virtual machine by pressing the green “Start” button.

The following boot process is very similar to a regular boot process of
a install CD/DVD on a real computer. In addition, the current virtual
machine can be used to start a fully functional Linux live session to
evaluate or experiment with the Xubuntu Linux OS (but this is not our
goal).

## Installing Xubuntu Linux

Now, the Linux OS has to be installed into the presently empty virtual
hard disk of the running virtual machine. Please make sure your host
computer has a working internet connection.

From the initial “Welcome” screen you choose your prefered language and
click the “Install Xubuntu” button to start the setup program of the
installer. You can accept default settings on all the following screens
(“Keyboard layout”, “Updates and other software”, “Installation type”).
Please note that the Linux OS is installed on the virtual hard disk
only, it does in no way erase data from your host computer’s file
system. Finally click “Install now” and confirm writing the changes to
the (virtual) disk by the “Continue” button.

While the installation process has already started in the background you
are asked to provide a few additional informations:

  - “Where are you”: Select your time zone by clicking close to your
    geographic location
  - “Who are you”: Fill in your (full) name, a computer name, username
    and user password. Note that choosing “xubuntu” for the name of the
    virtual computer is allowed, despite the given warning message. You
    might toggle the “Log in automatically” radio button for the sake of
    convenience.

Continue the installation process which will take a few minutes to
complete. Finally you are asked to restart the (virtual) computer. This
will take a little time and you might be prompted to remove the
installation medium (the ISO file used in the virtual CDROM drive).
Press the “Enter” key to continue. There are few combinations of host
hardware, VirtualBox version and guest operating system where the
virtual machine is not rebooting but showing a black screen for infinite
time. In this case you must manually close the virtual machine window
and select “Shutdown VM”. In the VirtualBox Manager, check that the ISO
file is removed from the virtual CDROM drive and start the virtual
machine again.

The virtual machine (in virtualbox jargon the “guest” system) will now
boot the installed Linux OS from the virtual disk and automatically logs
in to the Xubuntu Linux desktop. Please note the different sections of
the VirtualBox guest application window: the VirtualBox guest machine’s
menu bar at the top, a status bar at the bottom and the virtual screen
of the Linux Desktop in between.

After booting into the virtual Xubuntu Linux desktop you might be faced
by a message window stating “Incomplete Language Support”. It is save to
skip the update until later as it is not required by the AIRTOOLS
software installation.

Similarly the “Software Updater” might pop up at any time with the
information about available updates of currently installed packages.
Again, those updates are not required right now but should be completed
after the AIRTOOLS installation.

![Xubuntu Linux (with AIRTOOLS) running in
VirtualBox](images/xubuntu-vm-annotated.png "Xubuntu")

## Xubuntu Desktop Basics

On the top of the desktop screen there is a (dark) desktop panel. If you
click on the small icon on the left of this panel (it uses the Xubuntu
logo which mimics the head of a mouse) the main application menu pops
up. From there you can start programs, tweak several desktop settings,
log out and shutdown the virtual Linux system. Note the location of the
“Log out” icon at bottom-right of the menu, which is also used to
shutdown or restart the Linux OS. Get familiar with how to start the web
browser and the file manager and how to shutdown the Linux OS.

For additional information please consult the official [Xubuntu
Documentation](https://docs.xubuntu.org/2004/) or other tutorials on the
web. Please keep in mind that you do not have to worry about any
hardware specific setups in your Linux system (or for example network
connection) because all communication to the real devices of the host
computer is transparently handled by the VirtualBox drivers.

## Installing VirtualBox Guest Additions

The Guest Additions are designed to be installed inside a virtual
machine after the guest operating system has been installed. They
consist of device drivers and system applications provided by Oracle
VirtualBox that optimize the guest operating system for better
performance and usability.

For installation you must

  - Boot the guest OS.
  - Go to the VirtualBox guest menu item “Devices” and press “Install
    Guest Additions CD Image”. A new CD icon appears on the Linux
    desktop and a few seconds later the Linux file manager is showing
    the contents of the Guest Additions virtual CD.
  - Open a terminal window using “File” menu of the file manager and
    select “Open Terminal Here”.
  - From the command line of the terminal run the following command (you
    will be asked to provide your password): `sudo apt-get install
    build-essential`
  - Start installation by entering the command: `sudo bash
    VBoxLinuxAdditions.run`
  - If installation has finished close the terminal window and eject the
    virtual CD by using the eject button (caret-up) next to the CD entry
    in the file manager.
  - Finally you must reboot the Linux guest.

After a restart of the Linux virtual machine you may adjust the guest
window size and effectively the screen size of the Linux desktop as
needed.

Moreover, you can now configure the virtual machine to use a shared
clipboard between host and guest and use drag-and-drop between both
systems. Those settings are activated from the “Devices” menu of the
VirtualBox guest menu bar on the top of the window.

## Installing the AIRTOOLS software

The AIRTOOLS project is hosted at <https://github.com/ewelot/airtools>
where you can find the latest source code and documentation.
Pre-compiled binary packages are build for several Debian based Linux
distributions (e.g. Xubuntu) and can easily be installed by running an
install script.

The download of the installer requires a few more steps than usual,
because you will fetch it from a GitHub source repository:

  - From within the Linux virtual machine start the web browser and open
    the project page at <https://github.com/ewelot/airtools>.
  - Locate the install script `install_deb.sh` within the source tree
    and click on it.
  - On the top-right of the displayed script source locate the button
    labeled “Raw”, click it with right mouse button and select “Save
    Link As” which will download the installer file.

You run the installer by following the next steps:

  - Locate the directory which contains the previously downloaded file
    `install_deb.sh`. E.g. double-click the “Home” icon on the desktop
    which starts the file manager and open the “Downloads” folder.
  - Open the “File” menu of the file manager and choose “Open Terminal
    Here”. A new terminal window will pop up, ready to enter commands to
    be executed.
  - Enter the following command on a single line: `sudo bash
    install_deb.sh`
  - You must provide your password before the installation is started.

Upon first installation of the AIRTOOLS software the script will
download many other required software packages from the official Xubuntu
repository. This might take a few minutes depending on the bandwidth of
your internet connection. At the end of the installation you will
receive some log messages about success (or failure) in the terminal
window. A log file is created for later reference and a new icon is
showing up on your Linux desktop.

## Updating the AIRTOOLS software

An update of the AIRTOOLS software is issued the same way as the initial
installation, that is by downloading and executing the installer
`install_deb.sh`. Though, it will complete much faster due to much
smaller amount of required downloads.

# The AIRTOOLS Graphical User Interface

The graphical user interface consists of three tabs. The first tab is
used for all basic image reduction steps to process the raw images with
the goal to obtain stacked images of your targets. The second tab is
dedicated to the comet extraction and large aperture photometry tasks.
Finally, a couple of handy tasks are placed on a third tab.

The lower part of the interface will display text output from any
processing steps. There you can watch progress of the running tasks, see
some measurement results but also possible error messages. In a few
cases during the comet extraction part you will get information about a
required user action written to the same text area. Please note that all
the visible output is logged to a text file `airtools.log` as well,
which comes handy in case of errors or simply for later reference.

  
![The AIRTOOLS user interface tabs](images/airtools-gui.png
"airtools-gui")

# The first AIRTOOLS Project

## What is a Project?

When observing during a clear night, many different exposures are taken,
usually of different targets. It is common practice that an observation
of a single target consists of multiple bracketed exposures. Serious
observers are capturing calibration frames (darks, flats) as well. It is
possible that different instruments (telescopes, filters, cameras) are
used. All these images of a single night will be analyzed in a single
AIRTOOLS project. Consequently, the project directory itself (and
related ones) must have the date of observation used as part of its
name. It is good practice to use the date at the beginning of the night.

The following directories are related to a project:

  - Project directory:  
    It stores all config files of this project, results from image
    reduction and analysis (images, plots, data tables) and log files.
    After finishing a project this directory should be saved, e.g. to an
    external disk drive.
  - Raw directory:  
    Used for all the individual raw images as created by your image
    asquisition system, both light frames and calibration images related
    to the project.
  - Temporary directory:  
    Used to store individual calibrated images of the project which are
    used by several different AIRTOOLS analysis tasks as well as
    temporary files created during those tasks. This directory may be
    savely deleted when the project is finished.

## Setting up the first Project

Upon first start of the AIRTOOLS software the base directories for the
three above mentioned storage places must be defined. Each new project
will later create a new subdirectory below these places.

Next, the setup for the first project must be configured. Select the
date of observation. This will be used to make initial suggestions for
names of the project directory, raw directory and temporary directory.
It is allowed to modify those names, e.g. append a letter. E.g. you
might want to repeat the image reduction of a given night using other
parameters without interfering the original analysis. In that case you
could use the same raw directory name but different names for the
project and temporary directories.

Further settings are:

  - Site:  
    Enter the name of your observatory site (must be single word) or
    choose one of the items from the combobox dropdown list (it holds
    items which are already defined in the parameter file `sites.dat`).
  - TZoff:  
    Enter the time zone offset of your camera time with respect to UT in
    hours. The camera time is found either in RAW images metadata of
    DSLR cameras or in the header of your FITS images (usually stored in
    keyword DATE-OBS).

## Parameter Files

The different image acquisition systems used by amateurs do normally
write some meta data about telescope, camera etc. to image headers.
Those data is required by any image reduction and analysis software.
Unfortunately, keyword names and the format of their values is not
standardized in any way.

We therefore decided to supply most redundant data by means of parameter
files - simple text files, structured in a tabular way. The first line
in the file is used to define the columns (name of parameters). Anything
that appears after the `#` sign in any other line is considered a
comment and will be ignored. Each line describes a separate entry and
each parameter value is made by a single word. In some places you are
allowed to use the character `-` to indicate an unknown value.

At first the information about your observatory site must be added to
the corresponding parameter file `sites.dat`. From the AIRTOOLS
application’s “Edit” menu select “Edit Site Parameters”. This will start
a simple text editor (called *mousepad*). The parameter file should have
a few entries already, which can be used as reference when adding a new
line for your site. The column description is as follows:

  - ID:  
    This is a unique short identifier for your site (three letters)
  - location:  
    A unique single word for the name of your observatory location. The
    previously used entry of the observatory site during project setup
    must match one of these.
  - long:  
    Geographic longitude in degrees, negative for a location east of
    Greenwich meridian.
  - lat:  
    Geographic latitude in degrees, negative for a locations south of
    the equator.
  - alt:  
    Altitude of your observatory in meters.

Save your edits and close the text editor.

The next information you have to provide is those of the instrumentation
you have used. Open the parameter file `camera.dat` by selecting “Edit”
and “Edit Camera Parameters”. Each combination of telescope and camera
must have a dedicated entry. Use the existing sample entries as a
reference for your newly added lines. The columns used are:

  - tel:  
    Unique identifier for the telescope and camera, using 3-6
    alphanumeric characters.
  - flen:  
    Focal length of the telescope or camera lens in mm.
  - aperture:  
    Open aperture of the telescope or camera lens in mm.
  - fratio:  
    F-ration of the telescope or camera, that is `flen/aperture`.
  - camera:  
    Camera model, used for your convenience only
  - camchip:  
    Camera and sensor keys used in final ICQ records of a comet
    measurement. Refer to the lists of [camera
    keys](https://cobs.si/help?page=ccd_type) and [sensor
    keys](https://cobs.si/help?page=ccd_chip). Both values have to be
    provided in a single word, using the character `/` as a delimiter.
    If you for example have used a Canon 6D DSLR for imaging then the
    correct entry would be `CDS/CFC`.
  - flip:  
    Indicate if the image data is flipped top-down (1) or not (0).
    Essentially this describes the order and interpretation of FITS
    data: If the FITS file is organized in such a way that the data of
    the bottom image row comes first and that of the top-most row latest
    then it is considered unflipped and the other way it is flipped. The
    check for image flipping is described in the next chapter.
  - rot:  
    If the camera is rotated with respect to the sky coordinate system
    then you should provide a value different from 0. If true north is
    left on your image then use a value of 90. A rough approximation is
    sufficient.
  - rawbits:  
    Original bitdepth or number of bits per pixel in a single color
    channel. Note that at start of the image reduction the counts (ADU,
    intensities) are scaled up to the 16-bit range where needed.
  - satur:  
    Saturation value. Strictly speeking the upper counts (ADU) for which
    the camera response is linear (proportional to the illumination
    intensity) must be provided. We need the value after scaling up to
    the 16-bit range, e.g. if you are using a consumer DSLR where
    response is linear up to 2/3 of its dynamic range then you should
    enter a value of 40000 approximately.
  - gain:  
    Number of electrons per ADU. Use a value of 1 if it is not known.
  - pixscale:  
    Approximate value of the size of a pixel on the sky in seconds of
    arc.
  - magzero:  
    Zeropoint of the non-calibrated instrumental magnitude scale. This
    is the magnitude of a star which yields a signal of 1 count (ADU) in
    a 1 second exposure. Initially you can use an arbitrary value but it
    is useful to refine it to something close to the zeropoint of the
    calibrated scale (see log output of your first photometric
    calibration later on)
  - ttype:  
    Telescope type: L=reflector, R=refractor, A=photo Lens
  - ctype:  
    Sensor type: CCD=monochrome CCD, DSLR=DSLR with native camera model
    RAW files, CMOS=monochrome CMOS sensor, RGGB or BGGR for a
    one-shot-color CMOS sensor with a Bayer filter matrix in the given
    layout.

Save your edits and close the text editor. After any modification you
can choose if the new parameter file is just applied to your current
project or if you like to use it in subsequent new projects.

## Raw Images and Image Set Definition

Initially the AIRTOOLS software was written to work on digital camera
raw image files. It uses a modified version of the
[dcraw](https://www.dechifro.org/dcraw/) converter (by D. Coffin).
Therefore raw images of all cameras supported by *dcraw* will be handled
by AIRTOOLS. Later on, support of single plane FITS images from CCD
cameras was added. Now, the AIRTOOLS software correctly handles
monochrome images as well as bayered images from one-shot color sensors
(e.g. CMOS sensors with an added Bayer filter matrix).

At first you must copy your unprocessed raw images to the project’s raw
directory within the Linux file system. There are different solutions to
handle this file transfer between the host operating system and a
VirtualBox guest. We suggest using an external USB pen drive or USB disk
for this purpose.

Use the file manager of your host OS to copy the raw image files to the
USB disk. Wait until all data have been completely written to disk. From
the running Linux virtual machine locate the “Devices” menu entry on the
VirtualBox VM menu at the top of the window. Select “USB” and you will
see a list of USB devices from which you need to identify and select the
USB disk. After a few seconds a new USB disk icon will apear on the
virtual Linux desktop and little after the file manager window pops up.
Use the common copy-and-paste feature to copy your raw images from the
USB disk to the appropriate raw directory of the current project.
Finally push the eject button on the USB device entry of the file
manager and close it.

You are now going to start the first AIRTOOLS task. By pressing the
“Extract basic image info” the program reads meta data of all raw
image files. At the end an editor window pops up which shows an overview
of relevant data for each image. Please note the column which holds a
4-digit image number associated with each image (first column if images
are in FITS format, second column if images are RAW files from DSLR).
Images are referenced by this number throughout the reduction process.

When a camera for which the data acquisition system delivers FITS data
is used for the first time then you should check the image orientation
on a single frame. Choose an image number referring to a raw image with
a known object - one which you can easily recognize on a sky chart. Go
to the “Misc. Tools” tab, enter the image number next to the “Load Raw
Images” button and press the button to start the SAOImage viewer. If
necessary correct the values for flipping and image rotation in the
camera parameters file (refer to the previous chapter).

Now it is time to group the individual images to form “image sets”. An
image set is a number of images of the same type and target, e.g. a
couple of dark exposures with a given exposure time or a bracketed
sequence of exposures of a comet. All image sets of the project are
described in a parameter file called `set.dat` which must be created by
yourself. From the AIRTOOLS application’s main menu select “Edit” and
“Edit Image Set Definitions”. Here is an example of a typical file
which can be used for reference:

``` 
    # 191116
    # telescope 200/800, CGEM, Pentax K5IIs, ISO 200
    # autoguider SX Lodestar, 1x1.5s, move_thres=0.07 move_relax=1.0

    # UT, S 3-4, D 2, Wo 1-2..5, Wi 3, Mo 1..4
    # h:m set  target type texp n1 n2   nref dark flat tel
    15:30 sk01 poly80s  f   1 0044 0055 -    dk11 -    GSOG # 12x 0.4s
    16:48 co01 2018N2   o 120 0178 0194 0186 dk01 sk01 GSOG # t=3
    17:29 co02 260P     o 120 0196 0217 0207 dk01 sk01 GSOG
    18:20 co03 2017T2   o 120 0221 0238 0224 dk01 sk01 GSOG
    22:08 dk01 -        d 120 0323 0341 -    -    -    GSOG # t=1
    # 191115
    18:28 dk02 -        d 120 0436 0459 -    -    -    GSOG # t=6

    # dk11 is taken from 191031
    # exclude 0228-0233 cloudy
    # 0200 satellite
```

The syntax is as follows: everything after the character `#` is
considered a comment. Each line (uncommented and non-empty) defines an
image set using at least 11 fields (words separated by spaces) which
are:

  - h:m:  
    The local time at start of observation (approximation only, not used
    by the program)
  - set:  
    The name given to the image set. We do recommend the following
    scheme: Use the first two letters to denote the image type, where
    “dk” is for darks (and bias exposures) and “sk” for sky flats,
    “co” might be used for a comet observation. Any other deep sky
    target could use two (or three) letters from the constellation it
    belongs to. After the letters use a two-digit running number, so the
    image set of the first comet target would be named `co01`, the
    second `co02` and so on. The set name is used in many places later
    on, e.g. in the file names of computed stacks and other result
    files.
  - target:  
    Short name of the target observed (up to 8 characters).
  - type:  
    Type of images (1 character): d=dark/bias, f=flat, o=lights,
    a=addition (continuation) of a previously defined image set. If you
    for some reason would like to exclude a series of images from the
    analysis (e.g. a focus sequence) but keep the information about
    those files for your record then use the character `-` in place of
    the image type.
  - texp:  
    Exposure time of a single exposure in seconds.
  - n1:  
    Number of the first image of the set.
  - n2:  
    Number of the last image of the set.
  - nref:  
    Number of the image which is used as a reference image for stacking,
    typically it should be close to the middle of the bracketed
    sequence. Not used for darks and flats.
  - dark:  
    Name of the master dark (image set name) used for calibration.
  - flat:  
    Name of the master flat used for calibration.
  - tel:  
    Identifier of the instrument (telescope/camera) used. This must
    match a valid entry in `camera.dat`.

A note about master calibration images. It is not required and not
convenient to capture darks and flats in every night. After you have
collected some calibration sets and build some master files by AIRTOOLS
it is common practice to reuse them later on. This can be done by simply
copying them over from older project directories to the current one
using the file manager.

# Image Reduction

The “Image Reduction” tab is the first tab of the AIRTOOLS graphical
user interface. Its main purpose is to provide general tasks for basic
reduction of astronomical images that is to process all of the raw image
sequences to obtain deep stacked result images of your targets.

The tasks are presented in logical order and may be run one step after
the other - which is recommended for first time users - or run
completely unattended, including astrometry and blind stacking on a
moving comet. Just select the tasks you wish to run in a row. Suitable
parameters are determined automatically and will work in most cases.

It is possible to limit the requested tasks to run on a specific image
set (or a list of image sets) by providing the set name in the
appropriate text entry field.

The final group of checkboxes determines which part of the tasks is
executed. Normally, you will want the program to process your images and
display any diagnostic plot it creates and show all result images. Image
processing is normally applied to unprocessed image sets only. You might
use the checkbox “Delete previous results” if you need to re-run a
specific task and overwrite previously generated data (for safety reason
you need to provide the desired image set names explicitely).

Pressing the “Start” button causes the selected tasks to execute. At any
time you may interrupt operation by pressing the same button again. Note
that interruption is typically defered by a couple of seconds.

## Master Darks and Flats

The processing of calibration images involves a mixture of median and
average operations. For best results it is therefore adviced to capture
multiples of 6 exposures, e.g. 6 individual dark images at any required
exposure time (and temperature) and 12 individual flat images for each
filter used.

Throughout this manual we refer to the term master dark by meaning of an
image which has not been subtracted by a bias image. Within this
definition a bias image is just a dark image at zero seconds exposure
time. Furthermore a master flat image is a dark-subtracted flat field
(where the corresponding master dark was taken at the same exposure
time, sometimes called a flat-dark).

If you don’t know your camera/sensor very well then it is a good idea to
take more exposures - especially darks. The processing routines include
measurements of the dark level in each image. A plot of this
measurements is displayed and you can evaluate the stability of the mean
intensity level. In addition, the difference of each individual dark
exposure with respect to the mean image is computed. A mosaic of the
much downsized and contrast enhanced difference images is created and
displayed. This is helpful again to judge sensor stability and health.
You may measure image intensity withing self defined regions. Note that
the mean intensity of difference images has been shifted to 1000 and
streched by a factor of 10.

The number of individual flat images has to be choosen to be large
enough to provide suitable signal to noise (not degrade the signal to
noise of the stacked target image). Also its intensity level should be
choosen carefully to provide high signal but fall well within linear
range of the sensor response. Creating high quality flat fields is a
challenge but crucial for obtaining precise photometry of extended
objects like comets.

![Variation of dark images with respect to master dark (Pentax K-5II
DSLR)](images/dark_variation2.png "Dark variation")

## Image Calibration

Image calibration involves the subtraction of the master dark image and
division by the master flat image. The calibrated images are stored in
the temporary directory defined for the project. Their name starts with
the image number associated with each individual raw image. Calibrated
images are not overwritten by default and kept throughout the project.

There is no plots or result images produced by the caibration task.
Though you may display certain calibrated images by using actions from
the “Misc. Tools” tab: enter an image set name or specific image numbers
and press the button “Load Calibrated Images”.

For DSLR images it is possible to provide a text file which holds a list
of known hot pixels. Those will be replaced by the interpolation
algorithm during the debayering step. The hot pixel file must be named
using a fixed scheme which uses the camera name you have defined in the
parameter file `camera.dat`. The appropriate line is found by matching
the telescope identifier of the image set (first column in
`camera.dat`). The camera name is given at fifth field position of that
line. If the camera identifier is `K5II` then you have to name the hot
pixel file `hotpix.k5ii.dat` and place it in the project directory. The
file contains one line per pixel, with at least 3 space separated
values. The values are image coordinates in x (starting at left with 0)
and y (starting at top with 0) and a third fixed value of 0.

In addition it is possible to manually create masks of bad image regions
where necessary (e.g. satellite trails) on calibrated images. Load the
calibrated images and use SAOImage regions to draw around affected
areas. Save the regions file under the `bgvar` subdirectory using a name
containing the given image number, e.g. `0003.bad.reg`. Those image
regions will be excluded from the stacking process later on.

## Background evaluation

Often, observations are carried out under non-perfect conditions. If you
plan to estimate photometric magnitudes from extended sources, then it
is important to carefully check image quality and possibly reject some
exposures from stacking of a long sequence of images. Therefore a check
of variation in the sky background has been added to the processing
pipeline. At first, a downsized background map is created for each image
and the average intensity level is plotted.

![Background intensity (3 image sets)](images/gsog.bg.png
"Background intensity")

Then an average background image is created for each image set as
reference and difference images are created for each individual
exposure. A mosaic of those thumbnail difference images is finally
displayed.

![Background variation (2 different image sets)](images/bgvar.png
"Background variation")

## Image Registration

The stacking process involves several steps. At first, sources (stars)
are extracted for each calibrated image. Then sources are matched with
respect to the reference image of the given set. Some of the brighter,
unsaturated stars are used to measure relative brightness between images
and an average value of star size (full width at half maximum). Those
values are plotted to allow to quantify image quality and sky
conditions.

If some of your images have signs of much degraded quality then you
might wish to exclude them from any further processing. To do so, go to
the “Edit” menu and open the “Project Settings”. Add the corresponding
image numbers to the string variable `AI_EXCLUDE` (space separated four
digit numbers). Save your edits and close the text editor.

![Mag difference](images/gsog.dmag.png "Mag difference")

![FWHM of stars](images/gsog.fwhm.png "FWHM")

## Stacking and Astrometry

Finally the images are projected to the reference image arbitrary
coordinate system and co-added. The stacked image is used to create an
object catalog. Stellar sources of this catalog are matched against a
local copy of the Tycho2 star catalog to obtain a first astrometric
solution (using an offline Astrometry.net solver). In a second step a
global model is fitted (using online UCAC-4 catalog) over the whole
image including to map some degree of distortion. This new WCS model is
saved and used later on to identify objects from photometric catalogs.
The overall astrometric accuracy is printed to the log output and
several diagnostic plots are created to show deviations from catalog
position in different axes, a distortion map showing pixel scale
variation and a sky chart with detected sources.

![Distortion map (8" Newton f/4, Pentax K-5II)](images/distortion2.png
"Distortion map")

With the help of the astrometric solution and comet ephemeris data
fetched from MPC it is possible to predict the comet motion between
individual exposures and use this information to do blind stacking on
the comet.

The resulting output images have names starting with the image set name.
Stacks centered on the moving comet have a fixed string suffix of `_m`
after the set name. Images consist of 16bit integer data and are either
in PGM (monochrome, gray image) or PPM (RGB color image) format. The
choice of these formats over FITS is mainly due to historic reasons -
the software originally was written to reduce DSLR images only - and
because many of the underlying image reduction software programs simply
do not operate on (RGB-) FITS images. Image metadata are stored in
associated ASCII header files using the file extension `.head`.

# Large Aperture Comet Photometry

## Comet Observation

## PSF Extraction and Star Removal

## Measuring the Comet

## Photometric Calibration
