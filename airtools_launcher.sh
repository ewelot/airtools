#!/bin/bash

########################################################################
#   airtools_launcher.sh [-h]
#
#   launcher GUI to help startup of airtools
#
########################################################################
VERSION="1.2"
VINFO="T. Lehmann, Sep. 2017"
PINFO="\
    options:
      h          show this help text
"
CHANGELOG="
    1.2  - 25 Sep 2017
        * added field 'binning' to form 'image set' and set appropriate
          header keyword after image conversion (in AIstart)
        * show progress window during image conversion and loading
          
    1.1  - 13 Sep 2017
        * added button to access help docs

    1.0  - 13 Aug 2017
        * added check for target name to better match a valid comet
          designation
        * added check for some basic FITS header keywords

    0.4  - 16 Jun 2017
        * added option -p projectdir

    0.3  - 04 Jun 2017
        * add mapping of rawfiles to rawfiles.dat

    0.2  - 18 May 2017
        * implemented final launcher form
        * added logging

    0.1  - 27 Apr 2017
        * initial version
"


#--------------------
#   user definitions
#--------------------
datadir=/usr/share/airtools
ini=$HOME/.airtools.ini
log=$HOME/airtools.log
rc=.airtoolsrc


#--------------------
#   functions
#--------------------
shorthelp ()
{
    echo "usage: $(basename $0) [-h] [-v] [-p projectdir]"
}

longhelp ()
{
    echo $(basename $0)"   $VERSION   $VINFO"
    shorthelp
    printf "$PINFO"
}

error ()
{
    f_str="$1"
    echo "ERROR:  $f_str" >&2
    exit 1
}

parse_ini ()
{
    # evaluate a given section from ini file
    # syntax for section line:          ^[sname]$    sname in a-zA-Z0-9._
    # syntax for variable setting line: ^vname=...   vname in a-zA-Z0-9._
    # syntax for comment line:          ^(spaces)#...
    # note: make sure command line settings have higher priority than
    #       ini file settings
    local fname="$1"
    local section="$2"

    test ! -f "$fname" && error "ini file '$fname' not found"
    cat "$fname" | awk -v s="$section" 'BEGIN{found=0; sline=0}{
        ltype="unknown"
        if ($1~/^\[[[:alnum:]\._]+]$/) {ltype="section"} else {
            if ($1~/^[[:alnum:]\._]+=/) {ltype="varset"} else {
                if ($1~/^[[:space:]]*(#.*|)$/) {ltype="comment"}
            }
        }
        if (ltype == "unknown") {
            found=0
            printf("echo WARNING: parse_ini did not process line %d.;\n", NR)
        }
        if (ltype == "section") {
            if (substr($1,2,length($1)-2) == s) {found=1} else {found=0}
        }
        if ((found==1) && (ltype == "varset")) {printf("%s;\n", $0)}
    }'
}

is_equal () {
    # compare two numbers
    local x=$1
    local y=$2
    test $# -ne 2 && echo "ERROR: two parameters required" >&2 && return 255
    local err
    err=$(echo $x $y | awk '{
        d=$1-$2; if (d == 0) {print 0} else {print 255}
    }')
    return $err
}

is_time () {
    local x=$1
    local err
    err=$(echo $x | awk -F ':' '{
        x=0
        if (NF!=2) x=255
        if ($1!~/^[0-9][0-9]$/ || $2!~/^[0-9][0-9]$/) x=255
        if ($1>24 || $2>59) x=255
        print x
    }')
    return $err
}

select_item () {
    # prepend "^" to item string
    local list="$1"
    local item="$2"
    local sep=";"
    echo "$list" | awk -v s="$sep" -v x="$item" '{
        n=split($0,a,s)
        for (i=1;i<=n;i++) {
            sub(/\^/,"",a[i])
            if(i>1) printf("%s", s)
            if(a[i]==x) printf("^")
            printf("%s", a[i])
        }}'
}

adderr () {
    local newmsg="$1"
    if [ -z "$errmsg" ]
    then
        errmsg="WARNING: $newmsg"
    else
        errmsg="$errmsg, $newmsg"
    fi
}


save_ini () {
    local ini=$1
    local tmp1=$(mktemp /tmp/tmp_ailaunch_XXXX.ini)
    local d
    test "$projectdir" && d=$(basename $projectdir)
    echo "[global]
basedir=$basedir
lastproject=\"$d\"
lasttmpdir=\"$tmpdir\"
lastsite=\"$lastsite\"
lastcamera=\"$lastcamera\"" >> $tmp1
    test ! -e $ini &&
        echo "# wrinting $ini" &&
        mv $tmp1 $ini &&
        return
    ! diff -q $tmp1 $ini > /dev/null &&
        echo "# updating $ini" &&
        mv $tmp1 $ini &&
        cat $ini
    rm -f $tmp1
    return
}


