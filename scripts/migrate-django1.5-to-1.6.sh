#!/bin/sh

# Script to replace some things that changed from Django 1.5 to 1.6

# django.contrib.localflavor is not inside the core anymore

if [ -n "$1" ]; then
    FILES_TO_CONVERT="$@"
else
    FILES_TO_CONVERT="$(find . -name '*.html') $(find . -name '*.py') $(find . -name '*.txt')"
fi

for f in $FILES_TO_CONVERT; do
    perl -i -0 \
    -pe "s/from django\.contrib\.localflavor\.([a-zA-Z_\.0-9]+) import ([a-zA-Z_0-9\. ]+)/from localflavor.\1 import \2/g;" \
    -pe "s/from django\.conf\.urls\.defaults import ([a-zA-Z_0-9\. \*]+)/from django.conf.urls import \1/g;" \
    -pe "s/from django\.utils\.hashcompat import sha_constructor/import hashlib/g;" \
    -pe "s/sha_constructor/hashlib.sha256/g;" \
    $f
done

