#!/bin/bash

################################################################
# setup_airdeb.sh [-h] [-p proxy] [-l user]
#
# setup airtools software on Debian/Ubuntu Linux based Live-CD
# e.g. using live cd ISO image in a virtual PC (VirtualBox)
#
# tested on
#   debian  8.4 (xfce, mate, gnome, kde)
#   ubuntu 16.04 (also ubuntu-gnome, ubuntu-mate)
#   xubuntu 16.04 15.10 14.04
#   linuxmint 17.3 (cinnamon, xfce)
################################################################
VERSION="1.0.1"
VINFO="T. Lehmann, Jun. 2016"
PINFO="\
    options:
      h         show this help text
      p proxy   use given proxy (http://proxyhost:port)
      l user    get files from VirtualBox host using given user name
    parameters:
      -
"
CHANGELOG="
    1.0.1 - 03 Jun 2016
         * fixed typo and improved some text messages
         * added --no-wrap option to zenity commands (question dialogs)

    1.0  - 01 Jun 2016
         * free additional space by removing development packages
         * determine latest release by using github api

    0.9  - 31 May 2016
         * added support for wide range of debian/ubuntu based distributions
         * move install and build files to /tmp

    0.8  - 21 May 2016
         * initial version for xubuntu 14.04 and debian 8.4
"


#--------------------
#   user definitions
#--------------------
repo=https://github.com/ewelot/airtools
extdir=https://github.com/ewelot/temp/raw/master
vboxdir=http://download.virtualbox.org/virtualbox
demo=http://youtu.be/sK9D_M06ovA

prog=$(readlink -e $0)
builddir=/tmp/build-airtools
sdir=astro/160224   # relative to $HOME
log=$HOME/install.log


#--------------------
#   functions
#--------------------
shorthelp ()
{
    echo "usage: $(basename $0) [-h] [-p http://proxyhost:port] [-l localuser] [-s]"
}


#--------------------
#   get options
#--------------------
luser=""        # local user on vm host
opts=""
use_local_sources=""
while getopts hp:l:s c
do
    case $c in
        h)  shorthelp
            exit -1
            ;;
        p)  export http_proxy=$OPTARG
            export https_proxy=$OPTARG
            export no_proxy="10.0.2.2"
            echo "Defaults env_keep = \"http_proxy https_proxy ftp_proxy no_proxy\"" > /tmp/proxy
            sudo cp /tmp/proxy /etc/sudoers.d/proxy
            cp /etc/environment /tmp/
            echo "export http_proxy=$http_proxy" >> /tmp/environment
            echo "export https_proxy=$https_proxy" >> /tmp/environment
            echo "export no_proxy=$no_proxy" >> /tmp/environment
            test ! -f /etc/environment.orig && sudo mv /etc/environment /etc/environment.orig
            sudo cp /tmp/environment /etc/environment
            opts="$opts -p $http_proxy"
            ;;
        l)  luser=$OPTARG
            extdir="10.0.2.2/~"$luser
            vboxdir="10.0.2.2/~"$luser
            opts="$opts -l $luser"
            ;;
        s)  use_local_sources=1
            opts="$opts -s"
            ;;
        \?) exit -1
            ;;
    esac
done
shift `expr $OPTIND - 1`


#--------------------
#   get parameter
#--------------------
if [ $# -gt 0 ]
then
  shorthelp; exit -1
fi


#--------------------
#   checkings
#--------------------


#--------------------
#   start
#--------------------
#tmp1=$(mktemp "/tmp/tmp_txt1_$$.XXXXXX")

# get release name (e.g. xenial)
lsb_release -a | tee -a $log
release=$(lsb_release -s -c)


# check if zenity is availably
zen=""
type -p zenity > /dev/null && zen=1


# check if airtools is already installed
if type -p airfun.sh > /dev/null
then
    text="The AIRTOOLS software is already installed.
It is not recommended to continue and repeat
installation."

    if [ "$zen" ]
    then
        if answer=$(zenity --no-wrap --question --title "Install AIRTOOLS" \
            --text "$text\n\nAbort?" 2>/dev/null); then
            exit -1;
        fi
    else
        echo -e "\n$text\n"
        read -p "Abort?  [Y/n]  " -r -n 1 answer
        echo
        $answer=${answer,,}
        test "$answer" != "n" && exit -1
    fi
fi


# check if we run ubuntu-mate desktop (requires some tweaks)
ubuntu_mate=""
dpkg -l | grep -q "ii[ ]*ubuntu-mate-core" &&
    ubuntu_mate=1


# ubuntu 16.04 requires additional repositories
case $release in
    xenial) sudo apt-add-repository universe
            sudo apt-add-repository multiverse
            ;;
