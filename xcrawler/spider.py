"""
    spider
    ~~~~~~~~~~~~~~
    
    :copyright: (c) 2017 by 0xE8551CCB.
    :license: MIT, see LICENSE for more details.
"""

import logging
from .http.request import Request

__all__ = ['BaseSpider']

logger = logging.getLogger(__name__)


class BaseSpider(object):
    name = ''
    start_urls = []

    def __init__(self):
        pass

    def __repr__(self):
        return '<{} name="{}">'.format(self.__class__.__name__, self.name)

    def start_requests(self):
        for url in self.start_urls:
            yield self.make_request_from_url(url)

    def make_request_from_url(self, url):
        return Request(url, callback=self.parse)

    def parse(self, response):
        raise NotImplementedError