show_progresswindow () {
    local title="$1"
    local text="$2"
    yad --width 300 --center --skip-taskbar --borders=20 --no-buttons --title="$title" \
        --progress --pulsate --progress-text="" --text="\n\n$text\n" &
    SPLASH_PID=$!
}


stop_progresswindow () {
    kill $SPLASH_PID
    wait $SPLASH_PID 2>/dev/null
}



#--------------------
#   get options
#--------------------
cmdline="$(basename $0) $@"  # preserve command line
verbose=0
projectdir=""
has_arg_pdir=""
while getopts hvp: c
do
  case $c in
    p)  projectdir=$(realpath "$OPTARG"); has_arg_pdir=1;;
    h)  longhelp; exit -1;;
    v)  verbose=$((verbose + 1));;
    \?) shorthelp; exit -1;;
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
# start logging
exec > >(tee -a $log)
exec 2>&1
echo "
#### starting $(basename $0) v$VERSION at $(date +'%Y-%m-%d %H:%M')"

# check projectdir
test "$projectdir" && test ! -d "$projectdir" &&
    echo "ERROR: projectdir $projectdir does not exist." >&2 && exit 1
test "$projectdir" && test ! -e "$projectdir/$rc" &&
    echo "ERROR: invalid projectdir $projectdir" >&2 && exit 1

# prepend PATH to include local bin directories
for p in $HOME/bin/home $HOME/bin
do
    if [ -d "$p" ] && [[ ":$PATH:" != *":$p:"* ]]; then
        PATH="$p${PATH:+":$PATH"}"
    fi
done

! type -p airfun.sh > /dev/null 2>&1 &&
    error "missing function definition file airfun.sh
    (PATH=$PATH)"
echo "# loading $(which airfun.sh)"
. airfun.sh
echo "# AI_VERSION=$AI_VERSION"



#--------------------
#   start
#--------------------
# parsing global settings from ini file
basedir=""      # base directory of airtools projects
lastproject=""  # last project directory
lasttmpdir=""   # last temp directory
lastsite=""     # last site
lastcamera=""   # last camera


test -e "$ini" && eval $(parse_ini $ini global)
if [ "$projectdir" ]
then
    basedir=$(dirname $projectdir)
    source $projectdir/$rc
fi
test "$basedir" && echo "# basedir=$basedir"

# general options for yad
yadopts="--center --skip-taskbar --width 450 --borders=10 --wrap"

# find documentation
x=/usr/share/doc/airtools-doc
y="manual-"${LANG%_*}".html"
test ! -e $x/$y && y="manual-en.html"
test ! -e $x/$y && y=""
test ! -e $x/$y && x=/usr/share/doc/airtools-core
docu=$x/$y


#---------------------
#   project settings
#---------------------
# a project corresponds to an observing session of a single night at a given site
# it might have multiple targets, observed with different instruments