esac


# update package cache
export DEBIAN_FRONTEND=noninteractive
touch -d 'now - 1 day' /tmp/tstamp
if [ /tmp/tstamp -nt /var/cache/apt/pkgcache.bin ] &&
   [ /tmp/tstamp -nt /var/cache/apt/archives ]
then
    echo
    echo "Update package cache ..."
    sudo apt-get update -q
fi

# install zenity, wget, curl
(dpkg -l | grep -q "ii[ ]*zenity " &&
dpkg -l | grep -q "ii[ ]*wget " && 
dpkg -l | grep -q "ii[ ]*curl ") ||
    sudo apt-get -y install zenity wget curl
sudo apt-get clean
type -p zenity > /dev/null && zen=1

# find airtools sources
if [ "$use_local_sources" ] && [ "$luser" ]
then
    url=""
    tag=""
    sources="10.0.2.2/~"$luser/airtools.tar.gz
else
    # grab latest release
    url=$(curl -s ${repo/github.com/api.github.com\/repos}/releases | \
        grep tarball_url | head -n 1 | cut -d '"' -f 4)
    test -z "$url" &&
        echo "ERROR: cannot determine latest release tag." >&2 &&
        read && exit -1
    tag=$(basename $url)
    sources=https://github.com/ewelot/airtools/archive/$tag.tar.gz
fi
echo "sources=$sources" | tee -a $log


# install build-essential (required on ubuntu-mate 16.04)
if [ "$ubuntu_mate" ]
then
    dpkg -l | grep -q "ii[ ]*build-essential" ||
        sudo apt-get -y install build-essential
fi


# disable some autostart applications
for app in ubuntu-mate-welcome
do
    test -e ~/.config/autostart/$app.desktop &&
        rm ~/.config/autostart/$app.desktop
done


# enable large screen
cd ~
h=$(xwininfo -root | grep Height | awk '{print $2}')
test $h -le 800 &&
    m=$(xrandr 2>/dev/null | grep "^ " | grep x | tr 'x' ' ' | awk '{if($2>800){print $0}}' | \
        sort -nr -k2 | tail -1 | awk '{print $1"x"$2}') &&
    test "$m" && xrandr -s $m


# if required install VirtualBox Guest Additions
h=$(xwininfo -root | grep Height | awk '{print $2}')
if [ $h -le 800 ]
then
    vbios=$(sudo dmidecode -s bios-version)
    if [ "$vbios" != "VirtualBox" ]
    then
        text="It appears that you are not running a VirtualBox
VM software and therefore must set a larger screen
size manually (see documentation of your VM software)."

        if [ "$zen" ]
        then
            if ! answer=$(zenity --no-wrap --question --title "No VirtualBox" \
                --text "$text\n\nContinue anyway?" 2>/dev/null); then
                exit -1;
            fi
        else
            echo -e "\n$text\n"
            read -p "Continue anyway?  [Y/n]  " -r -n 1 answer
            echo
            $answer=${answer,,}
            test "$answer" != "n" && exit -1
        fi
    else
    
        # determine display manager which is going to be restarted
        # after installation of VirtualBox Guest Additions
        dm=""
        test -z "$dm" && pgrep -l lightdm >/dev/null && dm=lightdm
        test -z "$dm" && pgrep -l gdm3 >/dev/null && dm=gdm3
        test -z "$dm" && pgrep -l gdm >/dev/null && dm=gdm
        test -z "$dm" && pgrep -l kdm >/dev/null && dm=kdm
        test -z "$dm" &&
            echo "ERROR: cannot determine display manager." >&2 &&
            read && exit -1


        # install guest additions to get larger virtual screen size
        text="The VirtualBox Guest display size is small.
