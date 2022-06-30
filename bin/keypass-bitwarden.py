#!/bin/env python

import json
import os
import subprocess
import sys

if not os.environ.get('BW_SESSION'):
    print('ERROR: BW_SESSION environment variable not set.')
    sys.exit(1)

keys = {
    '.ssh/id_github': '',
    '.ssh/id_gitlab': '',
    '.ssh/id_rtfdcom': '',
    '.ssh/id_rtfdorg': '',
}

if len(sys.argv) != 2:
    print('ERROR: text prompted argument not received.')
    sys.exit(1)

for k in keys.keys():
    # First argument is the name of the program and the second argument is the text prompted
    # /home/humitos/keypass-bitwarden.py "Enter passphrase for .ssh/id_rtfdcom:"
    if k in sys.argv[1]:
        key = keys.get(k)

output = subprocess.run(f'/usr/bin/bw get item {key}'.split(), capture_output=True).stdout
print(json.loads(output)['fields'][0]['value'])