# form 1
# open existing airtools project
# start new airtools project (new observation)
# basedir ... base directory of airtools projects
# obsday  ... day of observation (local date, begin of night)
# tempdir ... temporary directory
# rawdir  ... directory with original raw images files (optional)
# site    ... observatory site definition
title="AIRTOOLS - Project"
echo "# form: $title"
formOK=""
errmsg=""
tmpdir=$lasttmpdir
test -z "$tmpdir" && tmpdir="/tmp"
site=""
test "$has_arg_pdir" && formOK=1
while [ ! "$formOK" ]
do
    # get list of existing projects
    projectlist=""
    latestlist=""
    if [ "$basedir" ] && [ -d $basedir ]
    then
        projectlist=$(ls $basedir/*/$rc 2>/dev/null | \
            awk -F '/' '{i=NF-1; printf(";%s", $i)}')
        latestlist=$(ls -t $basedir/*/$rc 2>/dev/null | head -10 | \
            awk -F '/' '{i=NF-1; printf(";%s", $i)}')
    fi

    # locate sites.dat
    sitesdat=""
    for d in $lastwdir $basedir /usr/local/share/airtools $datadir
    do
        test -d $d && test -e $d/sites.dat && sitesdat=$d/sites.dat && break
    done

    # get list of available sites
    newsite="[add new site]"
    test "$sitesdat" && test -e $sitesdat &&
        echo "# sitesdat=$sitesdat" &&
        siteslist=$(grep -v "^#" $sitesdat | grep "[[:alnum:]]" | awk '{printf(";%s (ID=%s)", $2, $1)}')
    siteslist="$newsite$siteslist"
    # select lastsite
    test "$lastsite" && siteslist=$(select_item "$siteslist" "$lastsite")


    txt="Choose to open an already existing project folder or \
create a new project by filling in the lower entries of this form\n"

    values=$(yad $yadopts --title="$title" \
        --text="$txt<span foreground='red'>$errmsg</span>" \
        --form \
        --date-format="%Y-%m-%d" --separator="|" --item-separator=";" \
        --field="<b>Open existing project</b>:LBL"  "" \
        --field="Latest Projects::CB"               "$latestlist" \
        --field="All Existing Projects::CB"         "$projectlist" \
        --field="\n:LBL" "" \
        --field="<b>Create a new project</b>:LBL"   "" \
        --field="Base Directory for Projects::MDIR" "$basedir" \
        --field="Date of observation::DT"           "" \
        --field="Temporary Directory::MDIR"         "$tmpdir" \
        --field="Observatory Site::CB"              "$siteslist" \
        --field="\n:LBL" "" \
        --button=gtk-help:"xdg-open $docu" \
        --button=gtk-cancel:1 \
        --button=gtk-ok:0 \
        )

    errmsg=""
    echo "# values=$values"
    test -z "$values" && echo "# launcher stoped (form canceled)" && exit 1

    # evaluate if form is completed
    projectdir=$(echo $values | cut -d '|' -f2 | grep -v null)
    test -z "$projectdir" && projectdir=$(echo $values | cut -d '|' -f3 | grep -v null)
    if [ "$projectdir" ]
    then
        projectdir=$basedir/$projectdir
        day=""
        site=""
        formOK=1
        source $projectdir/$rc
    else
        # basedir
        x=$(echo $values | cut -d '|' -f6)
        test "$x" && test -d "$x" && basedir="$x" && x=""
        test "$x" && adderr "Base directory $x does not exist"
        # day
        day=$(echo $values | cut -d '|' -f7 | \
            awk -F '-' '{if(NF==3){printf("%2d%s%s", $1%100, $2, $3)}}')
        # tmpdir
        x=$(echo $values | cut -d '|' -f8)
        test "$x" && test -d "$x" && tmpdir="$x" && x=""
        test "$x" && adderr "Temp. directory $x does not exist"
        # site
        site=$(echo $values | cut -d '|' -f9)
        # keep selected items of lists
        siteslist=$(select_item "$siteslist" "$site")
        
        test ! "$errmsg" && test "$basedir" && save_ini $ini
        if [ ! "$errmsg" ] && [ "$basedir" ] && [ "$day" ]
        then
            projectdir=$basedir/$day
            if [ -e $projectdir/$rc ]
            then
                adderr "cannot overwrite existing projectdir $projectdir"
            else
                test -d $projectdir || mkdir $projectdir
                if [ $? -ne 0 ]
                then
                    adderr "cannot create projectdir $projectdir"
                else
                    test "$site" != "$newsite" &&
                        lastsite="$site" &&
                        site=${site%% *} &&
                        echo "# site=$site"
                    formOK=1
                fi
            fi
        fi
    fi
done

# save global settings to ini file
test "$has_arg_pdir" || save_ini $ini


# copy metadata files to basedir
for f in refcat.dat sites.dat camera.dat
do
    for d in /usr/local/share/airtools $datadir
    do
        test ! -e $basedir/$f && test -e $d/$f && cp -p $d/$f $basedir
    done
done

