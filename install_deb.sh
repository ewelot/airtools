#!/bin/bash

# download and install airtools packages from github
echo "Starting $0 at $(date) ..."
test "$DEBUG" && set -x
#trap 'echo ERROR: program aborted on line $LINENO.; exit -1' ERR

# process command line options
package=airtools
test "$1" == "-n" && do_not_install=1 && shift 1
test "$1" == "-c" && package="airtools-core" && shift 1

# determine download url depending on distribution name
dist=$(lsb_release -s -c)
url=https://github.com/ewelot/airtools-deb.git
ddir=/opt/airtools-deb/$dist
test ! -d $ddir && mkdir -p $ddir

# install subversion
dpkg -l | grep -q "^ii  subversion "
test $? -ne 0 && (
    apt-get update
    apt-get -y install subversion)

# download packages
echo "
Starting download ($dist) ..."
sleep 2
test "$http_proxy" && set - ${http_proxy//:/ } && ph=${2#//} && pp=${3%/} &&
   svnopts="--config-option servers:global:http-proxy-host=$ph" &&
   svnopts="$svnopts --config-option servers:global:http-proxy-port=$pp"
(cd $ddir && svn $svnopts checkout $url/trunk/$dist/main)

# add local package repository
aptsrc=/etc/apt/sources.list.d/airtools-deb.list
test ! -e $aptsrc && echo "deb file://$ddir main/" > $aptsrc
apt-get update

# install airtools
test "$do_not_install" &&
    echo "" && echo "Script $0 finished (without installation)." &&
    exit 0
echo "
Installing $package ..."
sleep 2
apt-get -y --allow-unauthenticated install $package
echo ""
echo "Script $0 finished."

exit 0