It can be increased after installation of the
guest additions. To download the correct version
you must provide the current version of VirtualBox
software (see menu Help/About)."

        if [ "$zen" ]
        then
            if ! vboxvers=$(zenity --entry --title "Install VirtualBox Guest Additions" \
                --text "$text\n\nPlease enter version number, e.g. 5.0.20:" 2>/dev/null); then
                exit -1;
            fi
        else
            echo -e "\n$text\n"
            read -p "Please enter version number, e.g. 5.0.20:  " -r vboxvers
            echo
        fi
        echo "Try to install Virtualbox Guest Additions version $vboxvers ..."
        #sudo apt-get install virtualbox-guest-x11 virtualbox-guest-dkms
        
        #sudo apt-get install virtualbox-guest-additions-iso
        #test ! -d /mnt/iso && sudo mkdir /mnt/iso
        #sudo mount -o loop /usr/share/virtualbox/VBoxGuestAdditions.iso /mnt/iso
        
        rm -f VBoxGuestAdditions_$vboxvers.iso
        wget $vboxdir/$vboxvers/VBoxGuestAdditions_$vboxvers.iso
        test ! -f VBoxGuestAdditions_$vboxvers.iso &&
            echo "ERROR: downloading VBoxGuestAdditions ISO failed." &&
            read && exit -1
        test ! -d /mnt/vboxaddiso && sudo mkdir /mnt/vboxaddiso || true
        sudo mount -o loop VBoxGuestAdditions_$vboxvers.iso /mnt/vboxaddiso
        sudo bash /mnt/vboxaddiso/VBoxLinuxAdditions.run
        echo
        # "Building ... module"  takes some time
        sudo umount /mnt/vboxaddiso

        # avoid VBoxClient error messages: Failed to connect to the VirtualBox
        #   kernel service, verr_access_denied
        # disable multiple X11 startup scripts for vboxclient
        #   you must start VBoxClient-all later to activate shared clipboard
        for f in \
            /etc/X11/Xsession.d/98vboxadd-xclient \
            /etc/X11/xinit/xinitrc.d/98vboxadd-xclient.sh \
            /etc/xdg/autostart/vboxclient.desktop
        do
            test -f $f && sudo mv $f /root/${f//\//_}
        done

        # script to run on next login
        cat <<EOF > /tmp/continue.sh
#!/bin/bash
sleep 3
bash $prog $opts
EOF
        chmod u+x /tmp/continue.sh

        # add autostart script
        test -d ~/.config/autostart/ || mkdir ~/.config/autostart/
        if [ "$ubuntu_mate" ]
        then
        cat <<EOF > ~/.config/autostart/continue.desktop
[Desktop Entry]
Type=Application
Name=Continue Install
Exec=x-terminal-emulator -e /tmp/continue.sh
EOF
        else
        cat <<EOF > ~/.config/autostart/continue.desktop
[Desktop Entry]
Type=Application
Name=Continue Install
Exec=/tmp/continue.sh
Terminal=true
EOF
        fi

        # restart X11 to initialize new vbox guest modules
        cat <<EOF > /tmp/restart-x11.sh
set -x
ps uxaw | grep -i vbox
lsmod | grep vbox
sudo service $dm stop
sleep 2
ps uxaw | grep -i vbox
sudo killall VBoxClient
sudo killall VBoxService
sudo modprobe -r vboxvideo vboxsf
rm -f ~/.vboxclient*
sudo modprobe -a vboxguest vboxsf vboxvideo
sudo VBoxService -v -p /var/run/vboxadd-service.pid -l /var/log/vboxadd-service.log
lsmod | grep vbox
VBoxClient-all
sleep 2
ps uxaw | grep -i vbox
sudo service $dm start
EOF
        chmod u+x /tmp/restart-x11.sh
        nohup /tmp/restart-x11.sh > restart-x11.log 2>&1
        exit 0
    fi
fi



# activate clipboard integration
# note: does not always work
# killall VBoxClient
# rm -f .vboxclient*
# VBoxClient-all
type -p VBoxClient > /dev/null &&
    ! pgrep -l -f "VBoxClient --clipboard" > /dev/null &&
    VBoxClient --clipboard
# remove iso
rm -f VBoxGuestAdditions_*.iso


# airtools
version=$(basename $sources)
test "$tag" && version="Version $tag"
text="The AIRTOOLS software ($version)
can be installed now.

This includes download of all required
software components and sample data
(~200MB) and the full compilation and
installation procedure.
"
if ! answer=$(zenity --no-wrap --question --title "Install AIRTOOLS" \
    --text "$text\n\nContinue?" 2>/dev/null); then
    exit -1;
fi


test ! -d $builddir && mkdir -p $builddir || true
test ! -d ~/astro && mkdir ~/astro || true
cd $builddir
(
echo
echo "Download airtools package ..."
wget --content-disposition $sources
test $? -ne 0 &&
    echo "ERROR: download of $sources failed" >&2 && read && exit -1 
echo "Download third party software bundle ..."
wget $extdir/bundle3rd.tar
test $? -ne 0 &&
    echo "ERROR: download of bundle3rd.tar failed" >&2 && read && exit -1 
echo "Download sample data ..."
wget $extdir/sample_160224.tar.gz
test $? -ne 0 &&
    echo "ERROR: download of sample_160224.tar.gz failed" >&2 && read && exit -1 

echo
echo "Unpacking archives ..."
sleep 4
tar xf airtools*.tar.gz
test $? -ne 0 &&
    echo "ERROR: unpacking of airtools failed" >&2 && read && exit -1
tar xf bundle3rd.tar
test $? -ne 0 &&
    echo "ERROR: unpacking of bundle3rd failed" >&2 && read && exit -1
tar -C ~/astro -xf sample_160224.tar.gz
test $? -ne 0 &&
    echo "ERROR: unpacking of sample data failed" >&2 && read && exit -1
) 2>&1 | tee -a $log


(
echo
echo "Install build dependencies ..."
sleep 4
sudo apt-get -y install imagemagick xpa-tools wcstools gnuplot-x11 \
    librsvg2-bin potrace exiftool curl wget gawk default-jre
sudo apt-get clean
sudo apt-get -y install libnetpbm10-dev libjasper-dev libjpeg-dev libcfitsio3-dev \
    libtiff5-dev libfftw3-dev libblas-dev libatlas-base-dev \
    libplplot-dev plplot12-driver-xwin plplot12-driver-cairo libshp-dev
sudo apt-get clean
df /
) 2>&1 | tee -a $log

cd airtools-*
(
echo
echo "Compile/install airtools software ..."
sleep 4
make
test $? -ne 0 &&
    echo "ERROR: make failed" >&2 && read && exit -1
sudo make install
) 2>&1 | tee -a $log

(
echo
echo "Compile/install required third party software ..."
sleep 4
make externc
test $? -ne 0 &&
    echo "ERROR: make externc failed" >&2 && read && exit -1
sudo make install_externc
make astromatic
test $? -ne 0 &&
    echo "ERROR: make astromatic failed" >&2 && read && exit -1
sudo make install_astromatic
sudo make install_ds9
sudo make install_stilts
) 2>&1 | tee -a $log
cd

(
echo
echo "Remove software packages which are not required anymore ..."
sleep 4
sudo apt-get -y remove libnetpbm10-dev libjasper-dev libjpeg-dev libcfitsio3-dev \
    libtiff5-dev libfftw3-dev libblas-dev libatlas-base-dev libplplot-dev libshp-dev
plist=$(apt-get -q -q -s autoremove | awk '{print $2}' | \
    grep -E -- "-dev$|^libqt|^libplplot")
sudo apt-get -y remove $plist
plist=$(apt-get -q -q -s autoremove | awk '{print $2}' | \
    grep -E "cmake|mysql-common|libcfitsio-doc|libtiffxx|libmng")
test "$plist" && sudo apt-get -y remove $plist
) 2>&1 | tee -a $log


(
echo "Remove buggy plplot12-driver-qt ..."
sleep 4
dpkg -l | grep -q "ii[ ]*plplot12-driver-qt" &&
    sudo apt-get -y remove plplot12-driver-qt
) 2>&1 | tee -a $log


# on ubuntu 16.04 variants we need to force small font size in SAOImage ds9
# (otherwise it uses 12pt)
case $release in
    xenial) test ! -f ~/.ds9.prf && echo "global pds9
