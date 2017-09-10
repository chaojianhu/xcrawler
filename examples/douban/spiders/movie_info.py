"""
    movie_info
    ~~~~~~~~~~~~~~
    
    :copyright: (c) 2017 by 0xE8551CCB.
    :license: MIT, see LICENSE for more details.
"""

from xcrawler import BaseSpider


class DoubanMovieSpider(BaseSpider):
    name = 'douban_movie'
    custom_settings = {}
    start_urls = ['https://movie.douban.com']

    def parse(self, response):
        print(response)
