#!/bin/bash

if [ "$1" == "final" ]; then
    dpkg-query -W -f='${Package},${Architecture},${Version}\n' > $SRCDIR/build/packages.csv
fi