array set pds9 { nan,msg White dialog motif text,font courier samp 1 \
font,msg Helvetica threads 2 font,weight normal automarker 1 bg,msg White \
language locale text,font,weight normal dialog,all 0 nan white \
font,slant roman confirm 1 backup 1 language,dir {} font helvetica \
language,name English bg white xpa 1 text,font,msg Courier tcl 0 \
dialog,center 0 font,size 9 text,font,slant roman text,font,size 9 }" > ~/.ds9.prf
            ;;
esac
echo "# free" >> $log
free >> $log
echo "# df" >> $log
df >> $log


echo
echo
echo "#############################"
echo "    Installation finished"
echo "#############################"
echo

sleep 3
text="There are temporary files from the
download/installation process which can
be deleted now to free some disk space."
if answer=$(zenity --no-wrap --question --title "Temp files" \
    --text "$text\n\nDelete temp files?" 2>/dev/null); then
    rm -rf $builddir
    rm -f ~/.config/autostart/continue.desktop
fi

clear
free=$(echo $(df --output=avail -h $HOME/$sdir | tail -1))
text="We are ready to start the AIRTOOLS
software using sample data.

You could now follow the steps from the screencast
demo at   <i>$demo</i>
If you intent to walk through all analysis tasks
you will need about 200MB of free disk space.

Current free disk space: $free
Location of sample data: \$HOME/$sdir
"
if answer=$(zenity --no-wrap --question --title "Start AIRTOOLS" \
    --text "$text\n\nStart airtools using sample data?" 2>/dev/null); then
    echo
    echo "Starting airtools ..."
    cd $sdir
    nohup ./startup.sh > startup.log 2>&1
fi


#--------------------
#   clean-up
#--------------------
sleep 3
exit 0

