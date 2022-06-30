# -*- coding: utf-8 -*-

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# Author: Manuel Kaufmann <humitos@gmail.com>
# Date: 29 October 2016
# Release: 0.5

# DESCRIPTION:
#
# This program allows you to do not listen to Spotify Ads without having a paid
# account. It's not too much intelligent right now, so you have to add the
# Artists you usually listen to or the name of the Spotify Ads you want to mute.
#
# How it works? It just mute the sound system when it detects an Ads is being
# played. How? By reading the window's title and check against all the known
# names and Ads you have defined and using some dumb pre-defined rules that fail
# in some cases.

from __future__ import division, print_function, unicode_literals

import commands
import datetime
import os
import subprocess
import sys
import time

HOSTNAME = commands.getoutput('hostname')
TERMINAL_ENCODING = commands.getoutput('locale charmap')
WMCTRL_WINDOW_LIST = "wmctrl -l -x | grep 'spotify.Spotify' | grep -v 'grep'"
# MUTE_COMMAND = 'amixer -q -D pulse sset Master mute; pacmd set-sink-input-mute {index} true'
# UNMUTE_COMMAND = 'amixer -q -D pulse sset Master unmute; pacmd set-sink-input-mute {index} false'
MUTE_COMMAND = 'pacmd set-sink-input-mute {index} true'
UNMUTE_COMMAND = 'pacmd set-sink-input-mute {index} false'
SPOTIFY_OPEN_COMMAND = 'ps -ef | grep Spotify | grep -v grep | wc -l'

MUTED = False
SPOTIFY_OPENED = False
PAREC_PROCESS = None
LAME_PROCESS = None
SONGS_PLAYED = []

# Time in seconds
SLEEP_BEFORE_UNMUTE = 1.5
SLEEP_BETWEEN_EACH_CHECK = 0.1
SLEEP_WHEN_SPOTIFY_CLOSED = 5

DEFAULT_OUTPUT_DIR = 'spotify'

# Define the names of the Artists, Songs, etc you usually listen to here
KNOWN_TITLES = (
    # Titles that I found with problems matching dumb rules
    ['Emir Kusturica'],
    ['Jarabe De Palo'],
    ['Bob Marley'],
    ['Queen'],
    ['Soda Stereo'],
    ['Tonolec'],
    ['Kevin Johansen'],
    ['Michael Jackson'],
    ['Morcheeba'],
    ['Pink Floyd'],
    ['Queen'],
    ['Lenine'],
    ['Gustavo Santaolalla'],
    ['Genesis'],
    ['JAF'],
    ['Los Rodriguez'],
    ['Talking Heads'],
    ['Fito Páez'],
    ['Perotá Chingò'],
    ['John Lennon'],
    ['David Bowie'],

    # Titles I want to be sure that are valid
    map(
        lambda x: '- {}'.format(x), [
            'Remastered', 'Extended Version', 'En Vivo', 'MTV Unplugged',
            'Acoustic', 'Versión Acústica', 'Live', 'Directo', 'directo',
            'unplugged', 'en directo', 'Unplugged Version', 'Live/Unplugged',
            'Instrumental', 'Remasterizado', 'BBC', 'Single Version',
            'En Directo',
        ],
    ),
    # ...
)  # yapf: disable

# Define the names of the Ads you usually listen to and want to avoid here
ADS_TITLES = (
    # ...
    ['REYKON'],
    ['Directv'],
    ['TOP HITS'],
    ['Discovery Mujer'],
    ['The Voice'],
    ['5 Décadas De Rock Argentino'],
    ['Sillón de amigos'],
    ['Discover te lleva a Soda Stereo'],
    ['Legarda'],
    ['Queen of the South'],
    ['Super Hits'],
    ['Rome Santos'],
)  # yapf: disable


def get_pacmd_index():
    """
    Get the current index for the Spotify audio stream using `pacmd`.

    At the moment it's quite dumb and could be improved to really get just the
    Spotify index.
    """
    cmd = "LC_ALL=C pacmd list-sink-inputs | grep -C 20 Spotify | grep index | awk '{ print $2 }' | head -n 1"
    # cmd = "LC_ALL=C pactl list | grep -E '(^Sink Input)|(media.name = \"Spotify\"$)' | cut -d \# -f2 | grep -v Spotify"
    # cmd = "pacmd list | grep -C 20 Spotify | grep bluez_sink.FC_A8_9A_B9_45_14 | awk '{ print $2 }'"
    # cmd = "pacmd list-sink-inputs | grep index | awk '{ print $2 }'"
    return commands.getoutput(cmd).decode(TERMINAL_ENCODING)


