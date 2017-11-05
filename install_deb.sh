#!/bin/bash

# download and install airtools packages from github

# trap any error
trap 'echo ERROR: program aborted on line $LINENO.; exit -1' ERR

# create log file
touch /tmp/install.log
chmod a+r /tmp/install.log
exec >  >(tee -ia /tmp/install.log)
exec 2> >(tee -ia /tmp/install.log >&2)

echo "
Starting $(basename $0) at $(date) ..."
sleep 3
test "$DEBUG" && set -x || true

# process command line options
packages="airtools-core airtools airtools-doc"
svnopts="--non-interactive"
test "$1" == "-n" && do_not_install=1 && shift 1
test "$1" == "-c" && packages="airtools-core" && shift 1
test "$1" == "-r" && svnopts="$svnopts -r $2" && shift 2

# determine download url depending on distribution name
dist=$(lsb_release -s -c)
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
    echo "deb file://$ddir main/" > $aptsrc
fi
rm -f $ddir/main/Release
apt-get update

# install airtools
if [ "$do_not_install" ]
then
    echo "" && echo "Script $0 finished (without installation)."
    exit 0
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