# copy metadata files to projectdir
for f in refcat.dat sites.dat camera.dat
do
    test -e $projectdir/$f &&
        diff -q $basedir/$f $projectdir/$f >/dev/null && continue
    # TODO: try merging of files if header line is identical (same fields)
    test -e $projectdir/$f && test -e $projectdir/$rc && continue
    if [ -e $projectdir/$f ]
    then
        old=${f%%.*}".old."${f#*.}
        echo "WARNING: moving old $projectdir/$f to $old"
        mv $projectdir/$f $projectdir/$old
    fi
    cp -p $basedir/$f $projectdir/$f
done

# check if current site exists
test -z "$site" && test "$AI_SITE" && site=$AI_SITE &&
    echo "# site=$site (using AI_SITE)"
test "$site" && ! grep -q " $site " $projectdir/sites.dat && site="" &&
    echo "# WARNING: site $site not in sites.dat"
test -z "$site" && site="$newsite"



#-------------------------
#   new site definitions
#-------------------------
# form 2
if [ "$site" == "$newsite" ]
then
    title="AIRTOOLS - New Site"
    echo "# form: $title"
    formOK=""
    errmsg=""
    sid=""
    site=""
    tdiff=""
    long=""
    lat=""
    alt=""
    while [ ! "$formOK" ]
    do
        txt="Please add new observatory site definitions:\n"
        values=$(yad $yadopts --title="$title" \
            --text="$txt<span foreground='red'>$errmsg</span>" \
            --form \
            --date-format="%Y-%m-%d" --separator="|" --item-separator=";" \
            --field="Site ID (e.g. XYZ):"   "$sid" \
            --field="Location:"             "$site" \
            --field="TZ-UT / hr :"          "$tdiff" \
            --field="Longitude / ° :"       "$long" \
            --field="Latitude / ° :"        "$lat" \
            --field="Altitude / m :"        "$alt" \
            --field="\n:LBL"                ""
        )
        
        errmsg=""
        # check field values
        echo "# values=$values"
        test -z "$values" && echo "# launcher stoped (form canceled)" && exit 1
        
        # sid must be unique
        x=$(echo $values | cut -d '|' -f1)
        xexists=$(grep -v "^#" $sitesdat | awk -v x="$x" -v i=1 '{if(x==$i) {print 1}}')
        test ! "$xexists" && sid=$x || adderr "ID $x exists"
        # site must be unique
        x=$(echo $values | cut -d '|' -f2)
        xexists=$(grep -v "^#" $sitesdat | awk -v x="$x" -v i=2 '{if(x==$i) {print 1}}')
        test ! "$xexists" && site=$x || adderr "Location $x exists"
        # tdiff must be number
        x=$(echo $values | cut -d '|' -f3 | tr ',' '.')
        is_number "$x" && tdiff=$x && x=""
        test "$x" && adderr "TZ-UT $x is not a number"
        # long must be number
        x=$(echo $values | cut -d '|' -f4 | tr ',' '.')
        is_number "$x" && long=$x && x=""
        test "$x" && adderr "Long $x is not a number"
        # lat must be number
        x=$(echo $values | cut -d '|' -f5 | tr ',' '.')
        is_number "$x" && lat=$x && x=""
        test "$x" && adderr "Lat $x is not a number"
        # alt must be number
        x=$(echo $values | cut -d '|' -f6 | tr ',' '.')
        is_number "$x" && alt=$x && x=""
        test "$x" && adderr "Alt $x is not a number"
        
        echo "# sid=$sid site=$site tdiff=$tdiff long=$long lat=$lat alt=$alt"
        echo "# errmsg=$errmsg"
        x=$(echo $sid $site $tdiff $long $lat $alt | wc -w)
        test "$x" && test $x -eq 6 &&
            formOK=1
    done
    
    # saving new site
    line=$(echo $sid $site $tdiff $long $lat $alt | awk '{
        x=$3; if(x>0) {x="+"x}
        printf("%-7s %-11s 1   %-5s %7.2f   %6.2f  %4d",
            $1, $2, x, $4, $5, $6)}')
    echo "$line" >> $basedir/sites.dat
    echo "$line" >> $projectdir/sites.dat
    
    lastsite="$site (ID=$sid)"
    save_ini $ini
fi


# save settings to local resources file
if [ ! -e $projectdir/$rc ]
then
    echo "# saving new settings to $projectdir/$rc"
    echo "export day=$day
export AI_SITE=$site
export AI_TMPDIR=$tmpdir" > $projectdir/$rc
fi

test "$has_arg_pdir" || echo "# projectdir=$projectdir"

# prepare environment for loading airfun.sh
cd $projectdir
export AI_TMPDIR=/tmp
export AI_RAWDIR=./
. $rc
test -d $AI_TMPDIR || mkdir -p $AI_TMPDIR


#--------------------------
#   image set definitions
#--------------------------
# get list of existing image sets from set.dat
setlist=""
sdat=$projectdir/set.dat
test -e $sdat && setlist=$(grep -v "^#" $sdat | awk '{
    if ($1!~/^[0-9][0-9]:[0-9][0-9]/) next
    if ($4!="o") next
    if ($5!~/^[0-9]+$/) next
    if ($6!~/^[0-9]+$/) next
    if ($7!~/^[0-9]+$/) next
    if ($8!~/^[0-9]+$/) next
    if (NF<11) next
    printf(";%s (%s)", $2, $3)
    }')

# get list of available instruments
newcamera="[add new instrument]"
cameralist=""
cameralist=$(grep -v "^#" $projectdir/camera.dat | grep "[[:alnum:]]" | awk '{
    printf(";%s (d=%s, f/%s, %s)", $1, $3, $4, $5)}')
cameralist="$newcamera$cameralist"
# select lastcamera
test "$lastcamera" && cameralist=$(select_item "$cameralist" "$lastcamera")

# form 3
# open existing image set
# add new image set (new target object)
#   set name
#   target
#   ...
#   instrument
#   raw image files
title="AIRTOOLS - Image Set"
echo "# form: $title"
formOK=""
errmsg=""
setname=""
target=""
start=""
texp=""
nimg=""
nref=""
binning=""  # note: values is added to header after image conversion
telid=""
comm=""
rawfiles=""
while [ ! "$formOK" ]
do
    txt="Choose an existing image set or \
define a new image set by filling in the lower entries of this form\n"

    values=$(test -d $AI_RAWDIR && cd $AI_RAWDIR
        yad $yadopts --title="$title" \
        --text="$txt<span foreground='red'>$errmsg</span>" \
        --form \
        --date-format="%Y-%m-%d" --separator="|" --item-separator=";" \
        --field="<b>Existing image sets</b>:LBL"        "" \
        --field="Existing set (and target)::CB"         "$setlist" \
        --field="\n:LBL" "" \
        --field="<b>Define a new image set</b>:LBL"     "" \
        --field="Set name (e.g. co01):"                 "$setname" \
        --field="Target comet (e.g. 2P or 2015V2):"     "$target" \
        --field="Local start time / hh:mm :"            "$start" \
        --field="Average exposure time per image / sec :" "$texp" \
        --field="Number of exposures:"                  "$nimg" \
        --field="Reference image number for stacking:"  "$nref" \
        --field="Pixel binning:"                        "$binning" \
        --field="Instrument (telescope/camera)::CB"     "$cameralist" \
        --field="----   Optional fields:LBL"            "" \
        --field="Comments (e.g. filter):"               "$comm" \
        --field="Image files of individual exposures::MFL" "$rawfiles" \
        --field="\n:LBL" ""
        )
        # --file-filter="FITS images|*.fits" \

    errmsg=""
    # check field values
    echo "# values=$values"
    test -z "$values" && echo "# launcher stoped (form canceled)" && exit 1
    
    setname=$(echo $values | cut -d '|' -f2 | grep -v null | cut -d ' ' -f1)
    if [ "$setname" ]
    then
        echo "# using setname=$setname"
        formOK=1
    else
        # setname must be unique
        x=$(echo $values | cut -d '|' -f5 | tr ' ' '_')
        test "$x" && test -e "$sdat" && test "$(grep -v "^#" $sdat | awk -v s="$x" '{
        if ($1!~/^[0-9][0-9]:[0-9][0-9]/) next
        if ($2!=s) next
        if ($5!~/^[0-9]+$/) next
        if ($6!~/^[0-9]+$/) next
        if ($7!~/^[0-9]+$/) next
        if ($8!~/^[0-9]+$/ && $8!="-") next
        if (NF<10) next
        x=1
        }END{print x}')" && adderr "setname $x exists" && x=""
        test "$x" && setname=$x
        # target must match a valid comet designation
        x=$(echo $values | cut -d '|' -f6)
        test "$x" && (! is_number ${x:0:1} || test "$(echo $x | tr -d '[0-9][A-Z]')") &&
            adderr "target $x is not a valid comet name" && x=""
        test "$x" && target=$x
        # start, TODO format to hh:mm
        x=$(echo $values | cut -d '|' -f7 | tr -d ' ')
        is_time "$x" && start=$x && x=""
        test "$x" && adderr "Start time $x is not valid"
        # texp
        x=$(echo $values | cut -d '|' -f8 | tr -d ' ' | tr ',' '.')
        is_number "$x" && texp=$x && x=""
        test "$x" && adderr "Exposure time $x is not a number"
        # nimg
        x=$(echo $values | cut -d '|' -f9 | tr -d ' ')
        is_number "$x" && nimg=$x && x=""
        test "$x" && adderr "Number of images $x is not a number"
        # nref
        x=$(echo $values | cut -d '|' -f10 | tr -d ' ')
        is_number "$x" && nref=$x && x=""
        test "$x" && adderr "Ref. image number $x is not a number"
        # binning
        x=$(echo $values | cut -d '|' -f11 | tr -d ' ')
        is_number "$x" && binning=$x && x=""
        test "$x" && adderr "Binning $x is not a number"
        # telid
        x=$(echo $values | cut -d '|' -f12)
        test "$x" == "$newcamera" && telid="$newcamera"
        test "$x" != "$newcamera" && lastcamera="$x" && telid=${x%% *}
        
        # comm
        x=$(echo $values | cut -d '|' -f14)
        test "$x" && comm="$x"
        test "$binning" && test "$binning" != 1 && comm=$(echo $comm "bin"$binning)
        # rawfiles
        x=$(echo $values | cut -d '|' -f15)
        test "$x" && rawfiles="$x"
        
        # keep selected items of lists
        x=$(echo $values | cut -d '|' -f12)
        cameralist=$(select_item "$cameralist" "$x")
        
        echo "# setname=$setname target=$target start=$start texp=$texp nimg=$nimg nref=$nref bin=$binning telid=$telid"
        echo "# errmsg=$errmsg"
        x=$(echo $setname $target $start $texp $nimg $nref $binning | wc -w)
        if [ $x -eq 7 ]
        then
            formOK=1
            if [ "$rawfiles" ]
            then
                echo "# rawfiles=$rawfiles"
                x=$(echo $rawfiles | cut -d ';' -f1)
                rawdir=$(realpath $(dirname $x))
                if [ -e $projectdir/$rc ]
                then
                    # append/replace AI_RAWDIR
                    sed -i '/^export AI_RAWDIR/d' $projectdir/$rc
                    echo "export AI_RAWDIR=$rawdir" >> $projectdir/$rc
                fi
                show_progresswindow "$title" "Analyzing rawfiles ..."
                map_rawfiles ${rawfiles//;/ } >> rawfiles.dat
                stop_progresswindow
            fi
        fi
        
        # save ini file (in case new camera has been selected)
        test "$has_arg_pdir" || save_ini $ini
    fi
done

# check if camera of the current set exists
echo "# telid=$telid"
if [ -z "$telid" ]
then
    x=$(AIsetinfo -b $setname | head -1 | awk '{printf("%s", $11)}')
    test "$x" && ! grep -q "^$x " $projectdir/camera.dat && telid="$newcamera" &&
        echo "# WARNING: telid $x not in camera.dat"
fi


#---------------------------
#   new camera definitions
#---------------------------
# form 4
if [ "$telid" == "$newcamera" ]
then
    title="AIRTOOLS - New Instrument"
    echo "# form: $title"
    formOK=""
    errmsg=""
    tel=""
    flen=""
    aperture=""
    fratio=""
    camera=""
    rot=""
    rawbits=""
    satur=""
    gain=""
    pixscale=""
    magzero=""
    ttypelist="Reflector;Refractor;Photo Lens"  # L;R;A
    ctypelist="CCD;DSLR"
    while [ ! "$formOK" ]
    do
        txt="Please add new telescope/camera definitions (note: only two of the \
three values for focal length, aperture and f-ratio must be specified):\n"
        values=$(yad $yadopts --title="$title" \
            --text="$txt<span foreground='red'>$errmsg</span>" \
            --form \
            --date-format="%Y-%m-%d" --separator="|" --item-separator=";" \
            --field="Instrument ID (e.g. XYZ):" "$tel" \
            --field="Focal length / mm :"       "$flen" \
            --field="Aperture / mm :"           "$aperture" \
            --field="F-Ratio (f/d):"            "$fratio" \
            --field="Camera Model:"             "$camera" \
            --field="Camera Rotation / ° :"     "$rot" \
            --field="RawBits:"                  "$rawbits" \
            --field="Saturation:"               "$satur" \
            --field="Gain / e-/ADU :"           "$gain" \
            --field="Pixel scale / arcsec :"    "$pixscale" \
            --field="Mag zero point:"           "$magzero" \
            --field="Telescope type::CB"        "$ttypelist" \
            --field="Camera type::CB"           "$ctypelist" \
            --field="\n:LBL"                    ""
        )
        
        errmsg=""
        echo "# values=$values"
        test -z "$values" && echo "# launcher stoped (form canceled)" && exit 1

        # check field values
        # tel must be unique
        x=$(echo $values | cut -d '|' -f1 | tr ' ' '_')
        xexists=$(grep -v "^#" $projectdir/camera.dat | awk -v x="$x" -v i=1 '{if(x==$i) {print 1}}')
        test ! "$xexists" && tel=$x || adderr "ID $x exists"
        # flen must be number
        x=$(echo $values | cut -d '|' -f2)
        is_number "$x" && flen=$x && x=""
        test "$x" && adderr "Focal length $x is not a number"
        # aperture must be number
        x=$(echo $values | cut -d '|' -f3 | tr ',' '.')
        is_number "$x" && aperture=$x && x=""
        test "$x" && adderr "Aperture $x is not a number"
        # fratio must be number
        x=$(echo $values | cut -d '|' -f4 | tr ',' '.')
        is_number "$x" && fratio=$x && x=""
        test "$x" && adderr "F-ratio $x is not a number"
        
        # compute missing flen or aperture or fratio
        test -z "$flen" && test "$fratio" && test "$aperture" &&
            flen=$(echo $fratio $aperture | awk '{printf("%.0f", $1*$2)}')
        test -z "$aperture" && test "$flen" && test "$fratio" &&
            aperture=$(echo $flen $fratio | awk '{printf("%.0f", $1/$2)}')
        test -z "$fratio" && test "$flen" && test "$aperture" &&
            fratio=$(echo $flen $aperture | awk '{printf("%.1f", $1/$2)}')
        
        # camera
        camera=$(echo $values | cut -d '|' -f5 | tr ' ' '_')
        # rot must be number
        x=$(echo $values | cut -d '|' -f6 | tr ',' '.')
        is_number "$x" && rot=$x && x=""
        test "$x" && adderr "Rotation $x is not a number"
        # rawbits must be number
        x=$(echo $values | cut -d '|' -f7)
        is_number "$x" && rawbits=$x && x=""
        test "$x" && adderr "Rawbits $x is not a number"
        # satur must be number
        x=$(echo $values | cut -d '|' -f8)
        is_number "$x" && satur=$x && x=""
        test "$x" && adderr "Saturation $x is not a number"
        # gain must be number
        x=$(echo $values | cut -d '|' -f9 | tr ',' '.')
        is_number "$x" && gain=$x && x=""
        test "$x" && adderr "Gain $x is not a number"
        # pixscale must be number
        x=$(echo $values | cut -d '|' -f10 | tr ',' '.')
        is_number "$x" && pixscale=$x && x=""
        test "$x" && adderr "Pixel scale $x is not a number"
        # magzero must be number
        x=$(echo $values | cut -d '|' -f11 | tr ',' '.')
        is_number "$x" && magzero=$x && x=""
        test "$x" && adderr "Mag zero point $x is not a number"
        
        # keep selected items of ttypelist, ctypelist
        x=$(echo $values | cut -d '|' -f12)
        ttypelist=$(select_item "$ttypelist" "$x")
        x=$(echo $values | cut -d '|' -f13)
        ctypelist=$(select_item "$ctypelist" "$x")

        echo "# tel=$tel flen=$flen aperture=$aperture fratio=$fratio camera=$camera pixscale=$pixscale"
        echo "# errmsg=$errmsg"
        x=$(echo $tel $flen $aperture $fratio $camera $rot $rawbits $satur $gain $pixscale $magzero | wc -w)
        test "$x" && test $x -eq 11 &&
            formOK=1
    done
    telid=$tel

    # ttype, ctype
    case "$(echo $values | cut -d '|' -f12)" in
        Reflector)  ttype="L";;
        Refractor)  ttype="R";;
        Photo\ Lens) ttype="A";;
        *)          ttype="L";;
    esac
    ctype=$(echo $values | cut -d '|' -f13)
    
    # saving new camera
    line=$(echo $tel $flen $aperture $fratio $camera $rot $rawbits $satur \
        $gain $pixscale $magzero $ttype $ctype | awk '{
        printf("%-6s %4d   %4d   %4.1f   %-11s %3d  %2d %6d  ",
            $1, $2, $3, $4, $5, $6, $7, $8)
        printf("%5.2f  %6.2f    %4.1f    %s   %s",
            $9, $10, $11, $12, $13)
        }')
    echo "$line" >> $basedir/camera.dat
    echo "$line" >> $projectdir/camera.dat
    
    # save ini
    lastcamera=$(echo $line | awk '{
        printf("%s (d=%s, f/%s, %s)", $1, $3, $4, $5)}')
    test "$has_arg_pdir" || save_ini $ini
