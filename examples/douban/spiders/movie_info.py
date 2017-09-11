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
    start_urls = ['https://movie.douban.com/chart']

    def parse(self, response):
        # extract items from response
        # yield new requests
        # yield new items
        print(response.text)
