import mechanize

import os
import re
import urllib2

from PIL import Image
from BeautifulSoup import BeautifulSoup

url = 'http://sms2.personal.com.ar/Mensajes/sms.php'

br = mechanize.Browser()
br.open(url)
br.select_form(name='messageForm')
soup = BeautifulSoup(br.response().get_data())
img = soup.find('img', attrs={'src': re.compile('http://sms2.personal.com.ar/Mensajes/.*png')})
src = img.get('src')
fpimg = urllib2.urlopen(src)
pil_image = Image.open(fpimg.read())
pil_image.show()
import ipdb;ipdb.set_trace()
br.submit()

while True:
    soup = BeautifulSoup(urllib2.urlopen(url))

    # soup.find('input', attrs={'name': 'Filename'})
    img = soup.find('img', attrs={'src': re.compile('http://sms2.personal.com.ar/Mensajes/.*png')})
    if img:
        src = img.get('src')
        outputpath = 'downloads/' + src.split('/')[-1]
        if not os.path.exists(outputpath):
            print 'Downloading:', src, '...',
            fpimg = urllib2.urlopen(src)
            r = fpimg.read()
            fpout = open(outputpath, 'w')
            fpout.write(r)
            fpout.close()
            print '   [DONE]'
