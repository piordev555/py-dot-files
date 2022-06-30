#!/bin/sh

# Script to replace django.contrib.localflavor (it's not anymore
# inside Django core) and django_localflavor_us because it's
# DEPRECATED to django-localflavor 1.0
# https://github.com/django/django-localflavor/

if [ -n "$1" ]; then
    FILES_TO_CONVERT="$@"
else
    FILES_TO_CONVERT="$(find . -name '*.py')"
fi

for f in $FILES_TO_CONVERT; do
    perl -i -0 \
    -pe "s/from django.contrib.localflavor.us.models import PhoneNumberField\n/from localflavor.us.models import PhoneNumberField\n/g;" \
    -pe "s/django.contrib.localflavor.us.models/localflavor.us.models/g;" \
    -pe "s/django_localflavor_us.models/localflavor.us.models/g;" \
    -pe "s/from django_localflavor_us/from localflavor.us/g;" \
    $f
done
