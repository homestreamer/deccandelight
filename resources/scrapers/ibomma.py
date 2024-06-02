'''
DeccanDelight scraper plugin
Copyright (C) 2022 gujal

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.
'''
import base64
import json
import re

from bs4 import BeautifulSoup, SoupStrainer
from resources.lib import client
from resources.lib.base import Scraper
from six.moves import urllib_parse


class ibomma(Scraper):
    def __init__(self):
        Scraper.__init__(self)
        self.bu = 'https://kev.ibomma.observer/'
        self.icon = self.ipath + 'ibomma.png'
        self.list = {
            # '01Tamil Movies': self.bu + 'tamil-movies/',
            '02Telugu Movies': self.bu + 'telugu-movies/',
            # '03Malayalam Movies': self.bu + 'malayalam-movies/',
            # '04Kannada Movies': self.bu + 'kannada-movies/',
            # '05Hindi Movies': self.bu + 'hindi-movies/',
            '99[COLOR yellow]** Search **[/COLOR]': 'https://search-v2.ibomma.support/?label=telugu&q='
        }

    def get_menu(self):
        return (self.list, 7, self.icon)

    def get_items(self, url):
        movies = []

        if url[-3:] == '&q=':
            search_text = self.get_SearchQuery('iBomma')
            search_text = urllib_parse.quote_plus(search_text)
            url = url + search_text

        html = client.request(url)
        mlink = SoupStrainer('article')
        items = BeautifulSoup(html, "html.parser", parse_only=mlink)
        if len(items) > 1:
            for item in items:
                title = item.h2.a.text
                title = title.encode('utf8') if self.PY2 else title
                title += ' [COLOR yellow]({0})[/COLOR]'.format(item.h2.span.text)
                thumb = item.img.get('data-src')
                url = item.a.get('href')
                movies.append((title, thumb, url))
        else:
            items = re.findall(r'(?:data={},\s*)?data=\s*(.+?)</script>', html)[0]
            items = json.loads(items)
            items = items.get('hits', {}).get('hits', [])
            for item in items:
                item = item.get('_source')
                desc = item.get('description')
                title = item.get('title').split('Telugu')[0].strip()
                title = title.encode('utf8') if self.PY2 else title
                r = re.search(r'\d{4}', desc)
                if r:
                    title += ' [COLOR yellow][{0}][/COLOR]'.format(r.group(0))
                thumb = item.get('image_link')
                url = item.get('location')
                movies.append((title, thumb, url))

        return (movies, 8)

    def get_videos(self, url):
        videos = []
        html = client.request(url)

        try:
            mlink = SoupStrainer('button', {'class': 'server-button'})
            items = BeautifulSoup(html, "html.parser", parse_only=mlink)
            urldiv = re.findall(r'const\s*urls\s*=\s*([^]]+])', html)[0]
            urls = re.findall(r"(http[^']+)", urldiv)
            for item in items:
                linkcode = int(item.get('data-index')) - 1
                ref, vurl = urls[linkcode].split('link=')
                ref = urllib_parse.urljoin(ref, '/')
                vurl = base64.b64decode(vurl).decode('utf-8')
                vidhost = self.get_vidhost(vurl)
                videos.append((vidhost, vurl + '|Referer={0}&verifypeer=false'.format(ref)))
        except:
            pass

        try:
            r = re.search(r"frame\.src\s*=\s*'([^']+)", html)
            if r:
                r = r.group(1)
                ref = urllib_parse.urljoin(r, '/')
                ehtml = client.request(r, referer=self.bu)
                s = re.search(r'file:"([^"]+)', ehtml)
                if s:
                    s = s.group(1)
                    vidhost = self.get_vidhost(s)
                    videos.append((vidhost, s + '|Referer={0}&Origin={1}&verifypeer=false'.format(ref, ref[:-1])))
        except:
            pass

        return videos