fi


# append new set to $sdat (target and telid are defined)
if [ "$target" ] && [ "$telid" ]
then
    if [ -e $sdat ]
    then
        nmax=$(grep -v "^#" $sdat | awk '{
            if ($1!~/^[0-9][0-9]:[0-9][0-9]/) next
            if ($5!~/^[0-9]+$/) next
            if ($6!~/^[0-9]+$/) next
            if ($7!~/^[0-9]+$/) next
            if (NF<10) next
            printf("%d\n%d\n", 1*$6, 1*$7)
            }' | sort -n -r | head -1)
        n1=$((nmax+1))
        n2=$((nmax+nimg))
        nref=$((nmax+nref))
    else
        echo "
# $day

# LT
# h:m set  target type texp n1 n2   nref dark flat tel" > $sdat
        n1=1
        n2=$nimg
    fi
    echo $start $setname $target $texp $n1 $n2 $nref $telid | awk -v c="$comm" '{
        printf("%-5s %-4s %-8s o %3.0f %04d %04d %04d ", $1, $2, $3, $4, $5, $6, $7)
        if (c=="") {
            printf("dark flat %s\n", $8)
        } else {
            printf("dark flat %-4s # %s\n", $8, c)
        }
    }' >> $sdat
fi

# if target is not set but telid is set then modify telid in $sdat
if [ "$target" ] && [ "$telid" ]
then
    x=$(AIsetinfo -b $setname | head -1 | awk '{printf("%s", $11)}')
    echo "# TODO: replace x by $telid"
