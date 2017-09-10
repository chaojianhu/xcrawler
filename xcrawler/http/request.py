"""
    request
    ~~~~~~~~~~~~~~
    
    :copyright: (c) 2017 by 0xE8551CCB.
    :license: MIT, see LICENSE for more details.
"""

from ..helpers import safe_url

__all__ = ['Request']


class Request(object):
    def __init__(self, url, spider, method='GET', data=None, headers=None,
                 cookies=None, proxy=None, callback=None, meta=None,
                 dont_filter=False, priority=0):
        self.url = safe_url(url)
        self.spider = spider
        self.method = method.upper()
        self.data = data
        self.headers = headers
        self.cookies = cookies
        self.proxy = proxy
        self.callback = callback
        self.meta = meta
        self.dont_filter = dont_filter
        self.priority = priority
        self.retry_count = 0

    def __repr__(self):
        return '<[{}]Request {} {!r}>'.format(self.spider.name,
                                              self.method.upper(), self.url)
