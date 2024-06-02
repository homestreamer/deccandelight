'''
DeccanDelight scraper plugin
Copyright (C) 2019 gujal

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
import json
import re

from resources.lib import client
from resources.lib.base import Scraper


class ary(Scraper):
    def __init__(self):
        Scraper.__init__(self)
        self.bu = 'https://videos.arydigital.tv/'
        self.icon = self.ipath + 'ary.png'
        self.list = {'01Current Dramas': self.bu + 'popularplaylists',
                     '02Finished Dramas': self.bu + 'archiveplaylists',
                     '03Latest Videos': 'latestvideosMMMM7'}

    def get_menu(self):
        return (self.list, 5, self.icon)

    def get_second(self, iurl):
        """
        Get the list of shows.
        """
        shows = []
        html = client.request(iurl)
        mdiv = re.findall(r'application/json">([^<]+)', html)[-1]
        items = json.loads(mdiv).get('props').get('pageProps').get('data').get('videosData')
        if 'archiveplaylists' in iurl:
            items = items[-1].get('videos')
        else:
            items = items[0].get('videos')
        for item in items:
            title = self.unescape(item.get('name'))
            title = title.encode('utf8') if self.PY2 else title
            url = item.get('link')
            thumb = item.get('cover_url')
            shows.append((title, thumb, url))
        return (shows, 7)

    def get_items(self, iurl):
        movies = []
        """
        https://api.dailymotion.com/playlist/x7uqr9/videos?fields=title%2Cthumbnail_360_url%2Cid&page=1&limit=50
        params = {'fields': 'title,thumbnail_360_url,id', 'page': 1, 'limit': 50}
        """
        page = '1'
        if '#' in iurl:
            iurl, page = iurl.split('#')
        if iurl == 'latestvideos':
            plurl = 'https://api.dailymotion.com/user/arydigitalofficial/videos'
        else:
            plurl = 'https://api.dailymotion.com/playlist/{0}/videos'.format(iurl)
        params = {'fields': 'title,thumbnail_360_url,id', 'page': page, 'limit': 50}
        html = client.request(plurl, params=params)
        jd = json.loads(html)
        items = jd.get('list')

        for item in items:
            title = item.get('title')
            if '|' in title:
                title = title.split('|')
                if 'digital' in title[-1].lower():
                    _ = title.pop(-1)
                if iurl != 'latestvideos':
                    _ = title.pop(0)
                title = '-'.join(title)
            url = 'https://www.dailymotion.com/video/' + item.get('id')
            thumb = item.get('thumbnail_360_url')
            movies.append((title, thumb, url))

        np = False
        total = jd.get('total')
        if total is None:
            np = jd.get('has_more')
        else:
            np = jd.get('page') * jd.get('limit') < total
        if np:
            purl = '{0}#{1}'.format(iurl, int(page) + 1)
            title = 'Next Page...'
            movies.append((title, self.nicon, purl))

        return (movies, 9)
