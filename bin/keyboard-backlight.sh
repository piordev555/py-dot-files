#!/bin/sh

# Cron entry as 'root'
#
# $ sudo crontab -e
# * * * * * /home/humitos/bin/keyboard-backlight.sh

# TODO: another possible solution https://github.com/wavexx/acpilight/

TURN_ON_MS=5000  # 5 seconds
AUTOSUSPEND_MS=30000  # 30 seconds
X_IDLE_TIME=`xprintidle`

echo $X_IDLE_TIME

# Turn on the keybord backlight if we press a key
if [ "$X_IDLE_TIME" -lt "$TURN_ON_MS" ];
then
    echo 1 > /sys/devices/platform/thinkpad_acpi/leds/tpacpi\:\:kbd_backlight/brightness
fi


# Turn off the keyboard backlight after some time without pressing a key
if [ "$X_IDLE_TIME" -gt "$AUTOSUSPEND_MS" ];
then
    echo 0 > /sys/devices/platform/thinkpad_acpi/leds/tpacpi\:\:kbd_backlight/brightness
fi
