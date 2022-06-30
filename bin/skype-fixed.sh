#!/bin/bash

# From:
# http://askubuntu.com/questions/453515/skype-14-04-no-sound-output-in-conversations

# Skype is not working properly in Xubuntu 14.04 LTS (no sound at all). After
# running Skype with this configuration the issue dissappears...

env PULSE_LATENCY_MSEC=30 skype &
skype-call-recorder
