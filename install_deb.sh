#!/bin/bash

# download and install airtools packages from github

# trap any error
trap 'echo ERROR: program aborted on line $LINENO.; exit -1' ERR

# create log file
touch install.log
chown 1000:1000 install.log
exec >  >(tee -ia install.log)
exec 2> >(tee -ia install.log >&2)

# process command line options
pkglist="airtools-core airtools airtools-doc"
pkgothers="cfitsio-examples missfits scamp sextractor skymaker stiff swarp stilts"
svnopts="--non-interactive"
for i in $(seq 1 10)
do
    test "$1" == "-n" && do_not_install=1 && shift 1
    test "$1" == "-r" && svnopts="$svnopts -r $2" && shift 2
    test "$1" == "-a" && pkglist="$pkglist $pkgothers" && shift 1

    test "$1" == "-h" &&
	echo "usage: install_deb.sh [-a] [pkg1] [pkg2] ..." && exit 1
    test "${1:0:1}" == "-" &&
	echo "ERROR: unknown option $1." && exit -1
done
packages=${@:-"$pkglist"}

echo "
Starting $(basename $0) at $(date) ..."
sleep 3
test "$DEBUG" && echo packages=$packages && set -x || true

# determine download url depending on distribution name
echo "# Current Linux distribution:"
lsb_release -idrc
dist=$(lsb_release -s -c)
# mapping linuxmint to ubuntu distribution it is based on
test "$dist" == "tessa" && dist=bionic &&
    echo "# mapping to ubuntu $dist"
sleep 3
url=https://github.com/ewelot/airtools-deb.git
ddir=/opt/airtools-deb/$dist
test ! -d $ddir && mkdir -p $ddir

# install subversion
str=$(dpkg -l | grep "^ii  subversion " || true)
if [ -z "$str" ]
then
    apt-get update
    apt-get -y install subversion
fi

# download packages
echo "
Starting download ($dist) ..."
sleep 3
if [ "$http_proxy" ]
then
   set - ${http_proxy//:/ } && ph=${2#//} && pp=${3%/}
   svnopts="$svnopts --config-option servers:global:http-proxy-host=$ph"
   svnopts="$svnopts --config-option servers:global:http-proxy-port=$pp"
fi
(cd $ddir
svn $svnopts info main/
if [ $? -eq 0 ]
then
    svn $svnopts revert -R main/
    svn $svnopts update main/
else
    svn $svnopts checkout $url/trunk/$dist/main
fi
)

# add local package repository
aptsrc=/etc/apt/sources.list.d/airtools-deb.list
if [ ! -e $aptsrc ]
then
    echo "deb [trusted=yes] file://$ddir main/" > $aptsrc
fi
rm -f $ddir/main/Release
apt-get update

# install airtools
if [ "$do_not_install" ]
then
    echo "" && echo "Script $0 finished (without installation)."
    exit 0
fi
# check for other apt/dpkg processes holding lock file
while [ "$(lsof /var/lib/dpkg/lock 2>/dev/null)" ]
do
    echo ""
    echo "WARNING: Another system process in blocking installation."
    echo "    It might be necessary to wait a few minutes to allow"
    echo "    that process to finish and release the lock."
    printf "    Waiting 1 minute now ..."
    for i in $(seq 1 6); do
    	for k in $(seq 1 5); do sleep 2; printf "."; done
        test ! "$(lsof /var/lib/dpkg/lock 2>/dev/null)" && break
    done
    printf "\n"
done
# handle openjfx package peculiarities in Ubuntu 18.04
if [ $dist == "bionic" ]
then
    v=$(apt-cache policy openjfx | sed -e 's,^ *,,' | grep "^8" | cut -d ' ' -f1)
    if [ "$v" ]
    then
        echo "
Installing JavaFX8 and pinning packages ..."
        sleep 3
        apt-get -y install libopenjfx-jni=$v libopenjfx-java=$v openjfx=$v
        for p in libopenjfx-jni libopenjfx-java openjfx
        do
            echo $p hold | dpkg --set-selections
        done
    fi
fi
echo "
Installing $packages ..."
sleep 3
apt-get -y --allow-unauthenticated install $packages
apt-get clean
echo ""
echo "Installation finished."
echo "For AIRTOOLS documentation see /usr/share/doc/airtools-doc/"

exit 0
