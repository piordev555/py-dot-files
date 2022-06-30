#!/bin/sh

# Script to replace some things that changed from Django 1.4 to 1.5

# {% url %} template tag
# Generic Views are now Class-Based


if [ -n "$1" ]; then
    FILES_TO_CONVERT="$@"
else
    FILES_TO_CONVERT="$(find . -name '*.html') $(find . -name '*.py') $(find . -name '*.txt')"
fi

for f in $FILES_TO_CONVERT; do
    perl -i -0 \
    -pe "s/{% url ([a-zA-Z0-9\._]*) %}/{% url \"\1\" %}/g;" \
    -pe "s/{% url ([a-zA-Z0-9\._]*) ([a-zA-Z0-9\._=]*) %}/{% url \"\1\" \2 %}/g;" \
    -pe "s/{% url ([a-zA-Z0-9\._]*) ([a-zA-Z0-9\._=]*) as ([a-zA-Z0-9_]*) %}/{% url \"\1\" \2 as \3 %}/g;" \
    -pe "s/from django.views.generic.simple import direct_to_template/from django.views.generic import TemplateView/g;" \
    -pe "s/url\((.*), direct_to_template, {'template': (.*)}, ([a-zA-Z\._=']*)/url\(\1, TemplateView.as_view\(template_name=\2\), \3/g;" \
    -pe "s/from django.views.generic.list_detail import object_list/from django.views.generic import ListView/g;" \
    $f
done