fi



#---------------------------
#   launch airtools
#---------------------------
# locate image stacks and launch airtools or choose another action
# form 5
title="AIRTOOLS - Launch"
echo "# form: $title"
formOK=""
errmsg=""
actionlist="Lauch AIRTOOLS;Open File Browser;Open Terminal"
starstack=""
cometstack=""
sttype="SFL"   # starstack field type
cotype="SFL"   # cometstack field type
# check for stacked images in PNM format
ext=""
test -z "$starstack" && test -e $projectdir/$setname.ppm && ext=ppm &&
    starstack=$setname.$ext && sttype="RO"
test -z "$starstack" && test -e $projectdir/$setname.pgm && ext=pgm &&
    starstack=$setname.$ext && sttype="RO"
if [ "$starstack" ] && [ -e $projectdir/$setname.head ]
then
    x=$(get_header $projectdir/$setname.head AI_COMST)
    test "$x" && cometstack=$x && cotype="RO"
fi
test -z "$cometstack" && test -e $projectdir/${setname}_m.$ext &&
    cometstack=${setname}_m.$ext && cotype="RO"
echo "# starstack=$starstack  cometstack=$cometstack"

# read binning from comment in $sdat if there was no previous conversion via AIstart
if [ -z "$binning" ] && [ -e $sdat ] && [ ! -e $projectdir/$setname.head ]
then
    comm=$(grep -v "^#" $sdat | awk -v s=$setname '{if($2==s){print $0}}' | \
        head -1 | sed -e 's|[^#]*#||')
    x=$(echo $comm | tr ' ' '\n' | grep -w "bin[2-9]" | head -1)
    binning=${x:3:1}
    echo "# binning=$binning"
