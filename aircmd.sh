#!/bin/bash

#
# ds9 analysis command wrapper around function ds9cmd from airfun.sh
#

prog=$(type -p airfun.sh)
test $? -ne 0 &&
    echo "ERROR: airfun.sh not found." >&2 && exit 1
. $prog > /dev/null

# execute commands
test -z "$AI_LOG" && AI_LOG=ds9cmd.log
ds9cmd "$@" 2>&1 | tee -a $AI_LOG