def start_recording(index, output_filename):
    import shlex
    global PAREC_PROCESS, LAME_PROCESS

    parec_cmd = 'parec --format=s16le --record --monitor-stream {index}'
    lame_cmd = 'lame -r -q 2 --lowpass 17 --abr 192 - "{output_filename}"'
    parec_cmd = parec_cmd.format(index=index).encode('utf-8')
    lame_cmd = lame_cmd.format(output_filename=output_filename).encode('utf-8')

    PAREC_PROCESS = subprocess.Popen(
        shlex.split(parec_cmd), stdout=subprocess.PIPE)
    LAME_PROCESS = subprocess.Popen(
        shlex.split(lame_cmd), stdin=PAREC_PROCESS.stdout)
    print('Recording at {}...'.format(output_filename))


def stop_recording():
    global PAREC_PROCESS, LAME_PROCESS

    if None not in (PAREC_PROCESS, LAME_PROCESS):
        print('Stop recording file...')

        import signal
        PAREC_PROCESS.send_signal(signal.SIGTERM)
        LAME_PROCESS.send_signal(signal.SIGTERM)
        PAREC_PROCESS = LAME_PROCESS = None


def mute():
    global MUTED
    MUTED = True
    index = get_pacmd_index()
    os.system(MUTE_COMMAND.format(index=index))


def unmute():
    global MUTED
    MUTED = False
    index = get_pacmd_index()
    os.system(UNMUTE_COMMAND.format(index=index))


def is_spotify_opened():
    global SPOTIFY_OPENED
    output = commands.getoutput(SPOTIFY_OPEN_COMMAND)
    output = output.decode(TERMINAL_ENCODING)
    SPOTIFY_OPENED = bool(int(output))  # 0 is closed
    return SPOTIFY_OPENED


def is_known_title(spotify_title):
    if spotify_title.isupper():
        # most of the ads are upper case
        return False

    if len(spotify_title.split()) == 1:
        # some of the ads are just one word
        return False

    # check for known Ads
    for title in ADS_TITLES:
        for t in title:
            if t in spotify_title:
                return False

    if len(spotify_title.split(' - ')) == 2:
        # most of the songs are in the form "Artist - Title"
        return True

    # check for known Artists or Songs
    for title in KNOWN_TITLES:
        for t in title:
            if t in spotify_title:
                return True
    return False


def check_spotify_ads():
    output = commands.getoutput(WMCTRL_WINDOW_LIST)
    try:
        output = output.decode(TERMINAL_ENCODING)
        _, spotify_title = output.split(HOSTNAME)
    except (ValueError, UnicodeDecodeError) as e:
        print('*** ERROR: {} ***'.format(e))
        print('*** Command Output: {} ***'.format(output))
        return

    spotify_title = spotify_title.strip()
    known_title = is_known_title(spotify_title)
    if (spotify_title not in SONGS_PLAYED and known_title) or (
            not MUTED and not known_title):  # and spotify_title != 'Spotify'):
        index = get_pacmd_index()

        try:
            output_path = None
            # FIXME: doesn't work with CD's with multiples artists
            # get output filename
            track = len(SONGS_PLAYED) + 1
            d = datetime.datetime.now().strftime('%Y-%m-%d_%H:%M:%S')
            print(spotify_title)
            artist, song = spotify_title.split(' - ')
            output_filename = '{} - {:03} - {}.mp3'.format(d, track, song)
            output_dir = os.path.join(DEFAULT_OUTPUT_DIR, artist)
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            output_path = os.path.join(output_dir, output_filename)
        except:
            stop_recording()

        stop_recording()
        if output_path:
            start_recording(index, output_path)
        print('Playing:', spotify_title)
    elif not known_title:
        stop_recording()

    if spotify_title not in SONGS_PLAYED and known_title:
        SONGS_PLAYED.append(spotify_title)

    if known_title:
        if MUTED:
            # the window title changes before the song starts
            time.sleep(SLEEP_BEFORE_UNMUTE)
            unmute()
    else:
        if not MUTED:
            stop_recording()
            print('Sound MUTED.')
            mute()


if __name__ == '__main__':
    try:
        while is_spotify_opened():
            check_spotify_ads()
            time.sleep(SLEEP_BETWEEN_EACH_CHECK)
    except KeyboardInterrupt:
        if MUTED:
            print('\nUnmuting...', end=' ')
            unmute()
        print('\nBye.')
        sys.exit(0)
