#!/usr/bin/env bash


FIREFOX=`wmctrl -l -x | grep Navigator | cut -d " " -f 1`
EMACS=`wmctrl -l -x | grep emacs@julia | cut -d " " -f 1`
TERMINAL=`wmctrl -l -x | grep zsh | cut -d " " -f 1`


# Duplicated because emacs does not take it the first one
wmctrl -i -r $EMACS -e 0,0,0,1920,1000
wmctrl -i -r $EMACS -e 0,0,0,1920,1000

wmctrl -i -r $FIREFOX -e 1,0,0,1920,1000
wmctrl -i -r $TERMINAL -e 1,0,0,1920,1000
