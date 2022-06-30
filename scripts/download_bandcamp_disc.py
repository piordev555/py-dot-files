import os
import re
import bs4
import sys
import json
import urllib
import urlparse
import requests

URL = sys.argv[1]

session = requests.session()
response = session.get(URL)
soup = bs4.BeautifulSoup(response.text)

table = soup.find('table', {'id': 'track_table'})
links = table.find_all('a', {'itemprop': 'url'})

tracks = []
for i, l in enumerate(links):
    title = l.text.encode('utf-8')
    url = urlparse.urljoin(URL, l.attrs['href'])
    number = i + 1

    filename = '{0:02d} - {1}.mp3'.format(number, title)
    if os.path.exists(filename):
        print('Skipping "{0}". It\'s already downloaded.'.format(filename))
        continue

    response = session.get(url)
    soup = bs4.BeautifulSoup(response.text)
    script = soup.find_all('script')[8]
    text_value = re.search('(trackinfo.*)', script.text).groups()[0][:-1]
    # http://stackoverflow.com/questions/13298201/parsing-variable-data-out-of-a-javascript-tag-using-python
    json_value = '{%s}' % (text_value.split('{', 1)[1].rsplit('}', 1)[0],)
    value = json.loads(json_value)
    download_url = value['file']['mp3-128']

    tracks.append({
        'number': number,
        'title': title,
        'url': url,
        'download-url': download_url,
    })

    print('Downloading: {0}'.format(title))
    print('Link: {0}'.format(download_url))
    urllib.urlretrieve(download_url, filename)
    # TODO: add ID3 to the files
