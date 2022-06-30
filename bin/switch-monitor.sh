#!/bin/bash
# $ xrandr
# Screen 0: minimum 8 x 8, current 1920 x 1080, maximum 32767 x 32767
# eDP1 connected 1920x1080+0+0 (normal left inverted right x axis y axis) 310mm x 170mm
#    1920x1080     60.05*+
#    1400x1050     59.98
#    1600x900      60.00
#    1280x1024     60.02
#    1280x960      60.00
#    1368x768      60.00
#    1280x720      60.00
#    1024x768      60.00
#    1024x576      60.00
#    960x540       60.00
#    800x600       60.32    56.25
#    864x486       60.00
#    640x480       59.94
#    720x405       60.00
#    640x360       60.00
# DP1 disconnected (normal left inverted right x axis y axis)
# DP2 disconnected (normal left inverted right x axis y axis)
# HDMI1 connected (normal left inverted right x axis y axis)
#    1920x1080     60.00 +  50.00    59.94
#    1920x1080i    60.00    50.00    59.94
#    1680x1050     59.88
#    1280x1024     60.02
#    1280x960      60.00
#    1152x864      59.97
#    1280x720      60.00    50.00    59.94
#    1024x768      60.00
#    800x600       60.32
#    720x576       50.00
#    720x480       60.00    59.94
#    640x480       60.00    59.94
# VIRTUAL1 disconnected (normal left inverted right x axis y axis)

CURRENT_MONITOR=`xrandr | grep 1920x1080+0+0 | awk '{ print $1 }' | head -n 1`

HDMI="HDMI1"
HDMI_HUB="DP2"
NOTEBOOK="eDP1"

if [ $CURRENT_MONITOR = $HDMI ] || [ $CURRENT_MONITOR = $HDMI_HUB ]
then
    # switch to NOTEBOOK monitor
    xrandr --output $HDMI --off --output $HDMI_HUB --off --output $NOTEBOOK --mode 1920x1080 --pos 0x0 --rotate normal
    exit 0
fi

if [ $CURRENT_MONITOR = $NOTEBOOK ]
then
    # switch to EXTERNAL (LG) monitor
    xrandr --output $NOTEBOOK --off --output $HDMI --mode 1920x1080 --pos 0x0 --rotate normal
    # switch to EXTERNAL monitor over USC-C Hub
    xrandr --output $NOTEBOOK --off --output $HDMI_HUB --mode 1920x1080 --pos 0x0 --rotate normal
    exit 0
fi


# always fallback to the $NOTEBOOK monitor in case that the last
# monitor was $HDMI but now the cable is not connected so, not
# detected
echo "Fallback..."
xrandr --output $HDMI --off --output $NOTEBOOK --mode 1920x1080 --pos 0x0 --rotate normal
