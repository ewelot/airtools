# AIRTOOLS installation and testing from pre-build OVA appliance

## Introduction

The AIRTOOLS software is running under the Linux operating system.
To install it on any host operating sytem you can use a virtual computer
environment, e.g. by means of the VirtualBox software. The easiest way to
accomplish this task is to import a pre-build appliance of the virtual Linux
computer with all software components set up.
Finally, the virtual computer with ready to use AIRTOOLS software appears just
like an additional application window on your host computer.

The following instructions are meant to supply all necessary information
to get the installation done within a few minutes and start a first AIRTOOLS
project using sample data.


## VirtualBox software

- Download and install the Oracle VirtualBox software appropriate for your
  host computer operating system from the [download page](https://www.virtualbox.org/wiki/Downloads)

- Download and install the VirtualBox Extension Pack from the same
  web page.


## Importing appliance

- Download the [Xubuntu-AIRTOOLS appliance](http://fg-kometen.vdsastro.de/airtools/vm/xubuntu-airtools.ova)

- Start the Oracle VM VirtualBox Manager, choose File/Import Appliance and
  select the local .ova file

- Make sure there is sufficient free disk space in the virtual machine base
  folder. The .ova file size is only 1.6 GB but it contains the whole
  Linux operating system and all required software packages to run the AIRTOOLS
  software. It initially expands to about 6 GB of disk space but grows
  dynamically up to the virtual disk size of 50 GB.

- Virtual machine settings are choosen to impose low hardware requirements: it
  uses 3 CPU cores and 4 GB of physical RAM. This is sufficient to run the
  AIRTOOLS software even on large images (e.g. 60 Mpix color images). It is
  possible to adjust those settings at any time later on.

- Start importing into VirtualBox by clicking the button "Import".


## Starting the virtual Linux OS

- You are now ready to "boot" the virtual Linux computer from the VirtualBox
  Manager or create a desktop shortcut (see pop-up menu when right-clicking on
  the machine name) and start from there. It will automatically login to the
  Xubuntu desktop with the user name "user" (password is "user").

- There might be messages written at the top of the window (about mouse
  integration and alike) which you can savely ignore.

- You might need to adjust the keyboard language. This is done by clicking the
  appropriate panel applet with the name "EN" and choosing an item from the
  drop-down list.


## Create first AIRTOOLS project

- Start Airtools (double-click the icon)

- Accept default directories during setup

- Create a new project appropriate for the sample data (see next chapter):
  - choose date of observations by using the calendar date picker:
  2021 January 15th
  - choose observatory site Nerpio from dropdown list

- Optionally fill in observer details

- Remember the path to the raw images directory (with the default settings it
    should be /home/user/raw/210115)

- Press "Apply"


## Copy observations data files

Observations data files (raw FITS images) must be placed into the appropriate
folder on the virtual Linux computer. Here we describe the use of the new
VirtualBox File Manager for this purpose. For other methods of data transfer
between host and virtual computer (e.g. using a shared folder or using external
USB storage) please refer to the VirtualBox documentation.

- Download [sample data](http://fg-kometen.vdsastro.de/airtools/testdata/210115_snv_raw.zip)
  and extract files and directories in a local folder of your host computer.

- Locate the VirtualBox menubar (above the virtual Linux Desktop) and
  select Machine/File Manager
  
- Enter user name "user" and password "user" and create a new session

- Copy the locally extracted folder 210115 from the host (left panel) into the
  guest file system (inside the virtual computer) below the folder /home/user/raw

- Close the session and the VirtualBox File Manager


## Image reduction

The "Image Reduction" tab of the AIRTOOLS graphical user interface contains
all tasks to calibrate and stack images automatically.

- Select the first task "Extract basic image info" and run it via the button
  "Start"

- Next you need to allocate images to "image sets" of darks, flats and lights:
  from the menu choose Edit/Edit Image Set Definitions, create an empty file
  set.dat and copy and paste the following contents:

```
# 2021-01-15
# Nerpio Veloce

# LT
# h:m set  target type texp n1 n2   nref dark flat  tel  # notes
06:39 dk01 dark     d   5 0001 0010 -    -    -     SNV
20:01 co01 398P     o  60 0011 0018 0014 dk02 sk01  SNV  # green filter
06:52 sk01 skyflat  f   8 0024 0035 -    dk01 -     SNV
06:58 dk02 dark     d 120 0036 0050 -    -    -     SNV
``` 

- Check for a valid entry of SNV in camera.dat (Edit/Edit Camera Parameters),

- Run every single task in the given order until the comet stack is created:
  select a task, activate all processing options (Process ..., View ..., Show ...)
  and press the "Start" button 

- Evaluate results (new plots and images displayed) from each task

- Note: It is allowed to activate and execute several/all tasks in a single run
  but it is not recommended for the beginner.


## SAOImage display

- Get familiar with the SAOImage display application and examine the stacked
  images:
  - use right mouse button for brightness/contrast adjustment
  - use middle mouse button for pan, scroll wheel for zoom
  - use left mouse to place/move/edit regions
  - use tab to cycle through several loaded images (frames)

- Also try menuitems from the Zoom, Scale and Region menues and buttons from
  the two button bars above the image (e.g. region/save)


## Comet Photometry

- Run every single task in the given order (by clicking the named button)

- Many tasks provide a window to adjust user settings whose default settings
  are appropriate in most cases


## Documentation

- Please refer to the most up-to-date [AIRTOOLS manual](https://github.com/ewelot/airtools/blob/master/doc/manual-en.md)


## Help/Contact

- Please do not hesitate to ask questions or send feedback to
  t.lehmann@mailbox.org


Good luck and thanks for trying!

Thomas Lehmann
