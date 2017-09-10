"""
    test_downloaders
    ~~~~~~~~~~~~~~
    
    :copyright: (c) 2017 by 0xE8551CCB.
    :license: MIT, see LICENSE for more details.
"""

import pytest
from xcrawler.http import Request, Response
from xcrawler.downloaders import BaseDownloader
from xcrawler.errors import HTTPStatusError, HTTPTimeoutError, HTTPConnectionError


class FooSpider:
    name = 'foo'


spider = FooSpider()


def test_base_downloader(monkeypatch):
    def download(self, reqs):
        for req in reqs:
            yield self.send_request(req)

    monkeypatch.setattr(BaseDownloader, 'download', download)

    req = Request('http://www.baidu.com', spider)
    result = BaseDownloader().send_request(req)
    assert result[0].status == 200
    assert result[-1] is None

    req = Request('http://example.chriscabin.com', spider)
    result = BaseDownloader().send_request(req)
    assert result[0] == req
    assert isinstance(result[-1], HTTPConnectionError)

    req = Request('http://www.chriscabin.com', spider)
    result = BaseDownloader(download_timeout=0.001).send_request(req)
    assert result[0] == req
    assert isinstance(result[-1], HTTPTimeoutError)

    req = Request('http://blog.chriscabin.com/no/such/page', spider)
    result = BaseDownloader().send_request(req)
    assert result[0].status == 404
    assert isinstance(result[-1], HTTPStatusError)
