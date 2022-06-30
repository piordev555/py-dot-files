#!/usr/bin/env python

import os
import sys
import glob
import urllib

from BeautifulSoup import BeautifulSoup


URL = sys.argv[1]
FILENAME_TEMPLATE = '{title}: {season} - {n:02} - {chapter}'
NO_TITLE_FILENAME_TEMPLATE = '{season} - {n:02} - {chapter}'


def get_filename(chapter):
    try:
        return glob.glob(u'*{}*'.format(chapter))[0]
    except IndexError:
        return None


if __name__ == '__main__':

    html = urllib.urlopen(URL).read()
    soup = BeautifulSoup(html)

    title = soup.find('h1', attrs={u'id': 'programa'}).text

    for ul in soup.findAll(u'ul', attrs={u'id': u'listaEpisodios'}):
        season = ul.h2.text
        for n, li in enumerate(ul.findAll(u'li')):
            chapter = li.h3.text
            filename = get_filename(chapter)
            if filename is not None:
                if title == season:
                    # avoid title
                    template = NO_TITLE_FILENAME_TEMPLATE
                else:
                    template = FILENAME_TEMPLATE

                new_filename = template\
                    .format(**{
                        'title': title,
                        'season': season,
                        'n': n,
                        'chapter': chapter,
                    })
                print new_filename
