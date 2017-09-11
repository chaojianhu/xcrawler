"""
    response
    ~~~~~~~~~~~~~~
    
    :copyright: (c) 2017 by 0xE8551CCB.
    :license: MIT, see LICENSE for more details.
"""

from urllib.parse import urljoin

from ..helpers import base_url

__all__ = ['Response']


class Response(object):
    def __init__(self, url, status, content, encoding, request,
                 cookies=None, headers=None, reason=''):
        self.request = request
        self.url = url
        self.base_url = base_url(url)
        self.cookies = cookies
        self.headers = headers or {}
        self.status = status
        self.content = content
        self.encoding = encoding
        self.meta = request.meta
        self.callback = request.callback
        self.reason = reason

    @property
    def text(self):
        return self.content.decode(self.encoding)

    def decode_content(self, encoding='utf-8'):
        return self.content.decode(encoding)

    def urljoin(self, url):
        return urljoin(self.base_url, url)

    def __repr__(self):
        return '<[{}]Response {!r}: {}>'.format(self.request.spider.name,
                                                self.url, self.status)
