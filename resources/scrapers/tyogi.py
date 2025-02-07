'''
DeccanDelight scraper plugin
Copyright (C) 2016 gujal

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
import re

from bs4 import BeautifulSoup, SoupStrainer
from resources.lib import client
from resources.lib.base import Scraper
from six.moves import urllib_parse


class tyogi(Scraper):
    def __init__(self):
        Scraper.__init__(self)
        self.bu = 'https://tamilyogi.beer/home/'
        self.icon = self.ipath + 'tyogi.png'

    def get_menu(self):
        html = client.request(self.bu)
        items = {}
        cats = re.findall(r'''class="menu-item.+?href=['"]?([^'"\s]+)['"\s]*>([^<]+)''', html, re.DOTALL)
        sno = 1
        for cat, title in cats:
            cat = cat if cat.startswith('http') else self.bu[:-6] + cat
            items['%02d' % sno + title] = cat
            sno += 1
        items['%02d' % sno + '[COLOR yellow]** Search **[/COLOR]'] = self.bu[:-6] + '/?s='
        return (items, 7, self.icon)

    def get_items(self, url):
        movies = []
        if url[-3:] == '?s=':
            search_text = self.get_SearchQuery('Tamil Yogi')
            search_text = urllib_parse.quote_plus(search_text)
            url = url + search_text

        html = client.request(url)
        regex = r"<iframe\s*srcdoc.+?iframe>"
        html = re.sub(regex, '', html, 0, re.MULTILINE)
        mlink = SoupStrainer("div", {"id": "archive"})
        mdiv = BeautifulSoup(html, "html.parser", parse_only=mlink)
        plink = SoupStrainer("div", {"class": "navigation"})
        Paginator = BeautifulSoup(html, "html.parser", parse_only=plink)
        items = mdiv.find_all('li')
        for item in items:
            if '"cleaner"' not in str(item):
                title = self.unescape(item.text)
                title = self.clean_title(title)
                url = item.a.get('href')
                try:
                    thumb = item.img.get('src')
                except:
                    thumb = self.icon
                movies.append((title, thumb, url))

        if 'next' in str(Paginator):
            nextpg = Paginator.find('a', {'class': 'next'})
            purl = nextpg.get('href')
            currpg = Paginator.find('span', {'class': 'current'}).text
            pages = Paginator.find_all('a', {'class': 'page-numbers'})
            lastpg = pages[-2].text
            title = 'Next Page.. (Currently in Page %s of %s)' % (currpg, lastpg)
            movies.append((title, self.nicon, purl))

        return (movies, 9)

    def get_video(self, url):
        html = client.request(url, referer=self.bu)
        mlink = SoupStrainer('div', {'class': 'entry'})
        mdiv = BeautifulSoup(html, "html.parser", parse_only=mlink)
        eurl = mdiv.iframe.get('src')
        if self.hmf(eurl):
            return eurl

        self.log('{0} not resolvable {1}.\n'.format(url, eurl), 'info')
        return

# Iterate through items until the first result is found
    for item in items:
        if '"cleaner"' not in str(item):
            title = self.unescape(item.text)
            title = self.clean_title(title)
            url = item.a.get('href')

            # Append title and URL to movies list
            results.append((title, url))

            # Break the loop after processing the first item
            break

    return results
