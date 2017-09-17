"""
    test_spider
    ~~~~~~~~~~~~~~
    
    :copyright: (c) 2017 by 0xE8551CCB.
    :license: MIT, see LICENSE for more details.
"""

from xcrawler.spider import BaseSpider, Request


class MovieSpider(BaseSpider):
    name = 'movie'
    start_urls = [
        'http://movie.foo.com?page=1',
        'http://movie.foo.com?page=2',
    ]

    def parse(self, response):
        return response

    def on_engine_idle(self, engine):
        return 'engine is idle'


def test_spider():
    spider = MovieSpider()

    assert str(spider) == 'spider:movie'
    assert repr(spider) == '<MovieSpider name="movie">'

    requests = list(spider.start_requests())
    assert len(requests) == 2

    req1, req2 = requests
    assert req1.url == 'http://movie.foo.com?page=1'
    assert req1.spider is spider

    assert req2.url == 'http://movie.foo.com?page=2'

    assert spider.parse('Response') == 'Response'
    assert spider.on_engine_idle(None) == 'engine is idle'