fi

while [ ! "$formOK" ]
do
    txt="Launch AIRTOOLS or choose any of the other actions\n"

    values=$(test $sttype == "SFL" && test $cotype == "SFL" && test -d $AI_RAWDIR && \
        cd $AI_RAWDIR
        yad $yadopts --title="$title" \
        --text="$txt<span foreground='red'>$errmsg</span>" \
        --date-format="%Y-%m-%d" --separator="|" --item-separator=";" \
        --form \
        --field="Stack centered on stars:$sttype"   "$starstack" \
        --field="Stack centered on comet:$cotype"   "$cometstack" \
        --field="<b>Choose an Action</b>:CB"        "$actionlist" \
        --field="\n:LBL" ""
        )
    buttonID=$?

    errmsg=""
    echo "# values=$values"
    test -z "$values" && echo "# launcher stoped (form canceled)" && exit 1
    
    # get field values
    # starstack
    x=$(echo $values | cut -d '|' -f1)
    test "$x" && test "$sttype" == "RO" && starstack=$x && x=""
    test "$x" && test -f $x && starstack=$x && x=""
    test "$x" && adderr "Star stack image $x not found"
    # cometstack
    x=$(echo $values | cut -d '|' -f2)
    test "$x" && test "$cotype" == "RO" && cometstack=$x && x=""
    test "$x" && test -f $x && cometstack=$x && x=""
    test "$x" && adderr "Comet stack image $x not found"
    (test -z "$starstack" || test -z "$cometstack") &&
        test -z "$errmsg" &&
        adderr "Missing entry for stacked image(s)"
                    
    # take an action
    action=$(echo $values | cut -d '|' -f3 | awk '{print tolower($NF)}')
    case "$action" in
        browser)    echo "# open file browser"
                    xdg-open $projectdir
                    ;;
        terminal)   echo "# open terminal"
                    (cd $projectdir; x-terminal-emulator);;
        airtools)   if [ ! "$errmsg" ]
                    then
                        x=""
                        test "$binning" && x="-k BINNING=$binning"
                        echo "# AIstart -c -n $x $setname $starstack $cometstack"
                        show_progresswindow "$title" "Loading images ..."
                        str=$(AIstart -c -n $x $setname $starstack $cometstack)
                        if [ $? -eq 0 ]
                        then
                            formOK=1
                            echo "# open airtools user interface"
                            test -e $setname.ppm &&
                                starstack=$setname.ppm && cometstack=${setname}_m.ppm
                            test -e $setname.pgm &&
                                starstack=$setname.pgm && cometstack=${setname}_m.pgm
                            AIexamine $starstack $cometstack &
                            while [ $(xpaaccess -n -t "2,2" AIRTOOLS) -eq 0 ]
                            do
                                sleep 0.2
                            done
                            stop_progresswindow
                        else
                            stop_progresswindow
                            # create error message
                            #echo "# result=$str"
                            if [ -z "$str" ] || [ "$(echo $str | tr ' ' '\n' | grep -vE "^$|^JD$|^RA$|^DEC$")" ]
                            then
                                # unusual error
                                errfile=$(mktemp /tmp/tmp_err_XXXXXX.txt)
                                x=$(grep -n "^####" $log | tail -1 | cut -d ":" -f1)
                                x=$((x-1))
                                cat $log | sed -e "1,${x}d" > $errfile
                                yad --text-info --tail --width 600 --height 300 \
                                    --title "AIRTOOLS - ERROR" < $errfile
                                errmsg="ERROR: AIstart failed."
                                rm -f $errfile
                            else
                                errmsg=$(echo "ERROR: missing FITS header keywords" $str)
                            fi
                        fi
                    fi
                    ;;
        *)          adderr "Unknown action $action";;
    esac
    test "$errmsg" && echo "$errmsg" && echo ""
done

echo "# launcher finished"


#--------------------
#   clean-up
#--------------------
exit 0
